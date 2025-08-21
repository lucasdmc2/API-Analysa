#!/usr/bin/env python3
"""
Script para testar o deploy no Railway.
"""

import json
import subprocess
import sys
from pathlib import Path

def test_railway_cli():
    """Testa se o Railway CLI está disponível."""
    print("🚂 Testando Railway CLI...")
    
    try:
        result = subprocess.run(
            ["railway", "--version"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Railway CLI disponível: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI não disponível")
            print("   Instale com: npm install -g @railway/cli")
            return False
            
    except FileNotFoundError:
        print("❌ Railway CLI não encontrado")
        print("   Instale com: npm install -g @railway/cli")
        return False

def test_railway_config():
    """Testa configuração do Railway."""
    print("\n📋 Testando configuração do Railway...")
    
    # Verifica railway.json
    railway_file = Path("railway.json")
    if not railway_file.exists():
        print("❌ railway.json não encontrado")
        return False
    
    try:
        with open(railway_file) as f:
            config = json.load(f)
        
        # Verifica campos obrigatórios
        required_fields = ["build", "deploy"]
        for field in required_fields:
            if field not in config:
                print(f"❌ Campo {field} ausente")
                return False
        
        print("✅ railway.json válido")
        
        # Verifica configuração de build
        build_config = config.get("build", {})
        if build_config.get("builder") == "DOCKERFILE":
            print("✅ Builder Dockerfile configurado")
        else:
            print("⚠️ Builder não é Dockerfile")
        
        # Verifica configuração de deploy
        deploy_config = config.get("deploy", {})
        if "startCommand" in deploy_config:
            print("✅ Comando de inicialização configurado")
        if "healthcheckPath" in deploy_config:
            print("✅ Healthcheck configurado")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ railway.json inválido: {e}")
        return False

def test_dockerfile():
    """Testa se o Dockerfile está configurado corretamente."""
    print("\n🐳 Testando Dockerfile...")
    
    dockerfile = Path("Dockerfile")
    if not dockerfile.exists():
        print("❌ Dockerfile não encontrado")
        return False
    
    try:
        with open(dockerfile) as f:
            content = f.read()
        
        # Verifica elementos essenciais
        checks = [
            ("FROM python", "Base image Python"),
            ("WORKDIR", "Diretório de trabalho"),
            ("COPY requirements.txt", "Cópia de requirements"),
            ("RUN pip install", "Instalação de dependências"),
            ("COPY src/", "Cópia do código fonte"),
            ("USER app", "Usuário não-root"),
            ("CMD", "Comando de execução")
        ]
        
        all_ok = True
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"❌ Erro ao ler Dockerfile: {e}")
        return False

def test_requirements():
    """Testa se requirements.txt está configurado."""
    print("\n📦 Testando requirements.txt...")
    
    requirements = Path("requirements.txt")
    if not requirements.exists():
        print("❌ requirements.txt não encontrado")
        return False
    
    try:
        with open(requirements) as f:
            lines = f.readlines()
        
        # Verifica dependências essenciais
        essential_deps = [
            "fastapi",
            "uvicorn",
            "supabase",
            "pytesseract",
            "pdf2image",
            "pydantic"
        ]
        
        content = "".join(lines)
        all_ok = True
        
        for dep in essential_deps:
            if dep in content:
                print(f"✅ {dep}")
            else:
                print(f"❌ {dep}")
                all_ok = False
        
        print(f"📊 Total de dependências: {len(lines)}")
        return all_ok
        
    except Exception as e:
        print(f"❌ Erro ao ler requirements.txt: {e}")
        return False

def test_environment_vars():
    """Testa variáveis de ambiente necessárias."""
    print("\n🔧 Testando variáveis de ambiente...")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SECRET_KEY"
    ]
    
    all_ok = True
    for var in required_vars:
        if var in Path("env.example").read_text():
            print(f"✅ {var} documentada")
        else:
            print(f"❌ {var} não documentada")
            all_ok = False
    
    return all_ok

def test_health_endpoint():
    """Testa se o endpoint de health está configurado."""
    print("\n🏥 Testando endpoint de health...")
    
    main_file = Path("src/main.py")
    if not main_file.exists():
        print("❌ main.py não encontrado")
        return False
    
    try:
        with open(main_file) as f:
            content = f.read()
        
        if "/health" in content and "health_check" in content:
            print("✅ Endpoint /health configurado")
            return True
        else:
            print("❌ Endpoint /health não configurado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao ler main.py: {e}")
        return False

def main():
    """Função principal."""
    print("🚀 Teste de Deploy no Railway")
    print("=" * 50)
    
    # Testa Railway CLI
    cli_ok = test_railway_cli()
    
    # Testa configuração
    config_ok = test_railway_config()
    
    # Testa Dockerfile
    dockerfile_ok = test_dockerfile()
    
    # Testa requirements
    requirements_ok = test_requirements()
    
    # Testa variáveis de ambiente
    env_ok = test_environment_vars()
    
    # Testa endpoint de health
    health_ok = test_health_endpoint()
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    print(f"🚂 Railway CLI: {'✅ OK' if cli_ok else '❌ FALHOU'}")
    print(f"📋 Configuração: {'✅ OK' if config_ok else '❌ FALHOU'}")
    print(f"🐳 Dockerfile: {'✅ OK' if dockerfile_ok else '❌ FALHOU'}")
    print(f"📦 Requirements: {'✅ OK' if requirements_ok else '❌ FALHOU'}")
    print(f"🔧 Variáveis de ambiente: {'✅ OK' if env_ok else '❌ FALHOU'}")
    print(f"🏥 Health endpoint: {'✅ OK' if health_ok else '❌ FALHOU'}")
    
    if all([config_ok, dockerfile_ok, requirements_ok, env_ok, health_ok]):
        print("\n🎉 Deploy no Railway está configurado perfeitamente!")
        print("   - Configuração válida")
        print("   - Dockerfile funcionando")
        print("   - Dependências configuradas")
        print("   - Variáveis de ambiente documentadas")
        print("   - Health check configurado")
        
        if cli_ok:
            print("\n🚀 Para fazer deploy:")
            print("   1. railway login")
            print("   2. railway init")
            print("   3. railway up")
        else:
            print("\n📋 Instale o Railway CLI:")
            print("   npm install -g @railway/cli")
        
        return 0
    else:
        print("\n⚠️ Há problemas na configuração do Railway.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
