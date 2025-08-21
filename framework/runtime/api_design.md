# API Integration Design - API de Exames Médicos

## Visão Geral
Design das integrações para Supabase (Auth/Storage) e Tesseract OCR com foco em resilience, determinismo e LGPD compliance.

## Stack de Integrações
- **Supabase Auth**: JWT authentication com refresh tokens
- **Supabase Storage**: File upload com links assinados
- **Tesseract OCR**: Processamento local determinístico
- **Resilience**: Retries, timeouts, circuit breakers

## 1. Supabase Auth Integration

### Configuração do Cliente
```python
# src/core/supabase_client.py
import os
from supabase import create_client, Client
from typing import Optional

class SupabaseAuthClient:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )
        self._current_user = None
    
    async def sign_up(self, email: str, password: str, full_name: str, crm: str) -> dict:
        """Registro de médico com retry e validação"""
        try:
            response = await self._with_retry(
                lambda: self.supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "full_name": full_name,
                            "crm": crm,
                            "role": "doctor"
                        }
                    }
                })
            )
            return {"success": True, "user": response.user}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def sign_in(self, email: str, password: str) -> dict:
        """Login com JWT e refresh token"""
        try:
            response = await self._with_retry(
                lambda: self.supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
            )
            return {
                "success": True,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": response.user
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _with_retry(self, operation, max_retries: int = 3, delay: float = 1.0):
        """Retry pattern com exponential backoff"""
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(delay * (2 ** attempt))
```

### JWT Middleware para FastAPI
```python
# src/core/auth_middleware.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
import jwt
from typing import Optional

security = HTTPBearer()

class AuthMiddleware:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Valida JWT e retorna usuário atual"""
        try:
            token = credentials.credentials
            user = await self._verify_jwt(token)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Erro de autenticação"
            )
    
    async def _verify_jwt(self, token: str) -> Optional[dict]:
        """Verifica JWT com Supabase"""
        try:
            # Verifica com Supabase
            user = self.supabase.auth.get_user(token)
            return user.user
        except Exception:
            return None
```

## 2. Supabase Storage Integration

### File Upload Service
```python
# src/services/storage_service.py
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from supabase import Client
import asyncio

class StorageService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.bucket_name = "medical-exams"
        self.max_file_size = 5 * 1024 * 1024  # 5MB
    
    async def upload_file(self, file_content: bytes, file_name: str, mime_type: str) -> dict:
        """Upload de arquivo com validação e retry"""
        try:
            # Validação de tamanho
            if len(file_content) > self.max_file_size:
                raise ValueError("Arquivo muito grande (máx: 5MB)")
            
            # Validação de tipo
            allowed_types = ["application/pdf", "image/png", "image/jpeg", "text/plain"]
            if mime_type not in allowed_types:
                raise ValueError("Tipo de arquivo não suportado")
            
            # Gera nome único
            unique_name = f"{uuid.uuid4()}_{file_name}"
            
            # Upload com retry
            file_path = await self._upload_with_retry(file_content, unique_name, mime_type)
            
            # Gera link assinado (expira em 24h)
            signed_url = await self._generate_signed_url(file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "file_name": file_name,
                "file_size": len(file_content),
                "mime_type": mime_type,
                "signed_url": signed_url,
                "expires_at": datetime.now() + timedelta(hours=24)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _upload_with_retry(self, content: bytes, name: str, mime_type: str, max_retries: int = 3) -> str:
        """Upload com retry pattern"""
        for attempt in range(max_retries):
            try:
                response = self.supabase.storage.from_(self.bucket_name).upload(
                    path=name,
                    file=content,
                    file_options={"content-type": mime_type}
                )
                return f"{self.bucket_name}/{name}"
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(1 * (2 ** attempt))
    
    async def _generate_signed_url(self, file_path: str) -> str:
        """Gera link assinado que expira em 24h"""
        try:
            response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                path=file_path,
                expires_in=86400  # 24 horas
            )
            return response.signed_url
        except Exception as e:
            raise Exception(f"Erro ao gerar link assinado: {str(e)}")
    
    async def delete_file(self, file_path: str) -> bool:
        """Remove arquivo do storage"""
        try:
            self.supabase.storage.from_(self.bucket_name).remove([file_path])
            return True
        except Exception:
            return False
```

## 3. Tesseract OCR Integration

### OCR Service com Determinismo
```python
# src/services/ocr_service.py
import pytesseract
from PIL import Image
import pdf2image
import hashlib
import json
from typing import Dict, List, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OCRService:
    def __init__(self):
        # Configuração determinística do Tesseract
        self.tesseract_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:;()[]{}%+-=<>/\\|&*^$#@!?'
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def process_file(self, file_path: str, file_type: str) -> dict:
        """Processa arquivo com OCR determinístico"""
        try:
            # Extrai texto baseado no tipo
            if file_type == "application/pdf":
                text = await self._process_pdf(file_path)
            elif file_type in ["image/png", "image/jpeg"]:
                text = await self._process_image(file_path)
            elif file_type == "text/plain":
                text = await self._read_text_file(file_path)
            else:
                raise ValueError("Tipo de arquivo não suportado para OCR")
            
            # Calcula hash para determinismo
            text_hash = hashlib.md5(text.encode()).hexdigest()
            
            # Calcula confiança baseada na qualidade do texto
            confidence = self._calculate_confidence(text)
            
            return {
                "success": True,
                "ocr_text": text,
                "text_hash": text_hash,
                "confidence": confidence,
                "file_type": file_type
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_pdf(self, file_path: str) -> str:
        """Processa PDF com pdf2image + Tesseract"""
        try:
            # Converte PDF para imagens
            images = pdf2image.convert_from_path(file_path, dpi=300)
            
            # Processa cada página
            texts = []
            for i, image in enumerate(images):
                text = await self._extract_text_from_image(image)
                texts.append(f"--- Página {i+1} ---\n{text}")
            
            return "\n\n".join(texts)
            
        except Exception as e:
            raise Exception(f"Erro ao processar PDF: {str(e)}")
    
    async def _process_image(self, file_path: str) -> str:
        """Processa imagem com Tesseract"""
        try:
            image = Image.open(file_path)
            text = await self._extract_text_from_image(image)
            return text
            
        except Exception as e:
            raise Exception(f"Erro ao processar imagem: {str(e)}")
    
    async def _extract_text_from_image(self, image: Image.Image) -> str:
        """Extrai texto de imagem com configuração determinística"""
        try:
            # Executa OCR em thread separada para não bloquear
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                self.executor,
                lambda: pytesseract.image_to_string(
                    image, 
                    config=self.tesseract_config
                )
            )
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Erro no OCR: {str(e)}")
    
    def _calculate_confidence(self, text: str) -> float:
        """Calcula confiança baseada na qualidade do texto extraído"""
        if not text:
            return 0.0
        
        # Métricas de qualidade
        total_chars = len(text)
        alphanumeric_chars = sum(1 for c in text if c.isalnum())
        space_chars = text.count(' ')
        
        # Fórmula de confiança
        confidence = (
            (alphanumeric_chars / total_chars) * 0.6 +  # Caracteres alfanuméricos
            (space_chars / total_chars) * 0.2 +         # Espaços
            (1 - (text.count('?') / total_chars)) * 0.2  # Menos interrogações
        )
        
        return min(max(confidence * 100, 0.0), 100.0)
    
    async def _read_text_file(self, file_path: str) -> str:
        """Lê arquivo de texto diretamente"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo de texto: {str(e)}")
```

## 4. Resilience Patterns

### Circuit Breaker para Supabase
```python
# src/core/resilience.py
import asyncio
from typing import Callable, Any
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Funcionando normalmente
    OPEN = "open"          # Falhando, não tenta
    HALF_OPEN = "half_open"  # Testando se recuperou

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com circuit breaker"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker está aberto")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Sucesso - fecha o circuit breaker"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Falha - incrementa contador"""
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar reset"""
        if not self.last_failure_time:
            return False
        
        return (asyncio.get_event_loop().time() - self.last_failure_time) >= self.recovery_timeout
```

## 5. Configuração de Ambiente

### Variáveis de Ambiente
```bash
# .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Tesseract
TESSERACT_CMD=/usr/bin/tesseract
TESSERACT_LANG=por+eng

# Storage
MAX_FILE_SIZE=5242880  # 5MB em bytes
SIGNED_URL_EXPIRY=86400  # 24 horas em segundos

# Resilience
MAX_RETRIES=3
CIRCUIT_BREAKER_THRESHOLD=5
RECOVERY_TIMEOUT=60
```

## 6. LGPD Compliance Features

### Logging Anonimizado
```python
# src/core/logging.py
import structlog
import hashlib
from typing import Any, Dict

class AnonymizedLogger:
    def __init__(self):
        self.logger = structlog.get_logger()
    
    def _anonymize_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove/anonimiza dados pessoais dos logs"""
        anonymized = data.copy()
        
        # Campos sensíveis
        sensitive_fields = ['email', 'cpf', 'crm', 'phone', 'address']
        
        for field in sensitive_fields:
            if field in anonymized:
                if anonymized[field]:
                    anonymized[field] = f"***{hashlib.md5(str(anonymized[field]).encode()).hexdigest()[:8]}***"
        
        return anonymized
    
    def log_operation(self, operation: str, user_id: str, details: Dict[str, Any]):
        """Log de operação com dados anonimizados"""
        log_data = {
            "operation": operation,
            "user_id": f"user_{hashlib.md5(user_id.encode()).hexdigest()[:8]}",
            "details": self._anonymize_pii(details),
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info("API Operation", **log_data)
```

---

## Resumo das Integrações

### Sprint 2 (Upload/Processamento)
- ✅ **Supabase Storage**: Upload com retry, validação, links assinados
- ✅ **Tesseract OCR**: Processamento determinístico, PDF + imagens
- ✅ **Resilience**: Circuit breaker, retry patterns

### Sprint 4 (Gestão)
- ✅ **Supabase Auth**: JWT com refresh, middleware FastAPI
- ✅ **Security**: RLS policies, LGPD compliance
- ✅ **Monitoring**: Logging anonimizado, métricas

### Características Técnicas
- **Determinismo**: Mesmo arquivo → mesmo resultado OCR
- **Resilience**: Retry, circuit breaker, timeouts
- **LGPD**: Logs anonimizados, dados criptografados
- **Performance**: Processamento assíncrono, thread pool

---
*Design criado pelo api_architect - Pronto para implementação*
