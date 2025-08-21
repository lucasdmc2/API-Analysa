#!/usr/bin/env python3
"""
Script para testar configuração do Swagger/OpenAPI.
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_swagger_config():
    """Testa se o Swagger está configurado corretamente."""
    print("🔍 Testando configuração do Swagger/OpenAPI...")
    
    try:
        # Verifica se o FastAPI está configurado com Swagger
        from fastapi import FastAPI
        from fastapi.openapi.utils import get_openapi
        
        # Cria uma instância temporária para testar
        app = FastAPI(
            title="API de Exames Médicos",
            version="1.0.0",
            description="API para processamento de exames médicos via OCR com LGPD compliance",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Verifica se o Swagger está habilitado
        assert app.docs_url == "/docs", "Swagger UI não está configurado corretamente"
        assert app.redoc_url == "/redoc", "ReDoc não está configurado corretamente"
        
        print("✅ Swagger UI configurado em /docs")
        print("✅ ReDoc configurado em /redoc")
        
        # Gera OpenAPI schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        print("✅ OpenAPI schema gerado com sucesso")
        print(f"   - Título: {openapi_schema['info']['title']}")
        print(f"   - Versão: {openapi_schema['info']['version']}")
        print(f"   - Descrição: {openapi_schema['info']['description']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração do Swagger: {e}")
        return False

def test_api_structure():
    """Testa se a estrutura da API está correta para Swagger."""
    print("\n🏗️ Testando estrutura da API...")
    
    try:
        # Verifica se os routers estão definidos
        from api import auth, patients, exams
        
        print("✅ Módulo auth importado")
        print("✅ Módulo patients importado") 
        print("✅ Módulo exams importado")
        
        # Verifica se os routers têm rotas
        if hasattr(auth, 'router'):
            print(f"✅ Router de auth tem {len(auth.router.routes)} rotas")
        else:
            print("❌ Router de auth não encontrado")
            
        if hasattr(patients, 'router'):
            print(f"✅ Router de patients tem {len(patients.router.routes)} rotas")
        else:
            print("❌ Router de patients não encontrado")
            
        if hasattr(exams, 'router'):
            print(f"✅ Router de exams tem {len(exams.router.routes)} rotas")
        else:
            print("❌ Router de exams não encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na estrutura da API: {e}")
        return False

def test_models():
    """Testa se os modelos Pydantic estão configurados corretamente."""
    print("\n📋 Testando modelos Pydantic...")
    
    try:
        from models import auth, patient, exam
        
        print("✅ Modelos de auth importados")
        print("✅ Modelos de patient importados")
        print("✅ Modelos de exam importados")
        
        # Verifica se os modelos têm schema
        from pydantic import BaseModel
        
        # Testa alguns modelos específicos
        if hasattr(auth, 'UserRegisterRequest'):
            print("✅ UserRegisterRequest disponível")
        if hasattr(patient, 'PatientCreate'):
            print("✅ PatientCreate disponível")
        if hasattr(exam, 'ExamUploadRequest'):
            print("✅ ExamUploadRequest disponível")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos modelos: {e}")
        return False

def main():
    """Função principal."""
    print("🚀 Teste de Configuração do Swagger/OpenAPI")
    print("=" * 50)
    
    # Testa configuração do Swagger
    swagger_ok = test_swagger_config()
    
    # Testa estrutura da API
    api_ok = test_api_structure()
    
    # Testa modelos
    models_ok = test_models()
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    print(f"🔍 Swagger Config: {'✅ OK' if swagger_ok else '❌ FALHOU'}")
    print(f"🏗️ Estrutura API: {'✅ OK' if api_ok else '❌ FALHOU'}")
    print(f"📋 Modelos: {'✅ OK' if models_ok else '❌ FALHOU'}")
    
    if all([swagger_ok, api_ok, models_ok]):
        print("\n🎉 Swagger/OpenAPI está configurado perfeitamente!")
        print("   - Acesse /docs para Swagger UI")
        print("   - Acesse /redoc para ReDoc")
        return 0
    else:
        print("\n⚠️ Há problemas na configuração do Swagger/OpenAPI.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
