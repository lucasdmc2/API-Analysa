"""
Cliente Supabase para autenticação e operações de banco de dados.
"""

import os
from supabase import create_client, Client
from typing import Optional, Dict, Any
import asyncio
from .config import get_settings_lazy


class SupabaseClient:
    """Cliente Supabase com métodos de autenticação e operações de banco."""
    
    def __init__(self):
        """Inicializa o cliente Supabase."""
        config = get_settings_lazy()
        self.supabase: Client = create_client(
            config.supabase_url,
            config.supabase_anon_key
        )
        self._current_user = None
    
    async def sign_up(self, email: str, password: str, full_name: str, crm: str) -> Dict[str, Any]:
        """
        Registra um novo usuário médico.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            full_name: Nome completo
            crm: CRM do médico
            
        Returns:
            Dict com resultado da operação
        """
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
            
            if response.user:
                # Cria registro na tabela users
                await self._create_user_profile(response.user.id, full_name, crm)
                
            return {"success": True, "user": response.user}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Autentica um usuário existente.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Dict com tokens e dados do usuário
        """
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
    
    async def get_current_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Obtém dados do usuário atual pelo token.
        
        Args:
            access_token: Token de acesso JWT
            
        Returns:
            Dados do usuário ou None
        """
        try:
            user = self.supabase.auth.get_user(access_token)
            return user.user
        except Exception:
            return None
    
    async def _create_user_profile(self, user_id: str, full_name: str, crm: str) -> bool:
        """
        Cria perfil do usuário na tabela users.
        
        Args:
            user_id: ID do usuário no Supabase Auth
            full_name: Nome completo
            crm: CRM do médico
            
        Returns:
            True se criado com sucesso
        """
        try:
            # Insere na tabela users
            data = {
                "id": user_id,
                "full_name": full_name,
                "crm": crm,
                "email": "",  # Será preenchido pelo trigger
                "is_active": True
            }
            
            result = self.supabase.table("users").insert(data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            print(f"Erro ao criar perfil do usuário: {e}")
            return False
    
    async def _with_retry(self, operation, max_retries: int = None, delay: float = 1.0):
        """
        Executa operação com retry pattern.
        
        Args:
            operation: Função a ser executada
            max_retries: Número máximo de tentativas
            delay: Delay inicial entre tentativas
            
        Returns:
            Resultado da operação
            
        Raises:
            Exception: Se todas as tentativas falharem
        """
        if max_retries is None:
            config = get_settings_lazy()
            max_retries = config.max_retries
            
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(delay * (2 ** attempt))
    
    def get_table(self, table_name: str):
        """
        Obtém referência para uma tabela.
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            Referência da tabela
        """
        return self.supabase.table(table_name)
    
    def get_storage(self, bucket_name: str):
        """
        Obtém referência para um bucket de storage.
        
        Args:
            bucket_name: Nome do bucket
            
        Returns:
            Referência do bucket
        """
        return self.supabase.storage.from_(bucket_name)


# Instância global do cliente (lazy)
_supabase_client = None

def get_supabase_client():
    """Retorna o cliente Supabase, criando se necessário."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client

# Para compatibilidade com código existente (lazy)
def supabase_client():
    """Retorna o cliente Supabase."""
    return get_supabase_client()
