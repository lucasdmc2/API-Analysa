#!/usr/bin/env python3
"""
Script para configurar ambiente de teste.
"""

import os
import sys

def setup_test_environment():
    """Configura variáveis de ambiente para testes."""
    print("🔧 Configurando ambiente de teste...")
    
    # Variáveis de ambiente para teste
    test_env = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_ANON_KEY": "test-key",
        "SUPABASE_SERVICE_KEY": "test-service-key",
        "SECRET_KEY": "test-secret-key-for-testing-only",
        "DEBUG": "true",
        "LOG_LEVEL": "INFO",
        "MAX_FILE_SIZE": "5242880",
        "TESSERACT_CMD": "/usr/bin/tesseract",
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test"
    }
    
    # Aplica variáveis de ambiente
    for key, value in test_env.items():
        os.environ[key] = value
        print(f"✅ {key} = {value}")
    
    print("\n🎯 Ambiente de teste configurado!")
    print("   - Todas as variáveis obrigatórias definidas")
    print("   - Configurações de teste aplicadas")
    
    return True

if __name__ == "__main__":
    setup_test_environment()
