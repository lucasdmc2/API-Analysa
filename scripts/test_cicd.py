#!/usr/bin/env python3
"""
Script para testar o pipeline de CI/CD localmente.
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Executa um comando e retorna o resultado."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCESSO")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FALHOU")
            if result.stderr.strip():
                print(f"   Erro: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERRO: {e}")
        return False

def test_code_formatting():
    """Testa formatação de código."""
    print("\n🎨 Testando formatação de código...")
    
    # Testa Black
    black_ok = run_command(
        "python3 -m black --check --diff src/ tests/ scripts/",
        "Verificação Black (formatação)"
    )
    
    # Testa isort
    isort_ok = run_command(
        "python3 -m isort --check-only --diff src/ tests/ scripts/",
        "Verificação isort (imports)"
    )
    
    return black_ok and isort_ok

def test_type_checking():
    """Testa verificação de tipos."""
    print("\n🔍 Testando verificação de tipos...")
    
    # Testa mypy
    mypy_ok = run_command(
        "python3 -m mypy src/ --ignore-missing-imports",
        "Verificação mypy (tipos)"
    )
    
    return mypy_ok

def test_security():
    """Testa análise de segurança."""
    print("\n🔒 Testando análise de segurança...")
    
    # Testa bandit se disponível
    try:
        import bandit
        bandit_ok = run_command(
            "python3 -m bandit -r src/ -f json -o bandit-report.json",
            "Análise Bandit (segurança)"
        )
    except ImportError:
        print("⚠️ Bandit não instalado, pulando análise de segurança")
        bandit_ok = True
    
    # Testa safety se disponível
    try:
        import safety
        safety_ok = run_command(
            "python3 -m safety check --json --output safety-report.json",
            "Verificação Safety (vulnerabilidades)"
        )
    except ImportError:
        print("⚠️ Safety não instalado, pulando verificação de vulnerabilidades")
        safety_ok = True
    
    return bandit_ok and safety_ok

def test_build():
    """Testa build da aplicação."""
    print("\n🏗️ Testando build da aplicação...")
    
    # Testa se o Dockerfile existe
    dockerfile_exists = Path("Dockerfile").exists()
    if dockerfile_exists:
        print("✅ Dockerfile encontrado")
        
        # Testa build Docker
        build_ok = run_command(
            "docker build -t api-exames-medicos:test .",
            "Build Docker"
        )
        
        if build_ok:
            # Testa se a imagem funciona
            test_ok = run_command(
                "docker run --rm api-exames-medicos:test python -c 'print(\"✅ Imagem Docker funcionando\")'",
                "Teste da imagem Docker"
            )
            
            # Limpa imagem de teste
            cleanup_ok = run_command(
                "docker rmi api-exames-medicos:test",
                "Limpeza da imagem de teste"
            )
            
            return build_ok and test_ok and cleanup_ok
        else:
            return False
    else:
        print("❌ Dockerfile não encontrado")
        return False

def test_railway_config():
    """Testa configuração do Railway."""
    print("\n🚂 Testando configuração do Railway...")
    
    # Verifica se railway.json existe
    railway_config = Path("railway.json")
    if railway_config.exists():
        print("✅ railway.json encontrado")
        
        # Verifica se é JSON válido
        try:
            import json
            with open(railway_config) as f:
                config = json.load(f)
            
            # Verifica campos obrigatórios
            required_fields = ["build", "deploy"]
            for field in required_fields:
                if field in config:
                    print(f"✅ Campo {field} presente")
                else:
                    print(f"❌ Campo {field} ausente")
                    return False
            
            print("✅ Configuração Railway válida")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ railway.json inválido: {e}")
            return False
    else:
        print("❌ railway.json não encontrado")
        return False

def main():
    """Função principal."""
    print("🚀 Teste do Pipeline de CI/CD")
    print("=" * 50)
    
    # Testa formatação
    formatting_ok = test_code_formatting()
    
    # Testa tipos
    types_ok = test_type_checking()
    
    # Testa segurança
    security_ok = test_security()
    
    # Testa build
    build_ok = test_build()
    
    # Testa Railway
    railway_ok = test_railway_config()
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    print(f"🎨 Formatação: {'✅ OK' if formatting_ok else '❌ FALHOU'}")
    print(f"🔍 Tipos: {'✅ OK' if types_ok else '❌ FALHOU'}")
    print(f"🔒 Segurança: {'✅ OK' if security_ok else '❌ FALHOU'}")
    print(f"🏗️ Build: {'✅ OK' if build_ok else '❌ FALHOU'}")
    print(f"🚂 Railway: {'✅ OK' if railway_ok else '❌ FALHOU'}")
    
    if all([formatting_ok, types_ok, security_ok, build_ok, railway_ok]):
        print("\n🎉 Pipeline de CI/CD está funcionando perfeitamente!")
        print("   - Código formatado e validado")
        print("   - Build Docker funcionando")
        print("   - Configuração Railway válida")
        return 0
    else:
        print("\n⚠️ Há problemas no pipeline de CI/CD.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
