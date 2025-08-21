"""
Configuração para testes pytest.
"""

import pytest
import os
from unittest.mock import Mock, patch


@pytest.fixture(autouse=True)
def mock_environment():
    """Mock das variáveis de ambiente para testes."""
    # Mock das variáveis de ambiente necessárias
    env_vars = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_ANON_KEY": "test-anon-key",
        "SUPABASE_SERVICE_KEY": "test-service-key",
        "SECRET_KEY": "test-secret-key",
        "DEBUG": "true",
        "LOG_LEVEL": "INFO",
        "MAX_FILE_SIZE": "5242880",
        "TESSERACT_CMD": "/usr/bin/tesseract",
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test"
    }
    
    with patch.dict(os.environ, env_vars):
        # Mock da função get_settings
        with patch("src.core.config.get_settings") as mock_get_settings, \
             patch("src.core.config.get_settings_lazy") as mock_get_settings_lazy:
            
            mock_settings = Mock()
            mock_settings.supabase_url = "https://test.supabase.co"
            mock_settings.supabase_anon_key = "test-anon-key"
            mock_settings.supabase_service_key = "test-service-key"
            mock_settings.secret_key = "test-secret-key"
            mock_settings.debug = True
            mock_settings.log_level = "INFO"
            mock_settings.max_file_size = 5242880
            mock_settings.tesseract_cmd = "/usr/bin/tesseract"
            mock_settings.database_url = "postgresql://test:test@localhost:5432/test"
            mock_settings.app_name = "API de Exames Médicos"
            mock_settings.app_version = "1.0.0"
            
            mock_get_settings.return_value = mock_settings
            mock_get_settings_lazy.return_value = mock_settings
            yield


@pytest.fixture(autouse=True)
def mock_supabase():
    """Mock do cliente Supabase para testes."""
    with patch("src.core.supabase_client.supabase_client") as mock_client:
        # Mock das operações básicas
        mock_client.get_table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_client.get_table.return_value.insert.return_value.execute.return_value.data = [{"id": "test-id"}]
        mock_client.get_table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "test-id"}]
        
        yield mock_client


@pytest.fixture(autouse=True)
def mock_logging():
    """Mock do sistema de logging para testes."""
    with patch("src.core.logging.api_logger") as mock_logger:
        yield mock_logger
