"""
Aplicação principal FastAPI para API de Processamento de Exames Médicos.
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
    structlog.get_logger().info("Iniciando API de Processamento de Exames Médicos")
    yield
    structlog.get_logger().info("Encerrando API de Processamento de Exames Médicos")

# Criação da aplicação FastAPI
def create_app():
    """Cria a aplicação FastAPI simplificada."""
    return FastAPI(
        title="API de Processamento de Exames Médicos",
        version="2.0.0",
        description="API simplificada para processamento de exames médicos via OCR",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

# Instância da aplicação
app = create_app()

# Configuração de CORS simplificada
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Removido - não precisamos mais
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz da API simplificada."""
    return {
        "message": "API de Processamento de Exames Médicos",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da API."""
    try:
        return {
            "status": "healthy",
            "version": "2.0.0"
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

# APENAS router de exames (simplificado)
from src.api import exams
app.include_router(exams.router, prefix="/exams", tags=["exams"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=get_settings_lazy().debug,
        log_level=get_settings_lazy().log_level.lower()
    )
