"""
Testes para o serviço OCR.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from PIL import Image
import tempfile
import os

from src.services.ocr_service import OCRService


class TestOCRService:
    """Testes para OCRService."""
    
    @pytest.fixture
    def ocr_service(self):
        """Instância do OCRService."""
        return OCRService()
    
    @pytest.fixture
    def sample_image(self):
        """Imagem de teste."""
        # Cria uma imagem simples para teste
        img = Image.new('RGB', (100, 100), color='white')
        return img
    
    @pytest.mark.asyncio
    async def test_process_file_from_bytes_success(self, ocr_service):
        """Testa processamento de arquivo a partir de bytes."""
        # Arrange
        file_content = b"test content"
        file_type = "text/plain"
        file_name = "test.txt"
        
        # Mock do processamento de arquivo
        with patch.object(ocr_service, 'process_file') as mock_process:
            mock_process.return_value = {
                "success": True,
                "ocr_text": "Texto extraído",
                "confidence": 85.5
            }
            
            # Act
            result = await ocr_service.process_file_from_bytes(file_content, file_type, file_name)
            
            # Assert
            assert result["success"] is True
            assert result["ocr_text"] == "Texto extraído"
            assert result["confidence"] == 85.5
    
    @pytest.mark.asyncio
    async def test_process_file_from_bytes_failure(self, ocr_service):
        """Testa falha no processamento de arquivo."""
        # Arrange
        file_content = b"test content"
        file_type = "text/plain"
        file_name = "test.txt"
        
        # Mock do processamento de arquivo
        with patch.object(ocr_service, 'process_file') as mock_process:
            mock_process.return_value = {
                "success": False,
                "error": "Erro no processamento"
            }
            
            # Act
            result = await ocr_service.process_file_from_bytes(file_content, file_type, file_name)
            
            # Assert
            assert result["success"] is False
            assert "Erro no processamento" in result["error"]
    
    def test_calculate_confidence_empty_text(self, ocr_service):
        """Testa cálculo de confiança para texto vazio."""
        # Act
        confidence = ocr_service._calculate_confidence("")
        
        # Assert
        assert confidence == 0.0
    
    def test_calculate_confidence_high_quality(self, ocr_service):
        """Testa cálculo de confiança para texto de alta qualidade."""
        # Arrange
        text = "Hemoglobina 14.5 g/dL Creatinina 1.2 mg/dL"
        
        # Act
        confidence = ocr_service._calculate_confidence(text)
        
        # Assert
        assert confidence > 80.0  # Deve ter alta confiança
    
    def test_calculate_confidence_low_quality(self, ocr_service):
        """Testa cálculo de confiança para texto de baixa qualidade."""
        # Arrange
        text = "??? ??? ??? ??? ???"
        
        # Act
        confidence = ocr_service._calculate_confidence(text)
        
        # Assert
        assert confidence < 50.0  # Deve ter baixa confiança
    
    def test_get_file_extension_with_extension(self, ocr_service):
        """Testa extração de extensão de arquivo."""
        # Act
        extension = ocr_service._get_file_extension("test.pdf")
        
        # Assert
        assert extension == ".pdf"
    
    def test_get_file_extension_without_extension(self, ocr_service):
        """Testa arquivo sem extensão."""
        # Act
        extension = ocr_service._get_file_extension("testfile")
        
        # Assert
        assert extension == ""
    
    def test_get_file_extension_multiple_dots(self, ocr_service):
        """Testa arquivo com múltiplos pontos."""
        # Act
        extension = ocr_service._get_file_extension("test.backup.pdf")
        
        # Assert
        assert extension == ".pdf"
    
    @pytest.mark.asyncio
    async def test_get_ocr_languages_success(self, ocr_service):
        """Testa obtenção de idiomas OCR."""
        # Arrange
        mock_languages = ["por", "eng", "spa"]
        
        with patch('pytesseract.get_languages') as mock_get_languages:
            mock_get_languages.return_value = mock_languages
            
            # Act
            result = await ocr_service.get_ocr_languages()
            
            # Assert
            assert result["success"] is True
            assert result["languages"] == mock_languages
    
    @pytest.mark.asyncio
    async def test_get_ocr_languages_failure(self, ocr_service):
        """Testa falha na obtenção de idiomas OCR."""
        # Arrange
        with patch('pytesseract.get_languages') as mock_get_languages:
            mock_get_languages.side_effect = Exception("Tesseract error")
            
            # Act
            result = await ocr_service.get_ocr_languages()
            
            # Assert
            assert result["success"] is False
            assert "Tesseract error" in result["error"]
    
    def test_cleanup(self, ocr_service):
        """Testa limpeza de recursos."""
        # Arrange
        mock_executor = Mock()
        ocr_service.executor = mock_executor
        
        # Act
        ocr_service.cleanup()
        
        # Assert
        mock_executor.shutdown.assert_called_once_with(wait=True)
    
    @pytest.mark.asyncio
    async def test_process_file_text_success(self, ocr_service):
        """Testa processamento de arquivo de texto."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Teste de texto para OCR")
            temp_file_path = temp_file.name
        
        try:
            # Act
            result = await ocr_service._read_text_file(temp_file_path)
            
            # Assert
            assert result == "Teste de texto para OCR"
        finally:
            # Cleanup
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_process_file_text_failure(self, ocr_service):
        """Testa falha no processamento de arquivo de texto."""
        # Arrange
        non_existent_path = "/path/that/does/not/exist.txt"
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro ao ler arquivo de texto"):
            await ocr_service._read_text_file(non_existent_path)
    
    @pytest.mark.asyncio
    async def test_process_file_invalid_type(self, ocr_service):
        """Testa erro para tipo de arquivo inválido."""
        # Arrange
        file_path = "test.xyz"
        file_type = "application/unknown"
        
        # Act
        result = await ocr_service.process_file(file_path, file_type)
        
        # Assert
        assert result["success"] is False
        assert "não suportado" in result["error"]
    
    def test_tesseract_config_initialization(self, ocr_service):
        """Testa inicialização da configuração do Tesseract."""
        # Assert
        assert "--oem 3" in ocr_service.tesseract_config
        assert "--psm 6" in ocr_service.tesseract_config
        assert "tessedit_char_whitelist" in ocr_service.tesseract_config
    
    def test_executor_initialization(self, ocr_service):
        """Testa inicialização do executor."""
        # Assert
        assert ocr_service.executor is not None
        assert ocr_service.executor._max_workers == 2


class TestOCRServiceIntegration:
    """Testes de integração para OCRService."""
    
    @pytest.fixture
    def ocr_service(self):
        """Instância do OCRService para testes de integração."""
        return OCRService()
    
    @pytest.mark.asyncio
    async def test_text_file_processing_integration(self, ocr_service):
        """Teste de integração para arquivo de texto."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Hemoglobina: 14.5 g/dL\nCreatinina: 1.2 mg/dL")
            temp_file_path = temp_file.name
        
        try:
            # Act
            result = await ocr_service.process_file(temp_file_path, "text/plain")
            
            # Assert
            assert result["success"] is True
            assert "Hemoglobina" in result["ocr_text"]
            assert "Creatinina" in result["ocr_text"]
            assert result["confidence"] > 0
            assert result["text_hash"] is not None
        finally:
            # Cleanup
            os.unlink(temp_file_path)
