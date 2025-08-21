"""
Configurações da aplicação usando Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # FastAPI
    app_name: str = "API de Exames Médicos"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: Optional[str] = None
    
    # Storage
    max_file_size: int = 5 * 1024 * 1024  # 5MB
    signed_url_expiry: int = 86400  # 24 horas
    
    # Tesseract
    tesseract_cmd: str = "/usr/bin/tesseract"
    tesseract_lang: str = "por+eng"
    
    # Resilience
    max_retries: int = 3
    circuit_breaker_threshold: int = 5
    recovery_timeout: int = 60
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instância global das configurações (lazy loading)
_settings = None

def get_settings():
    """Retorna as configurações, criando se necessário."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Para compatibilidade com código existente
def get_settings_lazy():
    """Retorna as configurações de forma lazy."""
    return get_settings()

# Instância global das configurações
try:
    _settings = get_settings()
except Exception:
    # Fallback para configurações básicas se houver erro
    _settings = None

# Validações de ambiente
def validate_environment():
    """Valida se as variáveis de ambiente obrigatórias estão definidas."""
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(
            f"Variáveis de ambiente obrigatórias não definidas: {', '.join(missing_vars)}"
        )

# Validação automática na importação (comentada para evitar erro)
# try:
#     validate_environment()
# except ValueError as e:
#     print(f"Erro de configuração: {e}")
#     print("Certifique-se de definir as variáveis de ambiente obrigatórias.")
#     raise
