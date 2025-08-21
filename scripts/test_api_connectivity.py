#!/usr/bin/env python3
"""
Script para testar conectividade básica da API Analysa
"""

import requests
import json

# Configurações da API
API_BASE_URL = "https://api-analysa-production.up.railway.app"

def test_api_connectivity():
    """Testa conectividade básica da API"""
    print("🔍 Testando conectividade da API Analysa")
    print("=" * 50)
    
    # Teste 1: Health check básico
    try:
        print("1️⃣ Testando endpoint raiz...")
        response = requests.get(f"{API_BASE_URL}/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API respondendo")
        else:
            print(f"   ⚠️  Resposta inesperada: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    # Teste 2: Documentação Swagger
    try:
        print("\n2️⃣ Testando documentação Swagger...")
        response = requests.get(f"{API_BASE_URL}/docs")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Swagger disponível")
        else:
            print(f"   ⚠️  Swagger não disponível: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    # Teste 3: OpenAPI spec
    try:
        print("\n3️⃣ Testando OpenAPI spec...")
        response = requests.get(f"{API_BASE_URL}/openapi.json")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ OpenAPI spec disponível")
            # Verifica endpoints disponíveis
            try:
                spec = response.json()
                paths = spec.get("paths", {})
                print(f"   📋 Endpoints disponíveis: {len(paths)}")
                for path in list(paths.keys())[:10]:  # Mostra os primeiros 10
                    print(f"      - {path}")
                if len(paths) > 10:
                    print(f"      ... e mais {len(paths) - 10} endpoints")
            except:
                print("   ⚠️  Não foi possível parsear o spec")
        else:
            print(f"   ⚠️  OpenAPI spec não disponível: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    # Teste 4: Endpoint de auth register
    try:
        print("\n4️⃣ Testando endpoint de registro...")
        response = requests.post(f"{API_BASE_URL}/api/v1/auth/register", json={})
        print(f"   Status: {response.status_code}")
        if response.status_code in [422, 400]:  # 422 = Validation Error (endpoint existe)
            print("   ✅ Endpoint de registro disponível")
        else:
            print(f"   ⚠️  Endpoint de registro não disponível: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    # Teste 5: Endpoint de upload de exames
    try:
        print("\n5️⃣ Testando endpoint de upload de exames...")
        response = requests.post(f"{API_BASE_URL}/api/v1/exams/upload", data={})
        print(f"   Status: {response.status_code}")
        if response.status_code in [422, 400, 401]:  # 422 = Validation Error (endpoint existe)
            print("   ✅ Endpoint de upload disponível")
        else:
            print(f"   ⚠️  Endpoint de upload não disponível: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Teste de conectividade concluído")

if __name__ == "__main__":
    test_api_connectivity()
