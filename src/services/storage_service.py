"""
Serviço de storage para upload de arquivos no Supabase.
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from supabase import Client
import asyncio
import mimetypes

from src.core.config import get_settings_lazy
from src.core.logging import api_logger


class StorageService:
    """Serviço para gerenciar uploads no Supabase Storage."""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.bucket_name = "medical-exams"
        config = get_settings_lazy()
        self.max_file_size = config.max_file_size
        self.signed_url_expiry = config.signed_url_expiry
    
    async def upload_file(self, file_content: bytes, file_name: str, mime_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload de arquivo com validação e retry.
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            file_name: Nome original do arquivo
            mime_type: Tipo MIME (inferido automaticamente se None)
            
        Returns:
            Dict com resultado da operação
        """
        try:
            # Validação de tamanho
            if len(file_content) > self.max_file_size:
                raise ValueError(f"Arquivo muito grande (máx: {self.max_file_size / (1024*1024):.1f}MB)")
            
            # Inferir MIME type se não fornecido
            if not mime_type:
                mime_type = self._infer_mime_type(file_name)
            
            # Validação de tipo
            if not self._is_allowed_file_type(mime_type):
                raise ValueError(f"Tipo de arquivo não suportado: {mime_type}")
            
            # Gera nome único para evitar conflitos
            unique_name = self._generate_unique_filename(file_name)
            
            # Upload com retry
            file_path = await self._upload_with_retry(file_content, unique_name, mime_type)
            
            # Gera link assinado
            signed_url = await self._generate_signed_url(file_path)
            
            # Log da operação
            api_logger.log_operation(
                operation="file_upload",
                details={
                    "file_name": file_name,
                    "file_size": len(file_content),
                    "mime_type": mime_type,
                    "file_path": file_path
                }
            )
            
            return {
                "success": True,
                "file_path": file_path,
                "file_name": file_name,
                "file_size": len(file_content),
                "mime_type": mime_type,
                "signed_url": signed_url,
                "expires_at": datetime.now() + timedelta(seconds=self.signed_url_expiry)
            }
            
        except Exception as e:
            api_logger.log_error(
                error=str(e),
                operation="file_upload",
                details={"file_name": file_name, "file_size": len(file_content)}
            )
            return {"success": False, "error": str(e)}
    
    async def _upload_with_retry(self, content: bytes, name: str, mime_type: str, max_retries: int = None) -> str:
        """
        Upload com retry pattern.
        
        Args:
            content: Conteúdo do arquivo
            name: Nome do arquivo
            mime_type: Tipo MIME
            max_retries: Número máximo de tentativas
            
        Returns:
            Caminho do arquivo no storage
            
        Raises:
            Exception: Se todas as tentativas falharem
        """
        if max_retries is None:
            config = get_settings_lazy()
        max_retries = config.max_retries
            
        for attempt in range(max_retries):
            try:
                response = self.supabase.get_storage(self.bucket_name).upload(
                    path=name,
                    file=content,
                    file_options={"content-type": mime_type}
                )
                
                # Verifica se o upload foi bem-sucedido
                if response and hasattr(response, 'path'):
                    return f"{self.bucket_name}/{response.path}"
                else:
                    return f"{self.bucket_name}/{name}"
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                # Exponential backoff
                delay = 1 * (2 ** attempt)
                await asyncio.sleep(delay)
    
    async def _generate_signed_url(self, file_path: str) -> str:
        """
        Gera link assinado que expira em 24h.
        
        Args:
            file_path: Caminho do arquivo no storage
            
        Returns:
            URL assinada para download
        """
        try:
            response = self.supabase.get_storage(self.bucket_name).create_signed_url(
                path=file_path.replace(f"{self.bucket_name}/", ""),
                expires_in=self.signed_url_expiry
            )
            return response.signed_url
        except Exception as e:
            raise Exception(f"Erro ao gerar link assinado: {str(e)}")
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Remove arquivo do storage.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se removido com sucesso
        """
        try:
            # Remove o prefixo do bucket se presente
            if file_path.startswith(f"{self.bucket_name}/"):
                file_path = file_path.replace(f"{self.bucket_name}/", "")
            
            self.supabase.get_storage(self.bucket_name).remove([file_path])
            
            api_logger.log_operation(
                operation="file_deletion",
                details={"file_path": file_path}
            )
            
            return True
        except Exception as e:
            api_logger.log_error(
                error=str(e),
                operation="file_deletion",
                details={"file_path": file_path}
            )
            return False
    
    def _infer_mime_type(self, file_name: str) -> str:
        """
        Infere o tipo MIME baseado na extensão do arquivo.
        
        Args:
            file_name: Nome do arquivo
            
        Returns:
            Tipo MIME inferido
        """
        mime_type, _ = mimetypes.guess_type(file_name)
        
        if mime_type:
            return mime_type
        
        # Fallback para extensões comuns
        extension = file_name.lower().split('.')[-1] if '.' in file_name else ''
        
        mime_map = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'txt': 'text/plain'
        }
        
        return mime_map.get(extension, 'application/octet-stream')
    
    def _is_allowed_file_type(self, mime_type: str) -> bool:
        """
        Verifica se o tipo de arquivo é permitido.
        
        Args:
            mime_type: Tipo MIME do arquivo
            
        Returns:
            True se permitido
        """
        allowed_types = [
            "application/pdf",
            "image/png",
            "image/jpeg",
            "text/plain"
        ]
        
        return mime_type in allowed_types
    
    def _generate_unique_filename(self, original_name: str) -> str:
        """
        Gera nome único para o arquivo.
        
        Args:
            original_name: Nome original do arquivo
            
        Returns:
            Nome único gerado
        """
        # Extrai extensão
        name_parts = original_name.rsplit('.', 1)
        base_name = name_parts[0] if len(name_parts) > 1 else original_name
        extension = f".{name_parts[1]}" if len(name_parts) > 1 else ""
        
        # Gera UUID único
        unique_id = str(uuid.uuid4())
        
        # Combina: base_name_uuid.extension
        return f"{base_name}_{unique_id}{extension}"
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações do arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dict com informações ou None se não encontrado
        """
        try:
            # Remove o prefixo do bucket se presente
            if file_path.startswith(f"{self.bucket_name}/"):
                file_path = file_path.replace(f"{self.bucket_name}/", "")
            
            # Lista arquivos para obter informações
            files = self.supabase.get_storage(self.bucket_name).list(path="")
            
            for file_info in files:
                if file_info.name == file_path:
                    return {
                        "name": file_info.name,
                        "size": getattr(file_info, 'metadata', {}).get('size', 0),
                        "mime_type": getattr(file_info, 'metadata', {}).get('mimetype', ''),
                        "created_at": getattr(file_info, 'created_at', None)
                    }
            
            return None
            
        except Exception as e:
            api_logger.log_error(
                error=str(e),
                operation="get_file_info",
                details={"file_path": file_path}
            )
            return None
