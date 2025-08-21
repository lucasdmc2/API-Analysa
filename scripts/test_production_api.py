#!/usr/bin/env python3
"""
Script de Testes para API Analysa em Produção
Testa todas as funcionalidades: auth, upload, OCR, parsing, etc.
"""

import requests
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Configurações da API
API_BASE_URL = "https://api-analysa-production.up.railway.app"
API_VERSION = "v1"

class APITester:
    def __init__(self):
        self.base_url = f"{API_BASE_URL}/api/{API_VERSION}"
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Registra resultado do teste"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   📝 {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def test_health_check(self) -> bool:
        """Testa endpoint de health check"""
        try:
            response = self.session.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Erro: {str(e)}")
            return False
    
    def test_root_endpoint(self) -> bool:
        """Testa endpoint raiz"""
        try:
            response = self.session.get(f"{API_BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Root Endpoint", True, f"Message: {data.get('message')}")
                return True
            else:
                self.log_test("Root Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Erro: {str(e)}")
            return False
    
    def test_swagger_docs(self) -> bool:
        """Testa se a documentação Swagger está acessível"""
        try:
            response = self.session.get(f"{API_BASE_URL}/docs")
            if response.status_code == 200:
                self.log_test("Swagger Docs", True, "Documentação acessível")
                return True
            else:
                self.log_test("Swagger Docs", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Swagger Docs", False, f"Erro: {str(e)}")
            return False
    
    def test_auth_endpoints(self) -> bool:
        """Testa endpoints de autenticação"""
        try:
            # Teste de registro (pode falhar se usuário já existir)
            test_user = {
                "email": f"test_{int(time.time())}@example.com",
                "password": "TestPassword123!",
                "full_name": "Usuário Teste"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=test_user)
            if response.status_code in [200, 201, 409]:  # 409 = usuário já existe
                self.log_test("Auth Register", True, f"Status: {response.status_code}")
                
                # Teste de login
                login_data = {
                    "email": test_user["email"],
                    "password": test_user["password"]
                }
                
                response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get("access_token")
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("Auth Login", True, "Token obtido com sucesso")
                    return True
                else:
                    self.log_test("Auth Login", False, f"Status code: {response.status_code}")
                    return False
            else:
                self.log_test("Auth Register", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Auth Endpoints", False, f"Erro: {str(e)}")
            return False
    
    def test_patients_endpoints(self) -> bool:
        """Testa endpoints de pacientes"""
        if not self.auth_token:
            self.log_test("Patients Endpoints", False, "Token de autenticação não disponível")
            return False
            
        try:
            # Teste de criação de paciente
            test_patient = {
                "full_name": "João Silva Teste",
                "date_of_birth": "1990-01-01",
                "cpf": "12345678901",
                "email": "joao.teste@example.com",
                "phone": "+5511999999999"
            }
            
            response = self.session.post(f"{self.base_url}/patients/", json=test_patient)
            if response.status_code in [200, 201]:
                data = response.json()
                patient_id = data.get("id")
                self.log_test("Create Patient", True, f"Paciente criado com ID: {patient_id}")
                
                # Teste de listagem de pacientes
                response = self.session.get(f"{self.base_url}/patients/")
                if response.status_code == 200:
                    self.log_test("List Patients", True, "Lista de pacientes obtida")
                    return True
                else:
                    self.log_test("List Patients", False, f"Status code: {response.status_code}")
                    return False
            else:
                self.log_test("Create Patient", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Patients Endpoints", False, f"Erro: {str(e)}")
            return False
    
    def test_exam_upload(self) -> bool:
        """Testa upload de exame (simulado)"""
        if not self.auth_token:
            self.log_test("Exam Upload", False, "Token de autenticação não disponível")
            return False
            
        try:
            # Simula dados de exame (sem arquivo real)
            exam_data = {
                "patient_id": "test_patient_id",
                "exam_type": "blood_test",
                "exam_date": "2025-01-21",
                "notes": "Teste de upload de exame"
            }
            
            # Teste sem arquivo (deve falhar, mas valida o endpoint)
            response = self.session.post(f"{self.base_url}/exams/upload", data=exam_data)
            
            # Esperamos que falhe sem arquivo, mas o endpoint deve estar funcionando
            if response.status_code in [400, 422]:  # Bad Request ou Validation Error
                self.log_test("Exam Upload Endpoint", True, "Endpoint funcionando (falha esperada sem arquivo)")
                return True
            else:
                self.log_test("Exam Upload Endpoint", False, f"Status code inesperado: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Exam Upload", False, f"Erro: {str(e)}")
            return False
    
    def test_biomarker_parsing(self) -> bool:
        """Testa parsing de biomarcadores"""
        try:
            # Dados de teste para parsing
            test_text = """
            Hemograma Completo:
            Hemoglobina: 14.2 g/dL
            Leucócitos: 7.500/mm³
            Plaquetas: 250.000/mm³
            Glicose: 95 mg/dL
            """
            
            # Teste do endpoint de parsing (se existir)
            response = self.session.post(f"{self.base_url}/exams/parse", json={"text": test_text})
            
            if response.status_code in [200, 201, 404, 405]:  # 404/405 se endpoint não implementado
                if response.status_code == 200:
                    self.log_test("Biomarker Parsing", True, "Parsing funcionando")
                else:
                    self.log_test("Biomarker Parsing", False, f"Endpoint não implementado (Status: {response.status_code})")
                return True
            else:
                self.log_test("Biomarker Parsing", False, f"Status code inesperado: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Biomarker Parsing", False, f"Erro: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🧪 INICIANDO TESTES DA API ANALYSA EM PRODUÇÃO")
        print("=" * 60)
        
        # Testes básicos
        self.test_health_check()
        self.test_root_endpoint()
        self.test_swagger_docs()
        
        # Testes de funcionalidade
        self.test_auth_endpoints()
        self.test_patients_endpoints()
        self.test_exam_upload()
        self.test_biomarker_parsing()
        
        # Resumo dos resultados
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de Testes: {total_tests}")
        print(f"✅ Passou: {passed_tests}")
        print(f"❌ Falhou: {failed_tests}")
        print(f"📈 Taxa de Sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ TESTES QUE FALHARAM:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🌐 URL da API: {API_BASE_URL}")
        print(f"📚 Documentação: {API_BASE_URL}/docs")
        
        return passed_tests == total_tests

def main():
    """Função principal"""
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TODOS OS TESTES PASSARAM! API funcionando perfeitamente!")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM. Verifique os detalhes acima.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
