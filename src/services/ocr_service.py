"""
Serviço OCR para processamento de exames médicos com Tesseract.
"""

import pytesseract
from PIL import Image
import pdf2image
import hashlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional
import tempfile
import os

from src.core.config import get_settings_lazy
from src.core.logging import api_logger


class OCRService:
    """Serviço OCR com Tesseract para processamento determinístico."""
    
    def __init__(self):
        # Configuração determinística do Tesseract
        self.tesseract_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:;()[]{}%+-=<>/\\|&*^$#@!?'
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Configura Tesseract se especificado
        config = get_settings_lazy()
        if hasattr(config, 'tesseract_cmd') and config.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd
    
    async def process_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Processa arquivo com OCR determinístico.
        
        Args:
            file_path: Caminho para o arquivo
            file_type: Tipo MIME do arquivo
            
        Returns:
            Dict com resultado do OCR
        """
        try:
            # Extrai texto baseado no tipo
            if file_type == "application/pdf":
                text = await self._process_pdf(file_path)
            elif file_type in ["image/png", "image/jpeg", "image/jpg"]:
                text = await self._process_image(file_path)
            elif file_type == "text/plain":
                text = await self._read_text_file(file_path)
            else:
                raise ValueError(f"Tipo de arquivo não suportado para OCR: {file_type}")
            
            # Calcula hash para determinismo
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            
            # Calcula confiança baseada na qualidade do texto
            confidence = self._calculate_confidence(text)
            
            # Log da operação
            api_logger.log_operation(
                operation="ocr_processing",
                details={
                    "file_type": file_type,
                    "text_length": len(text),
                    "confidence": confidence,
                    "text_hash": text_hash
                }
            )
            
            return {
                "success": True,
                "ocr_text": text,
                "text_hash": text_hash,
                "confidence": confidence,
                "file_type": file_type,
                "text_length": len(text)
            }
            
        except Exception as e:
            api_logger.log_error(
                error=str(e),
                operation="ocr_processing",
                details={"file_path": file_path, "file_type": file_type}
            )
            return {"success": False, "error": str(e)}
    
    async def _process_pdf(self, file_path: str) -> str:
        """
        Processa PDF com pdf2image + Tesseract.
        
        Args:
            file_path: Caminho para o PDF
            
        Returns:
            Texto extraído de todas as páginas
        """
        try:
            # Converte PDF para imagens
            images = pdf2image.convert_from_path(
                file_path, 
                dpi=300,  # DPI alto para melhor qualidade
                fmt='PNG'  # Formato consistente
            )
            
            # Processa cada página
            texts = []
            for i, image in enumerate(images):
                text = await self._extract_text_from_image(image)
                texts.append(f"--- Página {i+1} ---\n{text}")
            
            return "\n\n".join(texts)
            
        except Exception as e:
            raise Exception(f"Erro ao processar PDF: {str(e)}")
    
    async def _process_image(self, file_path: str) -> str:
        """
        Processa imagem com Tesseract.
        
        Args:
            file_path: Caminho para a imagem
            
        Returns:
            Texto extraído da imagem
        """
        try:
            image = Image.open(file_path)
            text = await self._extract_text_from_image(image)
            return text
            
        except Exception as e:
            raise Exception(f"Erro ao processar imagem: {str(e)}")
    
    async def _extract_text_from_image(self, image: Image.Image) -> str:
        """
        Extrai texto de imagem com configuração determinística.
        
        Args:
            image: Imagem PIL
            
        Returns:
            Texto extraído
        """
        try:
            # Executa OCR em thread separada para não bloquear
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                self.executor,
                lambda: pytesseract.image_to_string(
                    image, 
                    config=self.tesseract_config,
                    lang=config.tesseract_lang if hasattr(config, 'tesseract_lang') else 'por+eng'
                )
            )
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Erro no OCR: {str(e)}")
    
    def _calculate_confidence(self, text: str) -> float:
        """
        Calcula confiança baseada na qualidade do texto extraído.
        
        Args:
            text: Texto extraído
            
        Returns:
            Score de confiança (0-100)
        """
        if not text:
            return 0.0
        
        # Métricas de qualidade
        total_chars = len(text)
        alphanumeric_chars = sum(1 for c in text if c.isalnum())
        space_chars = text.count(' ')
        question_marks = text.count('?')
        
        # Fórmula de confiança ponderada
        confidence = (
            (alphanumeric_chars / total_chars) * 0.6 +      # Caracteres alfanuméricos
            (space_chars / total_chars) * 0.2 +             # Espaços
            (1 - (question_marks / total_chars)) * 0.2      # Menos interrogações
        )
        
        return min(max(confidence * 100, 0.0), 100.0)
    
    async def _read_text_file(self, file_path: str) -> str:
        """
        Lê arquivo de texto diretamente.
        
        Args:
            file_path: Caminho para o arquivo de texto
            
        Returns:
            Conteúdo do arquivo
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo de texto: {str(e)}")
    
    async def process_file_from_bytes(self, file_content: bytes, file_type: str, file_name: str) -> Dict[str, Any]:
        """
        Processa arquivo a partir de bytes (para uploads diretos).
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            file_type: Tipo MIME do arquivo
            file_name: Nome do arquivo
            
        Returns:
            Dict com resultado do OCR
        """
        try:
            # Cria arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix=self._get_file_extension(file_name)) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Processa o arquivo temporário
                result = await self.process_file(temp_file_path, file_type)
                return result
            finally:
                # Remove arquivo temporário
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_file_extension(self, file_name: str) -> str:
        """
        Obtém extensão do arquivo.
        
        Args:
            file_name: Nome do arquivo
            
        Returns:
            Extensão com ponto
        """
        if '.' in file_name:
            return '.' + file_name.split('.')[-1]
        return ''
    
    async def get_ocr_languages(self) -> Dict[str, Any]:
        """
        Obtém idiomas disponíveis no Tesseract.
        
        Returns:
            Dict com idiomas disponíveis
        """
        try:
            loop = asyncio.get_event_loop()
            languages = await loop.run_in_executor(
                self.executor,
                pytesseract.get_languages
            )
            
            return {
                "success": True,
                "languages": languages,
                "current_language": getattr(config, 'tesseract_lang', 'por+eng')
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cleanup(self):
        """Limpa recursos do executor."""
        if self.executor:
            self.executor.shutdown(wait=True)
