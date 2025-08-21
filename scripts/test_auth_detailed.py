#!/usr/bin/env python3
"""
Script para testar detalhadamente o endpoint de autenticação
"""

import requests
import json
import time

# Configurações da API
API_BASE_URL = "https://api-analysa-production.up.railway.app"

def test_auth_detailed():
    """Testa detalhadamente o endpoint de autenticação"""
    print("🔍 Teste Detalhado de Autenticação")
    print("=" * 50)
    
    # Teste 1: Dados válidos
    try:
        print("1️⃣ Testando registro com dados válidos...")
        timestamp = int(time.time())
        test_user = {
            "email": f"test_exam_{timestamp}@example.com",
            "password": "TestExam123!",
            "password_confirm": "TestExam123!",
            "full_name": "Dr. Teste Exames",
            "crm": f"TEST{timestamp}",
            "specialty": "Clínico Geral",
            "phone": "+5511999999999"
        }
        
        print(f"   📧 Email: {test_user['email']}")
        print(f"   🆔 CRM: {test_user['crm']}")
        
        response = requests.post(f"{API_BASE_URL}/api/v1/auth/register", json=test_user)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 201:
            print("   ✅ Registro bem-sucedido!")
            data = response.json()
            print(f"   🆔 User ID: {data.get('user_id', 'N/A')}")
        elif response.status_code == 422:
            print("   ⚠️  Erro de validação (esperado para teste)")
            try:
                errors = response.json()
                print(f"   📋 Detalhes: {json.dumps(errors, indent=2)}")
            except:
                print(f"   📋 Detalhes: {response.text}")
        elif response.status_code == 500:
            print("   ❌ Erro interno do servidor")
            print(f"   📋 Detalhes: {response.text}")
        else:
            print(f"   ⚠️  Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    # Teste 2: Dados inválidos (sem campos obrigatórios)
    try:
        print("\n2️⃣ Testando registro com dados inválidos...")
        invalid_user = {
            "email": "invalid@example.com"
        }
        
        response = requests.post(f"{API_BASE_URL}/api/v1/auth/register", json=invalid_user)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 422:
            print("   ✅ Validação funcionando (esperado)")
            try:
                errors = response.json()
                print(f"   📋 Erros: {json.dumps(errors, indent=2)}")
            except:
                print(f"   📋 Erros: {response.text}")
        else:
            print(f"   ⚠️  Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    # Teste 3: Verificar se o usuário foi criado
    try:
        print("\n3️⃣ Testando login com usuário criado...")
        if 'test_user' in locals():
            login_data = {
                "email": test_user["email"],
                "password": test_user["password"]
            }
            
            response = requests.post(f"{API_BASE_URL}/api/v1/auth/login", json=login_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Login bem-sucedido!")
                data = response.json()
                token = data.get("access_token", "")
                if token:
                    print(f"   🔑 Token obtido: {token[:20]}...")
                else:
                    print("   ⚠️  Token não encontrado na resposta")
            else:
                print(f"   ❌ Login falhou: {response.status_code}")
                print(f"   📋 Response: {response.text[:200]}")
                
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Teste de autenticação detalhado concluído")

if __name__ == "__main__":
    test_auth_detailed()
