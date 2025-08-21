#!/usr/bin/env python3
"""
Script para iniciar a aplicação FastAPI e testar o Swagger.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Configura variáveis de ambiente para teste
os.environ.update({
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_ANON_KEY": "test-key",
    "SUPABASE_SERVICE_KEY": "test-service-key",
    "SECRET_KEY": "test-secret-key",
    "DEBUG": "true",
    "LOG_LEVEL": "INFO",
    "MAX_FILE_SIZE": "5242880",
    "TESSERACT_CMD": "/usr/bin/tesseract",
    "DATABASE_URL": "postgresql://test:test@localhost:5432/test"
})

# Adiciona o diretório src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def start_app():
    """Inicia a aplicação FastAPI."""
    try:
        print("🚀 Iniciando API de Exames Médicos...")
        print("📚 Swagger UI estará disponível em: http://localhost:8000/docs")
        print("📖 ReDoc estará disponível em: http://localhost:8000/redoc")
        print("🔌 API estará disponível em: http://localhost:8000")
        print("=" * 60)
        
        # Inicia o servidor
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Aplicação interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(start_app())
