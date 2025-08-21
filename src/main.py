"""
Aplicação principal FastAPI para API de Exames Médicos.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from contextlib import asynccontextmanager

from .core.config import get_settings_lazy
from .core.logging import setup_logging


# Configuração de logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle da aplicação."""
    # Startup
    structlog.get_logger().info("Iniciando API de Exames Médicos")
    
    # Validações de startup
    try:
        # Aqui podemos adicionar validações de conexão com Supabase
        # e outras dependências
        pass
    except Exception as e:
        structlog.get_logger().error(f"Erro na inicialização: {e}")
        raise
    
    yield
    
    # Shutdown
    structlog.get_logger().info("Encerrando API de Exames Médicos")


# Criação da aplicação FastAPI
def create_app():
    """Cria a aplicação FastAPI."""
    return FastAPI(
        title="API de Exames Médicos",
        version="1.0.0",
        description="API para processamento de exames médicos via OCR com LGPD compliance",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

# Instância da aplicação
app = create_app()

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar adequadamente para produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "API de Exames Médicos",
        "version": get_settings_lazy().app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da API."""
    try:
        # Aqui podemos adicionar verificações de saúde
        # como conexão com banco, storage, etc.
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": get_settings_lazy().app_version
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções não tratadas."""
    structlog.get_logger().error(
        "Exceção não tratada",
        error=str(exc),
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "error": str(exc) if get_settings_lazy().debug else "Erro interno"
        }
    )


# Importar e incluir routers
from api import exams
from api import auth
from api import patients

app.include_router(exams.router, prefix="/api/v1/exams", tags=["exams"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["patients"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=get_settings_lazy().debug,
        log_level=get_settings_lazy().log_level.lower()
    )
