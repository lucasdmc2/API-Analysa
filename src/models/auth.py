"""
Modelos Pydantic para autenticação e usuários.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """Dados para registro de usuário."""
    
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=8, description="Senha (mínimo 8 caracteres)")
    password_confirm: str = Field(..., description="Confirmação da senha")
    full_name: str = Field(..., min_length=3, description="Nome completo")
    crm: str = Field(..., description="Número do CRM")
    specialty: str = Field(..., description="Especialidade médica")
    phone: str = Field(..., description="Telefone de contato")
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Senhas não coincidem')
        return v


class UserRegisterResponse(BaseModel):
    """Resposta do registro de usuário."""
    
    success: bool = Field(..., description="Indica se o registro foi bem-sucedido")
    user_id: str = Field(..., description="ID do usuário criado")
    email: str = Field(..., description="Email do usuário")
    full_name: str = Field(..., description="Nome completo")
    crm: str = Field(..., description="Número do CRM")
    specialty: str = Field(..., description="Especialidade médica")
    message: str = Field(..., description="Mensagem de confirmação")


class UserLoginRequest(BaseModel):
    """Dados para login de usuário."""
    
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")


class UserProfile(BaseModel):
    """Perfil do usuário."""
    
    id: str = Field(..., description="ID do usuário")
    email: str = Field(..., description="Email do usuário")
    full_name: str = Field(..., description="Nome completo")
    crm: str = Field(..., description="Número do CRM")
    specialty: str = Field(..., description="Especialidade médica")
    phone: str = Field(..., description="Telefone de contato")
    is_active: bool = Field(..., description="Indica se o usuário está ativo")
    created_at: str = Field(..., description="Data de criação")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "user-123",
                "email": "dr.silva@exemplo.com",
                "full_name": "Dr. João Silva",
                "crm": "12345-SP",
                "specialty": "Cardiologia",
                "phone": "(11) 99999-9999",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class UserLoginResponse(BaseModel):
    """Resposta do login de usuário."""
    
    success: bool = Field(..., description="Indica se o login foi bem-sucedido")
    access_token: str = Field(..., description="Token de acesso")
    refresh_token: str = Field(..., description="Token de renovação")
    token_type: str = Field(..., description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    user: UserProfile = Field(..., description="Perfil do usuário")


class UserProfileUpdate(BaseModel):
    """Dados para atualização do perfil."""
    
    full_name: Optional[str] = Field(None, min_length=3, description="Nome completo")
    crm: Optional[str] = Field(None, description="Número do CRM")
    specialty: Optional[str] = Field(None, description="Especialidade médica")
    phone: Optional[str] = Field(None, description="Telefone de contato")
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "Dr. João Silva Santos",
                "phone": "(11) 88888-8888"
            }
        }
