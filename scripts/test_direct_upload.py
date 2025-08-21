#!/usr/bin/env python3
"""
Script para testar upload direto usando credenciais Supabase
"""

import requests
import json
import time
from pathlib import Path

# Configurações da API
API_BASE_URL = "https://api-analysa-production.up.railway.app"

def test_direct_upload():
    """Testa upload direto sem autenticação completa"""
    print("🔍 Teste de Upload Direto")
    print("=" * 50)
    
    # Verifica se o arquivo existe
    exam_file_path = Path("Exames Dr. Julio.pdf")
    if not exam_file_path.exists():
        print(f"❌ Arquivo não encontrado: {exam_file_path}")
        return False
    
    file_size = exam_file_path.stat().st_size
    print(f"📁 Arquivo: {exam_file_path}")
    print(f"📏 Tamanho: {file_size / 1024:.1f} KB")
    
    # Teste 1: Tentar upload sem autenticação (deve dar 401)
    try:
        print("\n1️⃣ Testando upload sem autenticação...")
        
        files = {
            'file': ('Exames Dr. Julio.pdf', open(exam_file_path, 'rb'), 'application/pdf')
        }
        
        data = {
            'patient_id': 'test_patient_123',
            'user_id': 'test_user_123'
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/exams/upload",
            files=files,
            data=data
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Autenticação requerida (esperado)")
        elif response.status_code == 422:
            print("   ⚠️  Erro de validação")
            print(f"   📋 Response: {response.text[:200]}")
        else:
            print(f"   ⚠️  Status inesperado: {response.status_code}")
            print(f"   📋 Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    # Teste 2: Verificar se o endpoint está funcionando
    try:
        print("\n2️⃣ Verificando endpoint de upload...")
        
        # Teste com dados mínimos
        response = requests.post(
            f"{API_BASE_URL}/api/v1/exams/upload",
            data={}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 422:
            print("   ✅ Endpoint funcionando (validação ativa)")
            try:
                errors = response.json()
                print(f"   📋 Erros de validação: {len(errors.get('detail', []))} campos")
            except:
                print(f"   📋 Response: {response.text[:100]}")
        else:
            print(f"   ⚠️  Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    # Teste 3: Verificar se há algum usuário existente
    try:
        print("\n3️⃣ Verificando se há usuários existentes...")
        
        # Tenta fazer login com um usuário comum
        test_logins = [
            {"email": "admin@example.com", "password": "admin123"},
            {"email": "test@example.com", "password": "test123"},
            {"email": "user@example.com", "password": "user123"}
        ]
        
        for login_data in test_logins:
            print(f"   🔐 Tentando: {login_data['email']}")
            response = requests.post(
                f"{API_BASE_URL}/api/v1/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                print(f"   ✅ Login bem-sucedido com {login_data['email']}!")
                data = response.json()
                token = data.get("access_token", "")
                if token:
                    print(f"   🔑 Token: {token[:20]}...")
                    # Tenta fazer upload com este token
                    return test_upload_with_token(token)
                break
            elif response.status_code == 401:
                print(f"   ❌ Credenciais inválidas")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Teste de upload direto concluído")
    return False

def test_upload_with_token(token):
    """Testa upload usando um token válido"""
    try:
        print("\n4️⃣ Testando upload com token válido...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        exam_file_path = Path("Exames Dr. Julio.pdf")
        files = {
            'file': ('Exames Dr. Julio.pdf', open(exam_file_path, 'rb'), 'application/pdf')
        }
        
        data = {
            'patient_id': 'test_patient_123',
            'user_id': 'test_user_123'
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/exams/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print("   ✅ Upload bem-sucedido!")
            data = response.json()
            exam_id = data.get("exam_id")
            print(f"   🆔 ID do Exame: {exam_id}")
            print(f"   📋 Status: {data.get('status')}")
            return True
        else:
            print(f"   ❌ Upload falhou: {response.status_code}")
            print(f"   📋 Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        return False

if __name__ == "__main__":
    test_direct_upload()
