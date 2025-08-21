"""
Sistema de logging anonimizado para LGPD compliance.
"""

import structlog
import hashlib
from typing import Any, Dict
from datetime import datetime
import sys


class AnonymizedProcessor:
    """Processador que anonimiza dados pessoais dos logs."""
    
    def __init__(self):
        self.sensitive_fields = {
            'email', 'cpf', 'crm', 'phone', 'address', 
            'full_name', 'user_id', 'patient_id'
        }
    
    def __call__(self, logger, method_name, event_dict):
        """Processa o evento de log anonimizando dados sensíveis."""
        anonymized = event_dict.copy()
        
        for field in self.sensitive_fields:
            if field in anonymized:
                value = anonymized[field]
                if value and isinstance(value, str):
                    # Anonimiza com hash parcial
                    anonymized[field] = f"***{hashlib.md5(value.encode()).hexdigest()[:8]}***"
                elif value and isinstance(value, (int, float)):
                    # Para IDs numéricos, mantém apenas os últimos dígitos
                    anonymized[field] = f"***{str(value)[-4:]}***"
        
        return anonymized


def setup_logging():
    """Configura o sistema de logging estruturado."""
    
    # Configuração do structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            AnonymizedProcessor(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configuração do logging padrão do Python
    import logging
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO
    )


class AnonymizedLogger:
    """Logger que automaticamente anonimiza dados pessoais."""
    
    def __init__(self, logger_name: str = None):
        self.logger = structlog.get_logger(logger_name)
    
    def log_operation(self, operation: str, user_id: str = None, details: Dict[str, Any] = None):
        """
        Log de operação com dados anonimizados.
        
        Args:
            operation: Nome da operação
            user_id: ID do usuário (será anonimizado)
            details: Detalhes adicionais (serão anonimizados)
        """
        log_data = {
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }
        
        if user_id:
            log_data["user_id"] = f"user_{hashlib.md5(str(user_id).encode()).hexdigest()[:8]}"
        
        if details:
            log_data["details"] = details
        
        self.logger.info("API Operation", **log_data)
    
    def log_error(self, error: str, operation: str = None, user_id: str = None, details: Dict[str, Any] = None):
        """
        Log de erro com dados anonimizados.
        
        Args:
            error: Mensagem de erro
            operation: Nome da operação
            user_id: ID do usuário (será anonimizado)
            details: Detalhes adicionais (serão anonimizados)
        """
        log_data = {
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        if operation:
            log_data["operation"] = operation
        
        if user_id:
            log_data["user_id"] = f"user_{hashlib.md5(str(user_id).encode()).hexdigest()[:8]}"
        
        if details:
            log_data["details"] = details
        
        self.logger.error("API Error", **log_data)
    
    def log_security_event(self, event_type: str, user_id: str = None, ip_address: str = None, details: Dict[str, Any] = None):
        """
        Log de eventos de segurança com dados anonimizados.
        
        Args:
            event_type: Tipo do evento de segurança
            user_id: ID do usuário (será anonimizado)
            ip_address: Endereço IP (será anonimizado)
            details: Detalhes adicionais (serão anonimizados)
        """
        log_data = {
            "security_event": event_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if user_id:
            log_data["user_id"] = f"user_{hashlib.md5(str(user_id).encode()).hexdigest()[:8]}"
        
        if ip_address:
            # Anonimiza IP mantendo apenas a rede
            ip_parts = ip_address.split('.')
            if len(ip_parts) == 4:
                log_data["ip_network"] = f"{ip_parts[0]}.{ip_parts[1]}.***.***"
            else:
                log_data["ip_network"] = "***"
        
        if details:
            log_data["details"] = details
        
        self.logger.warning("Security Event", **log_data)


# Logger global para uso em toda a aplicação
api_logger = AnonymizedLogger("api_exames_medicos")
