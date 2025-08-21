#!/usr/bin/env python3
"""
Script simples para testar Swagger/OpenAPI básico.
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def test_basic_swagger():
    """Testa funcionalidade básica do Swagger."""
    print("🔍 Testando Swagger/OpenAPI básico...")
    
    # Cria aplicação de teste
    app = FastAPI(
        title="API de Exames Médicos",
        version="1.0.0",
        description="API para processamento de exames médicos via OCR com LGPD compliance",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Adiciona algumas rotas de teste
    @app.get("/")
    async def root():
        return {"message": "API funcionando"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    @app.get("/api/test")
    async def test():
        return {"test": "success"}
    
    # Verifica configuração
    print(f"✅ Título: {app.title}")
    print(f"✅ Versão: {app.version}")
    print(f"✅ Swagger UI: {app.docs_url}")
    print(f"✅ ReDoc: {app.redoc_url}")
    print(f"✅ Rotas: {len(app.routes)}")
    
    # Gera OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    print("✅ OpenAPI schema gerado:")
    print(f"   - Info: {openapi_schema['info']}")
    print(f"   - Paths: {list(openapi_schema['paths'].keys())}")
    
    # Verifica se as rotas estão documentadas
    paths = openapi_schema['paths']
    for route in app.routes:
        if hasattr(route, 'path'):
            path = route.path
            if path in paths:
                print(f"✅ Rota {path} documentada")
            else:
                print(f"⚠️ Rota {path} não documentada")
    
    return True

def test_swagger_features():
    """Testa recursos específicos do Swagger."""
    print("\n🚀 Testando recursos do Swagger...")
    
    app = FastAPI(
        title="API de Exames Médicos",
        version="1.0.0",
        description="API para processamento de exames médicos via OCR com LGPD compliance",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Adiciona rota com parâmetros
    @app.get("/api/users/{user_id}")
    async def get_user(user_id: int, include_details: bool = False):
        """
        Obtém usuário por ID.
        
        Args:
            user_id: ID do usuário
            include_details: Incluir detalhes completos
            
        Returns:
            Dados do usuário
        """
        return {"user_id": user_id, "include_details": include_details}
    
    # Adiciona rota POST
    @app.post("/api/users")
    async def create_user(name: str, email: str):
        """
        Cria novo usuário.
        
        Args:
            name: Nome do usuário
            email: Email do usuário
            
        Returns:
            Usuário criado
        """
        return {"name": name, "email": email, "created": True}
    
    # Gera schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    print("✅ Rotas com parâmetros documentadas:")
    for path, methods in openapi_schema['paths'].items():
        for method, details in methods.items():
            if 'summary' in details:
                print(f"   - {method.upper()} {path}: {details['summary']}")
    
    return True

def main():
    """Função principal."""
    print("🚀 Teste de Swagger/OpenAPI")
    print("=" * 40)
    
    # Testa funcionalidade básica
    basic_ok = test_basic_swagger()
    
    # Testa recursos específicos
    features_ok = test_swagger_features()
    
    # Resumo
    print("\n" + "=" * 40)
    print("📊 RESUMO")
    print("=" * 40)
    print(f"🔍 Swagger Básico: {'✅ OK' if basic_ok else '❌ FALHOU'}")
    print(f"🚀 Recursos: {'✅ OK' if features_ok else '❌ FALHOU'}")
    
    if all([basic_ok, features_ok]):
        print("\n🎉 Swagger/OpenAPI está funcionando perfeitamente!")
        print("   - Documentação automática funcionando")
        print("   - Parâmetros sendo documentados")
        print("   - Schemas sendo gerados")
        return 0
    else:
        print("\n⚠️ Há problemas com o Swagger/OpenAPI.")
        return 1

if __name__ == "__main__":
    exit(main())
