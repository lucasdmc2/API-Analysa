"""
Testes para o serviço de storage.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.storage_service import StorageService


class TestStorageService:
    """Testes para StorageService."""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock do cliente Supabase."""
        client = Mock()
        client.storage.from_.return_value = Mock()
        return client
    
    @pytest.fixture
    def storage_service(self, mock_supabase_client):
        """Instância do StorageService com mock."""
        return StorageService(mock_supabase_client)
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self, storage_service, mock_supabase_client):
        """Testa upload bem-sucedido."""
        # Arrange
        file_content = b"test content"
        file_name = "test.pdf"
        mime_type = "application/pdf"
        
        # Mock do upload
        mock_storage = Mock()
        mock_storage.upload.return_value = Mock(path="test_path")
        mock_supabase_client.storage.from_.return_value = mock_storage
        
        # Mock da URL assinada
        mock_storage.create_signed_url.return_value = Mock(signed_url="http://test.com/file")
        
        # Act
        result = await storage_service.upload_file(file_content, file_name, mime_type)
        
        # Assert
        assert result["success"] is True
        assert result["file_name"] == file_name
        assert result["file_size"] == len(file_content)
        assert result["mime_type"] == mime_type
        assert "signed_url" in result
    
    @pytest.mark.asyncio
    async def test_upload_file_too_large(self, storage_service):
        """Testa erro quando arquivo é muito grande."""
        # Arrange
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        file_name = "large.pdf"
        
        # Act
        result = await storage_service.upload_file(large_content, file_name)
        
        # Assert
        assert result["success"] is False
        assert "muito grande" in result["error"]
    
    @pytest.mark.asyncio
    async def test_upload_file_invalid_type(self, storage_service):
        """Testa erro quando tipo de arquivo não é suportado."""
        # Arrange
        file_content = b"test content"
        file_name = "test.exe"
        
        # Act
        result = await storage_service.upload_file(file_content, file_name)
        
        # Assert
        assert result["success"] is False
        assert "não suportado" in result["error"]
    
    @pytest.mark.asyncio
    async def test_upload_with_retry_success(self, storage_service, mock_supabase_client):
        """Testa upload com retry bem-sucedido."""
        # Arrange
        file_content = b"test content"
        file_name = "test.pdf"
        mime_type = "application/pdf"
        
        mock_storage = Mock()
        mock_storage.upload.return_value = Mock(path="test_path")
        mock_supabase_client.storage.from_.return_value = mock_storage
        
        # Act
        result = await storage_service._upload_with_retry(file_content, file_name, mime_type)
        
        # Assert
        assert result == "medical-exams/test_path"
        mock_storage.upload.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_with_retry_failure_then_success(self, storage_service, mock_supabase_client):
        """Testa upload com retry que falha e depois sucede."""
        # Arrange
        file_content = b"test content"
        file_name = "test.pdf"
        mime_type = "application/pdf"
        
        mock_storage = Mock()
        mock_storage.upload.side_effect = [Exception("Network error"), Mock(path="test_path")]
        mock_supabase_client.storage.from_.return_value = mock_storage
        
        # Act
        result = await storage_service._upload_with_retry(file_content, file_name, mime_type, max_retries=2)
        
        # Assert
        assert result == "medical-exams/test_path"
        assert mock_storage.upload.call_count == 2
    
    def test_infer_mime_type_pdf(self, storage_service):
        """Testa inferência de MIME type para PDF."""
        # Act
        mime_type = storage_service._infer_mime_type("document.pdf")
        
        # Assert
        assert mime_type == "application/pdf"
    
    def test_infer_mime_type_png(self, storage_service):
        """Testa inferência de MIME type para PNG."""
        # Act
        mime_type = storage_service._infer_mime_type("image.png")
        
        # Assert
        assert mime_type == "image/png"
    
    def test_infer_mime_type_unknown(self, storage_service):
        """Testa inferência de MIME type para extensão desconhecida."""
        # Act
        mime_type = storage_service._infer_mime_type("file.xyz")
        
        # Assert
        assert mime_type == "application/octet-stream"
    
    def test_is_allowed_file_type_valid(self, storage_service):
        """Testa validação de tipo de arquivo válido."""
        # Act & Assert
        assert storage_service._is_allowed_file_type("application/pdf") is True
        assert storage_service._is_allowed_file_type("image/png") is True
        assert storage_service._is_allowed_file_type("text/plain") is True
    
    def test_is_allowed_file_type_invalid(self, storage_service):
        """Testa validação de tipo de arquivo inválido."""
        # Act & Assert
        assert storage_service._is_allowed_file_type("application/exe") is False
        assert storage_service._is_allowed_file_type("text/html") is False
    
    def test_generate_unique_filename(self, storage_service):
        """Testa geração de nome único para arquivo."""
        # Arrange
        original_name = "test.pdf"
        
        # Act
        unique_name = storage_service._generate_unique_filename(original_name)
        
        # Assert
        assert unique_name.startswith("test_")
        assert unique_name.endswith(".pdf")
        assert len(unique_name) > len(original_name)  # Deve ter UUID
    
    @pytest.mark.asyncio
    async def test_delete_file_success(self, storage_service, mock_supabase_client):
        """Testa remoção bem-sucedida de arquivo."""
        # Arrange
        file_path = "medical-exams/test_file.pdf"
        mock_storage = Mock()
        mock_supabase_client.storage.from_.return_value = mock_storage
        
        # Act
        result = await storage_service.delete_file(file_path)
        
        # Assert
        assert result is True
        mock_storage.remove.assert_called_once_with(["test_file.pdf"])
    
    @pytest.mark.asyncio
    async def test_delete_file_failure(self, storage_service, mock_supabase_client):
        """Testa falha na remoção de arquivo."""
        # Arrange
        file_path = "medical-exams/test_file.pdf"
        mock_storage = Mock()
        mock_storage.remove.side_effect = Exception("Delete failed")
        mock_supabase_client.storage.from_.return_value = mock_storage
        
        # Act
        result = await storage_service.delete_file(file_path)
        
        # Assert
        assert result is False
