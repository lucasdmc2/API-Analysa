"""
Testes para configurações da aplicação.
"""

import pytest
import os
from unittest.mock import patch
from src.core.config import Settings, validate_environment


class TestSettings:
    """Testes para a classe Settings."""
    
    def test_settings_defaults(self):
        """Testa valores padrão das configurações."""
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_ANON_KEY': 'test-key',
            'DEBUG': 'false'
        }):
            settings = Settings()
    
            assert settings.app_name == "API de Exames Médicos"
            assert settings.app_version == "0.1.0"
            assert settings.debug is False
            assert settings.max_file_size == 5 * 1024 * 1024  # 5MB
            assert settings.signed_url_expiry == 86400  # 24h
    
    def test_settings_from_env(self):
        """Testa configurações a partir de variáveis de ambiente."""
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://custom.supabase.co',
            'SUPABASE_ANON_KEY': 'custom-key',
            'DEBUG': 'true',
            'MAX_FILE_SIZE': '10485760'  # 10MB
        }):
            settings = Settings()
            
            assert settings.supabase_url == 'https://custom.supabase.co'
            assert settings.supabase_anon_key == 'custom-key'
            assert settings.debug is True
            assert settings.max_file_size == 10485760
    
    def test_required_env_vars_missing(self):
        """Testa erro quando variáveis obrigatórias estão faltando."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Variáveis de ambiente obrigatórias não definidas"):
                validate_environment()
    
    def test_required_env_vars_present(self):
        """Testa sucesso quando variáveis obrigatórias estão presentes."""
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_ANON_KEY': 'test-key'
        }):
            # Não deve levantar exceção
            validate_environment()


class TestConfigValidation:
    """Testes para validação de configuração."""
    
    def test_validate_environment_success(self):
        """Testa validação bem-sucedida do ambiente."""
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_ANON_KEY': 'test-key'
        }):
            # Não deve levantar exceção
            validate_environment()
    
    def test_validate_environment_missing_supabase_url(self):
        """Testa erro quando SUPABASE_URL está faltando."""
        # Remove SUPABASE_URL do ambiente
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, {
                'SUPABASE_ANON_KEY': 'test-key'
            }):
                with pytest.raises(ValueError, match="SUPABASE_URL"):
                    validate_environment()
    
    def test_validate_environment_missing_supabase_anon_key(self):
        """Testa erro quando SUPABASE_ANON_KEY está faltando."""
        # Remove SUPABASE_ANON_KEY do ambiente
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, {
                'SUPABASE_URL': 'https://test.supabase.co'
            }):
                with pytest.raises(ValueError, match="SUPABASE_ANON_KEY"):
                    validate_environment()
