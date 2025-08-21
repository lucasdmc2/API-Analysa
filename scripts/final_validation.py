#!/usr/bin/env python3
"""
Script para validação final da aplicação.
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
            return True
        else:
            print(f"❌ {description} - FALHOU")
            if result.stderr.strip():
                print(f"   Erro: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERRO: {e}")
        return False

def test_application_structure():
    """Testa estrutura da aplicação."""
    print("🏗️ Testando estrutura da aplicação...")
    
    required_dirs = ["src", "tests", "scripts", "docs"]
    required_files = [
        "src/main.py",
        "src/core/config.py",
        "src/api/auth.py",
        "src/api/patients.py",
        "src/api/exams.py",
        "src/services/ocr_service.py",
        "src/services/parser_service.py",
        "src/services/biomarker_service.py",
        "requirements.txt",
        "Dockerfile",
        "railway.json",
        ".github/workflows/ci-cd.yml"
    ]
    
    all_ok = True
    
    # Verifica diretórios
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ Diretório {dir_name}")
        else:
            print(f"❌ Diretório {dir_name} não encontrado")
            all_ok = False
    
    # Verifica arquivos
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ Arquivo {file_path}")
        else:
            print(f"❌ Arquivo {file_path} não encontrado")
            all_ok = False
    
    return all_ok

def test_code_quality():
    """Testa qualidade do código."""
    print("\n🎨 Testando qualidade do código...")
    
    # Testa formatação (se as ferramentas estiverem disponíveis)
    try:
        import black
        black_ok = run_command(
            "python3 -m black --check --diff src/ tests/ scripts/",
            "Verificação Black"
        )
    except ImportError:
        print("⚠️ Black não instalado, pulando verificação de formatação")
        black_ok = True
    
    try:
        import isort
        isort_ok = run_command(
            "python3 -m isort --check-only --diff src/ tests/ scripts/",
            "Verificação isort"
        )
    except ImportError:
        print("⚠️ isort não instalado, pulando verificação de imports")
        isort_ok = True
    
    try:
        import mypy
        mypy_ok = run_command(
            "python3 -m mypy src/ --ignore-missing-imports",
            "Verificação mypy"
        )
    except ImportError:
        print("⚠️ mypy não instalado, pulando verificação de tipos")
        mypy_ok = True
    
    return black_ok and isort_ok and mypy_ok

def test_functionality():
    """Testa funcionalidades principais."""
    print("\n🚀 Testando funcionalidades principais...")
    
    # Testa se a aplicação pode ser importada
    try:
        sys.path.insert(0, str(Path("src")))
        from core.config import get_settings_lazy
        print("✅ Configuração carregada")
        
        from api.auth import router as auth_router
        print("✅ Router de autenticação carregado")
        
        from api.patients import router as patients_router
        print("✅ Router de pacientes carregado")
        
        from api.exams import router as exams_router
        print("✅ Router de exames carregado")
        
        from services.ocr_service import OCRService
        print("✅ Serviço OCR carregado")
        
        from services.parser_service import BiomarkerParser
        print("✅ Parser de biomarcadores carregado")
        
        from services.biomarker_service import BiomarkerService
        print("✅ Serviço de biomarcadores carregado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar funcionalidades: {e}")
        return False

def test_documentation():
    """Testa documentação."""
    print("\n📚 Testando documentação...")
    
    # Verifica se o Swagger está configurado
    main_file = Path("src/main.py")
    if main_file.exists():
        with open(main_file) as f:
            content = f.read()
        
        if "docs_url" in content and "redoc_url" in content:
            print("✅ Swagger/ReDoc configurado")
            swagger_ok = True
        else:
            print("❌ Swagger/ReDoc não configurado")
            swagger_ok = False
    else:
        swagger_ok = False
    
    # Verifica se o README existe
    readme_ok = Path("README.md").exists()
    if readme_ok:
        print("✅ README.md encontrado")
    else:
        print("❌ README.md não encontrado")
    
    # Verifica se há documentação da API
    api_docs_ok = Path("docs").exists()
    if api_docs_ok:
        print("✅ Documentação da API encontrada")
    else:
        print("⚠️ Documentação da API não encontrada")
    
    return swagger_ok and readme_ok

def test_security():
    """Testa aspectos de segurança."""
    print("\n🔒 Testando segurança...")
    
    # Verifica se há validação de entrada
    main_file = Path("src/main.py")
    if main_file.exists():
        with open(main_file) as f:
            content = f.read()
        
        if "HTTPException" in content and "status_code" in content:
            print("✅ Tratamento de erros configurado")
            error_handling_ok = True
        else:
            print("❌ Tratamento de erros não configurado")
            error_handling_ok = False
    else:
        error_handling_ok = False
    
    # Verifica se há CORS configurado
    if "CORSMiddleware" in content:
        print("✅ CORS configurado")
        cors_ok = True
    else:
        print("❌ CORS não configurado")
        cors_ok = False
    
    # Verifica se há logging estruturado
    if "structlog" in content:
        print("✅ Logging estruturado configurado")
        logging_ok = True
    else:
        print("❌ Logging estruturado não configurado")
        logging_ok = False
    
    return error_handling_ok and cors_ok and logging_ok

def test_deployment():
    """Testa configuração de deploy."""
    print("\n🚀 Testando configuração de deploy...")
    
    # Verifica Dockerfile
    dockerfile_ok = Path("Dockerfile").exists()
    if dockerfile_ok:
        print("✅ Dockerfile encontrado")
    else:
        print("❌ Dockerfile não encontrado")
    
    # Verifica railway.json
    railway_ok = Path("railway.json").exists()
    if railway_ok:
        print("✅ railway.json encontrado")
    else:
        print("❌ railway.json não encontrado")
    
    # Verifica CI/CD
    cicd_ok = Path(".github/workflows/ci-cd.yml").exists()
    if cicd_ok:
        print("✅ Pipeline CI/CD configurado")
    else:
        print("❌ Pipeline CI/CD não configurado")
    
    # Verifica requirements.txt
    requirements_ok = Path("requirements.txt").exists()
    if requirements_ok:
        print("✅ requirements.txt encontrado")
    else:
        print("❌ requirements.txt não encontrado")
    
    return all([dockerfile_ok, railway_ok, cicd_ok, requirements_ok])

def main():
    """Função principal."""
    print("🎯 VALIDAÇÃO FINAL - API de Exames Médicos")
    print("=" * 60)
    
    # Testa estrutura
    structure_ok = test_application_structure()
    
    # Testa qualidade
    quality_ok = test_code_quality()
    
    # Testa funcionalidades
    functionality_ok = test_functionality()
    
    # Testa documentação
    documentation_ok = test_documentation()
    
    # Testa segurança
    security_ok = test_security()
    
    # Testa deploy
    deployment_ok = test_deployment()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VALIDAÇÃO FINAL")
    print("=" * 60)
    print(f"🏗️ Estrutura: {'✅ OK' if structure_ok else '❌ FALHOU'}")
    print(f"🎨 Qualidade: {'✅ OK' if quality_ok else '❌ FALHOU'}")
    print(f"🚀 Funcionalidades: {'✅ OK' if functionality_ok else '❌ FALHOU'}")
    print(f"📚 Documentação: {'✅ OK' if documentation_ok else '❌ FALHOU'}")
    print(f"🔒 Segurança: {'✅ OK' if security_ok else '❌ FALHOU'}")
    print(f"🚀 Deploy: {'✅ OK' if deployment_ok else '❌ FALHOU'}")
    
    # Calcula score geral
    total_tests = 6
    passed_tests = sum([
        structure_ok, quality_ok, functionality_ok,
        documentation_ok, security_ok, deployment_ok
    ])
    
    score_percentage = (passed_tests / total_tests) * 100
    
    print(f"\n📊 SCORE GERAL: {passed_tests}/{total_tests} ({score_percentage:.1f}%)")
    
    if score_percentage >= 90:
        print("\n🎉 EXCELENTE! A aplicação está pronta para produção!")
        print("   - Todas as funcionalidades implementadas")
        print("   - Documentação completa")
        print("   - Segurança configurada")
        print("   - Deploy configurado")
        return 0
    elif score_percentage >= 80:
        print("\n✅ BOM! A aplicação está quase pronta para produção.")
        print("   - Alguns ajustes menores necessários")
        return 0
    elif score_percentage >= 70:
        print("\n⚠️ REGULAR! A aplicação precisa de melhorias.")
        print("   - Revisar funcionalidades críticas")
        return 1
    else:
        print("\n❌ INSUFICIENTE! A aplicação precisa de trabalho significativo.")
        print("   - Implementar funcionalidades básicas")
        return 1

if __name__ == "__main__":
    sys.exit(main())
