"""
Testes para endpoints de autenticação.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from src.api.auth import (
    register_user, login_user, get_current_user_profile,
    update_user_profile, logout_user, refresh_access_token
)
from src.models.auth import (
    UserRegisterRequest, UserLoginRequest, UserProfileUpdate
)


class TestAuthEndpoints:
    """Testes para endpoints de autenticação."""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock do cliente Supabase."""
        client = Mock()
        client.sign_up = AsyncMock()
        client.sign_in = AsyncMock()
        client.get_current_user = AsyncMock()
        client.refresh_token = AsyncMock()
        return client
    
    @pytest.fixture
    def mock_api_logger(self):
        """Mock do logger da API."""
        logger = Mock()
        logger.log_operation = Mock()
        logger.log_error = Mock()
        return logger
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, mock_supabase_client, mock_api_logger):
        """Testa registro bem-sucedido de usuário."""
        # Arrange
        request = UserRegisterRequest(
            email="dr.silva@exemplo.com",
            password="senha123",
            password_confirm="senha123",
            full_name="Dr. João Silva",
            crm="12345-SP",
            specialty="Cardiologia",
            phone="(11) 99999-9999"
        )
        
        mock_supabase_client.sign_up.return_value = {
            "success": True,
            "user_id": "user-123"
        }
        
        with patch("src.api.auth.supabase_client", mock_supabase_client), \
             patch("src.api.auth.api_logger", mock_api_logger):
            
            # Act
            result = await register_user(request)
            
            # Assert
            assert result.success is True
            assert result.user_id == "user-123"
            assert result.email == "dr.silva@exemplo.com"
            assert result.full_name == "Dr. João Silva"
            assert result.crm == "12345-SP"
            assert result.specialty == "Cardiologia"
            
            # Verifica se sign_up foi chamado
            mock_supabase_client.sign_up.assert_called_once_with(
                email="dr.silva@exemplo.com",
                password="senha123",
                user_metadata={
                    "full_name": "Dr. João Silva",
                    "crm": "12345-SP",
                    "specialty": "Cardiologia",
                    "phone": "(11) 99999-9999"
                }
            )
    
    @pytest.mark.asyncio
    async def test_register_user_password_mismatch(self, mock_supabase_client, mock_api_logger):
        """Testa erro quando senhas não coincidem."""
        # Arrange
        request = UserRegisterRequest(
            email="dr.silva@exemplo.com",
            password="senha123",
            password_confirm="senha456",
            full_name="Dr. João Silva",
            crm="12345-SP",
            specialty="Cardiologia",
            phone="(11) 99999-9999"
        )
        
        with patch("src.api.auth.supabase_client", mock_supabase_client), \
             patch("src.api.auth.api_logger", mock_api_logger):
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await register_user(request)
            
            assert exc_info.value.status_code == 400
            assert "Senhas não coincidem" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_register_user_short_password(self, mock_supabase_client, mock_api_logger):
        """Testa erro quando senha é muito curta."""
        # Arrange
        request = UserRegisterRequest(
            email="dr.silva@exemplo.com",
            password="123",
            password_confirm="123",
            full_name="Dr. João Silva",
            crm="12345-SP",
            specialty="Cardiologia",
            phone="(11) 99999-9999"
        )
        
        with patch("src.api.auth.supabase_client", mock_supabase_client), \
             patch("src.api.auth.api_logger", mock_api_logger):
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await register_user(request)
            
            assert exc_info.value.status_code == 400
            assert "pelo menos 8 caracteres" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_register_user_supabase_error(self, mock_supabase_client, mock_api_logger):
        """Testa erro do Supabase durante registro."""
        # Arrange
        request = UserRegisterRequest(
            email="dr.silva@exemplo.com",
            password="senha123",
            password_confirm="senha123",
            full_name="Dr. João Silva",
            crm="12345-SP",
            specialty="Cardiologia",
            phone="(11) 99999-9999"
        )
        
        mock_supabase_client.sign_up.return_value = {
            "success": False,
            "error": "Email já cadastrado"
        }
        
        with patch("src.api.auth.supabase_client", mock_supabase_client), \
             patch("src.api.auth.api_logger", mock_api_logger):
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await register_user(request)
            
            assert exc_info.value.status_code == 400
            assert "Email já cadastrado" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_login_user_success(self, mock_supabase_client, mock_api_logger):
        """Testa login bem-sucedido."""
        # Arrange
        request = UserLoginRequest(
            email="dr.silva@exemplo.com",
            password="senha123"
        )
        
        mock_supabase_client.sign_in.return_value = {
            "success": True,
            "access_token": "access-token-123",
            "refresh_token": "refresh-token-123"
        }
        
        mock_supabase_client.get_current_user.return_value = {
            "success": True,
            "user": {
                "id": "user-123",
                "email": "dr.silva@exemplo.com",
                "created_at": "2024-01-01T00:00:00Z",
                "user_metadata": {
                    "full_name": "Dr. João Silva",
                    "crm": "12345-SP",
                    "specialty": "Cardiologia",
                    "phone": "(11) 99999-9999"
                }
            }
        }
        
        with patch("src.api.auth.supabase_client", mock_supabase_client), \
             patch("src.api.auth.api_logger", mock_api_logger):
            
            # Act
            result = await login_user(request)
            
            # Assert
            assert result.success is True
            assert result.access_token == "access-token-123"
            assert result.refresh_token == "refresh-token-123"
            assert result.token_type == "bearer"
            assert result.expires_in == 3600
            
            assert result.user.id == "user-123"
            assert result.user.email == "dr.silva@exemplo.com"
            assert result.user.full_name == "Dr. João Silva"
            assert result.user.crm == "12345-SP"
            assert result.user.specialty == "Cardiologia"
    
    @pytest.mark.asyncio
    async def test_login_user_invalid_credentials(self, mock_supabase_client, mock_api_logger):
        """Testa erro de credenciais inválidas."""
        # Arrange
        request = UserLoginRequest(
            email="dr.silva@exemplo.com",
            password="senha_errada"
        )
        
        mock_supabase_client.sign_in.return_value = {
            "success": False,
            "error": "Credenciais inválidas"
        }
        
        with patch("src.api.auth.supabase_client", mock_supabase_client), \
             patch("src.api.auth.api_logger", mock_api_logger):
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await login_user(request)
            
            assert exc_info.value.status_code == 401
            assert "Credenciais inválidas" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_current_user_profile_success(self, mock_supabase_client, mock_api_logger):
        """Testa obtenção bem-sucedida do perfil do usuário."""
        # Arrange
        mock_credentials = Mock()
        mock_credentials.credentials = "valid-token"
        
        mock_supabase_client.get_current_user.return_value = {
            "success": True,
            "user": {
                "id": "user-123",
                "email": "dr.silva@exemplo.com",
                "created_at": "2024-01-01T00:00:00Z",
                "user_metadata": {
                    "full_name": "Dr. João Silva",
                    "crm": "12345-SP",
                    "specialty": "Cardiologia",
                    "phone": "(11) 99999-9999"
                }
            }
        }
        
        with patch("src.api.auth.supabase_client", mock_supabase_client), \
             patch("src.api.auth.api_logger", mock_api_logger):
            
            # Act
            result = await get_current_user_profile(mock_credentials)
            
            # Assert
            assert result.id == "user-123"
            assert result.email == "dr.silva@exemplo.com"
            assert result.full_name == "Dr. João Silva"
            assert result.crm == "12345-SP"
            assert result.specialty == "Cardiologia"
    
    @pytest.mark.asyncio
    async def test_get_current_user_profile_invalid_token(self, mock_supabase_client, mock_api_logger):
        """Testa erro com token inválido."""
        # Arrange
        mock_credentials = Mock()
        mock_credentials.credentials = "invalid-token"
        
        mock_supabase_client.get_current_user.return_value = {
            "success": False,
            "error": "Token inválido"
        }
        
        with patch("src.api.auth.supabase_client", mock_supabase_client), \
             patch("src.api.auth.api_logger", mock_api_logger):
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_profile(mock_credentials)
            
            assert exc_info.value.status_code == 401
            assert "Token inválido" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, mock_supabase_client, mock_api_logger):
        """Testa atualização bem-sucedida do perfil."""
        # Arrange
        mock_credentials = Mock()
        mock_credentials.credentials = "valid-token"
        
        profile_update = UserProfileUpdate(
            full_name="Dr. João Silva Santos",
            phone="(11) 88888-8888"
        )
        
        mock_supabase_client.get_current_user.return_value = {
            "success": True,
            "user": {
                "id": "user-123",
                "email": "dr.silva@exemplo.com",
                "created_at": "2024-01-01T00:00:00Z",
                "user_metadata": {
                    "full_name": "Dr. João Silva Santos",
                    "crm": "12345-SP",
                    "specialty": "Cardiologia",
                    "phone": "(11) 88888-8888"
                }
            }
        }
        
        # Mock da tabela users
        mock_table = Mock()
        mock_table.update.return_value.eq.return_value.execute.return_value.data = [{"id": "user-123"}]
        mock_supabase_client.get_table.return_value = mock_table
        
        with patch("src.api.auth.supabase_client", mock_supabase_client), \
             patch("src.api.auth.api_logger", mock_api_logger):
            
            # Act
            result = await update_user_profile(profile_update, mock_credentials)
            
            # Assert
            assert result.full_name == "Dr. João Silva Santos"
            assert result.phone == "(11) 88888-8888"
    
    @pytest.mark.asyncio
    async def test_logout_user_success(self, mock_supabase_client, mock_api_logger):
        """Testa logout bem-sucedido."""
        # Arrange
        mock_credentials = Mock()
        mock_credentials.credentials = "valid-token"
        
        mock_supabase_client.get_current_user.return_value = {
            "success": True,
            "user": {
                "id": "user-123",
                "email": "dr.silva@exemplo.com"
            }
        }
        
        with patch("src.api.auth.supabase_client", mock_supabase_client), \
             patch("src.api.auth.api_logger", mock_api_logger):
            
            # Act
            result = await logout_user(mock_credentials)
            
            # Assert
            assert result["success"] is True
            assert "Logout realizado com sucesso" in result["message"]
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, mock_supabase_client, mock_api_logger):
        """Testa renovação bem-sucedida do token."""
        # Arrange
        refresh_token = "refresh-token-123"
        
        mock_supabase_client.refresh_token.return_value = {
            "success": True,
            "access_token": "new-access-token",
            "refresh_token": "new-refresh-token"
        }
        
        with patch("src.api.auth.supabase_client", mock_supabase_client), \
             patch("src.api.auth.api_logger", mock_api_logger):
            
            # Act
            result = await refresh_access_token(refresh_token)
            
            # Assert
            assert result["success"] is True
            assert result["access_token"] == "new-access-token"
            assert result["refresh_token"] == "new-refresh-token"
            assert result["token_type"] == "bearer"
            assert result["expires_in"] == 3600
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, mock_supabase_client, mock_api_logger):
        """Testa erro com refresh token inválido."""
        # Arrange
        refresh_token = "invalid-refresh-token"
        
        mock_supabase_client.refresh_token.return_value = {
            "success": False,
            "error": "Refresh token expirado"
        }
        
        with patch("src.api.auth.supabase_client", mock_supabase_client), \
             patch("src.api.auth.api_logger", mock_api_logger):
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await refresh_access_token(refresh_token)
            
            assert exc_info.value.status_code == 401
            assert "Refresh token inválido" in str(exc_info.value.detail)
