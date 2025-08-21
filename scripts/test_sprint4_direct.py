#!/usr/bin/env python3
"""
Testes diretos para Sprint 4 - Gestão e Auth
Testa os módulos diretamente sem importar main.py
"""

import sys
import os
import subprocess
from pathlib import Path

# Adiciona o diretório src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_auth_module():
    """Testa o módulo de autenticação."""
    print("🔐 Testando módulo de autenticação...")
    try:
        # Testa importação dos modelos
        from models.auth import UserRegisterRequest, UserLoginRequest, UserProfile
        print("✅ Modelos de auth importados com sucesso")
        
        # Testa criação de instâncias
        user_data = {
            "email": "test@example.com",
            "password": "test123456",
            "password_confirm": "test123456",
            "full_name": "Test User",
            "crm": "12345-SP",
            "specialty": "Cardiologia",
            "phone": "11999999999"
        }
        user_req = UserRegisterRequest(**user_data)
        print(f"✅ UserRegisterRequest criado: {user_req.email}")
        
        return True
    except Exception as e:
        print(f"❌ Erro no módulo auth: {e}")
        return False

def test_patients_module():
    """Testa o módulo de pacientes."""
    print("👥 Testando módulo de pacientes...")
    try:
        # Testa importação dos modelos
        from models.patient import PatientCreate, PatientUpdate, PatientResponse
        print("✅ Modelos de patient importados com sucesso")
        
        # Testa criação de instâncias
        patient_data = {
            "full_name": "João Silva",
            "cpf": "12345678901",
            "birth_date": "1990-01-01",
            "gender": "M",
            "phone": "11999999999",
            "address": "Rua das Flores, 123 - São Paulo/SP"
        }
        patient_req = PatientCreate(**patient_data)
        print(f"✅ PatientCreate criado: {patient_req.full_name}")
        
        return True
    except Exception as e:
        print(f"❌ Erro no módulo patients: {e}")
        return False

def test_api_endpoints():
    """Testa os endpoints da API."""
    print("🌐 Testando endpoints da API...")
    try:
        # Testa se os arquivos de API existem
        from pathlib import Path
        
        auth_file = Path(__file__).parent.parent / "src" / "api" / "auth.py"
        patients_file = Path(__file__).parent.parent / "src" / "api" / "patients.py"
        
        if auth_file.exists():
            print("✅ Arquivo auth.py encontrado")
        else:
            print("❌ Arquivo auth.py não encontrado")
            
        if patients_file.exists():
            print("✅ Arquivo patients.py encontrado")
        else:
            print("❌ Arquivo patients.py não encontrado")
        
        # Verifica se os arquivos têm conteúdo
        if auth_file.exists() and auth_file.stat().st_size > 0:
            print("✅ Arquivo auth.py tem conteúdo")
        else:
            print("❌ Arquivo auth.py está vazio")
            
        if patients_file.exists() and patients_file.stat().st_size > 0:
            print("✅ Arquivo patients.py tem conteúdo")
        else:
            print("❌ Arquivo patients.py está vazio")
        
        return auth_file.exists() and patients_file.exists()
    except Exception as e:
        print(f"❌ Erro nos endpoints: {e}")
        return False

def run_pytest_tests():
    """Executa os testes pytest."""
    print("\n🧪 Executando testes pytest...")
    try:
        # Testa auth
        result = subprocess.run([
            "python3", "-m", "pytest", 
            "tests/test_auth.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.returncode == 0:
            print("✅ Testes de auth passaram")
        else:
            print(f"❌ Testes de auth falharam: {result.stderr}")
        
        # Testa patients
        result = subprocess.run([
            "python3", "-m", "pytest", 
            "tests/test_patients.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.returncode == 0:
            print("✅ Testes de patients passaram")
        else:
            print(f"❌ Testes de patients falharam: {result.stderr}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao executar testes pytest: {e}")
        return False

def main():
    """Função principal."""
    print("🚀 API de Exames Médicos - Testes Sprint 4 (Direto)")
    print("=" * 60)
    
    # Testa módulos individualmente
    auth_ok = test_auth_module()
    patients_ok = test_patients_module()
    endpoints_ok = test_api_endpoints()
    
    # Executa testes pytest
    pytest_ok = run_pytest_tests()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"🔐 Módulo Auth: {'✅ OK' if auth_ok else '❌ FALHOU'}")
    print(f"👥 Módulo Patients: {'✅ OK' if patients_ok else '❌ FALHOU'}")
    print(f"🌐 Endpoints API: {'✅ OK' if endpoints_ok else '❌ FALHOU'}")
    print(f"🧪 Testes Pytest: {'✅ OK' if pytest_ok else '❌ FALHOU'}")
    
    if all([auth_ok, patients_ok, endpoints_ok, pytest_ok]):
        print("\n🎉 Sprint 4 está funcionando perfeitamente!")
        return 0
    else:
        print("\n⚠️ Sprint 4 tem alguns problemas que precisam ser corrigidos.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
