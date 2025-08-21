"""
Endpoints de autenticação e autorização.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from src.core.supabase_client import supabase_client
from src.core.logging import api_logger
from src.models.auth import (
    UserRegisterRequest, UserRegisterResponse,
    UserLoginRequest, UserLoginResponse,
    UserProfile, UserProfileUpdate
)

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegisterRequest) -> UserRegisterResponse:
    """
    Registra um novo usuário médico.
    
    Args:
        request: Dados de registro
        
    Returns:
        Dados do usuário criado
    """
    try:
        # Valida dados de entrada
        if request.password != request.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senhas não coincidem"
            )
        
        if len(request.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve ter pelo menos 8 caracteres"
            )
        
        # Registra usuário no Supabase Auth
        auth_result = await supabase_client().sign_up(
            email=request.email,
            password=request.password,
            user_metadata={
                "full_name": request.full_name,
                "crm": request.crm,
                "specialty": request.specialty,
                "phone": request.phone
            }
        )
        
        if not auth_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=auth_result["error"]
            )
        
        # Log da operação
        api_logger.log_operation(
            operation="user_registration",
            details={
                "email": request.email,
                "crm": request.crm,
                "specialty": request.specialty
            }
        )
        
        return UserRegisterResponse(
            success=True,
            user_id=auth_result["user_id"],
            email=request.email,
            full_name=request.full_name,
            crm=request.crm,
            specialty=request.specialty,
            message="Usuário registrado com sucesso"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="user_registration",
            details={"email": request.email}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.post("/login", response_model=UserLoginResponse)
async def login_user(request: UserLoginRequest) -> UserLoginResponse:
    """
    Autentica um usuário médico.
    
    Args:
        request: Credenciais de login
        
    Returns:
        Token de acesso e dados do usuário
    """
    try:
        # Autentica usuário no Supabase
        auth_result = await supabase_client().sign_in(
            email=request.email,
            password=request.password
        )
        
        if not auth_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )
        
        # Busca perfil completo do usuário
        user_profile = await supabase_client().get_current_user(
            auth_result["access_token"]
        )
        
        if not user_profile["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao buscar perfil do usuário"
            )
        
        # Log da operação
        api_logger.log_operation(
            operation="user_login",
            details={
                "email": request.email,
                "user_id": user_profile["user"]["id"]
            }
        )
        
        return UserLoginResponse(
            success=True,
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            token_type="bearer",
            expires_in=3600,  # 1 hora
            user=UserProfile(
                id=user_profile["user"]["id"],
                email=user_profile["user"]["email"],
                full_name=user_profile["user"]["user_metadata"]["full_name"],
                crm=user_profile["user"]["user_metadata"]["crm"],
                specialty=user_profile["user"]["user_metadata"]["specialty"],
                phone=user_profile["user"]["user_metadata"]["phone"],
                is_active=user_profile["user"]["user_metadata"].get("is_active", True),
                created_at=user_profile["user"]["created_at"]
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="user_login",
            details={"email": request.email}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserProfile:
    """
    Obtém perfil do usuário autenticado.
    
    Args:
        credentials: Token de autorização
        
    Returns:
        Perfil do usuário
    """
    try:
        # Valida token e busca usuário
        user_result = await supabase_client().get_current_user(
            credentials.credentials
        )
        
        if not user_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
        
        user = user_result["user"]
        
        return UserProfile(
            id=user["id"],
            email=user["email"],
            full_name=user["user_metadata"]["full_name"],
            crm=user["user_metadata"]["crm"],
            specialty=user["user_metadata"]["specialty"],
            phone=user["user_metadata"]["phone"],
            is_active=user["user_metadata"].get("is_active", True),
            created_at=user["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="get_user_profile"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserProfile:
    """
    Atualiza perfil do usuário autenticado.
    
    Args:
        profile_update: Dados para atualização
        credentials: Token de autorização
        
    Returns:
        Perfil atualizado
    """
    try:
        # Valida token e busca usuário
        user_result = await supabase_client().get_current_user(
            credentials.credentials
        )
        
        if not user_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
        
        user_id = user_result["user"]["id"]
        
        # Atualiza perfil no banco
        update_data = profile_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.now().isoformat()
        
        result = supabase_client().get_table("users").update(update_data).eq("id", user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar perfil"
            )
        
        # Busca perfil atualizado
        updated_user = await supabase_client().get_current_user(credentials.credentials)
        
        # Log da operação
        api_logger.log_operation(
            operation="user_profile_update",
            details={
                "user_id": user_id,
                "updated_fields": list(update_data.keys())
            }
        )
        
        user = updated_user["user"]
        return UserProfile(
            id=user["id"],
            email=user["email"],
            full_name=user["user_metadata"]["full_name"],
            crm=user["user_metadata"]["crm"],
            specialty=user["user_metadata"]["specialty"],
            phone=user["user_metadata"]["phone"],
            is_active=user["user_metadata"].get("is_active", True),
            created_at=user["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="user_profile_update"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.post("/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Faz logout do usuário (invalida token).
    
    Args:
        credentials: Token de autorização
        
    Returns:
        Confirmação de logout
    """
    try:
        # Valida token
        user_result = await supabase_client().get_current_user(
            credentials.credentials
        )
        
        if not user_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
        
        # Log da operação
        api_logger.log_operation(
            operation="user_logout",
            details={
                "user_id": user_result["user"]["id"]
            }
        )
        
        # Nota: Supabase não tem endpoint de logout, mas o token pode ser invalidado no cliente
        return {
            "success": True,
            "message": "Logout realizado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="user_logout"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )


@router.post("/refresh")
async def refresh_access_token(
    refresh_token: str
) -> Dict[str, Any]:
    """
    Renova token de acesso usando refresh token.
    
    Args:
        refresh_token: Token de renovação
        
    Returns:
        Novo token de acesso
    """
    try:
        # Renova token no Supabase
        result = await supabase_client().refresh_token(refresh_token)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado"
            )
        
        return {
            "success": True,
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": "bearer",
            "expires_in": 3600
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error(
            error=str(e),
            operation="token_refresh"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor"
        )
