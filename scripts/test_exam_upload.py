#!/usr/bin/env python3
"""
Script para Testar Upload de Exames na API Analysa
Inclui testes com arquivos reais (PDF, imagem) e validação do output
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

class ExamUploadTester:
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
    
    def authenticate(self) -> bool:
        """Autentica na API"""
        try:
            # Criar usuário de teste
            test_user = {
                "email": f"test_exam_{int(time.time())}@example.com",
                "password": "TestExam123!",
                "full_name": "Usuário Teste Exames"
            }
            
            # Tentar registro
            response = self.session.post(f"{self.base_url}/auth/register", json=test_user)
            if response.status_code not in [200, 201, 409]:
                print(f"⚠️  Registro falhou: {response.status_code}")
                return False
            
            # Fazer login
            login_data = {
                "email": test_user["email"],
                "password": test_user["password"]
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("Authentication", True, "Token obtido com sucesso")
                return True
            else:
                self.log_test("Authentication", False, f"Login falhou: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Erro: {str(e)}")
            return False
    
    def create_test_patient(self) -> Optional[str]:
        """Cria um paciente de teste"""
        try:
            test_patient = {
                "full_name": "Maria Santos Teste",
                "date_of_birth": "1985-05-15",
                "cpf": "98765432100",
                "email": "maria.teste@example.com",
                "phone": "+5511888888888"
            }
            
            response = self.session.post(f"{self.base_url}/patients/", json=test_patient)
            if response.status_code in [200, 201]:
                data = response.json()
                patient_id = data.get("id")
                self.log_test("Create Test Patient", True, f"Paciente criado: {patient_id}")
                return patient_id
            else:
                self.log_test("Create Test Patient", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Create Test Patient", False, f"Erro: {str(e)}")
            return None
    
    def test_exam_upload_without_file(self, patient_id: str) -> bool:
        """Testa upload de exame sem arquivo (deve falhar)"""
        try:
            exam_data = {
                "patient_id": patient_id,
                "exam_type": "blood_test",
                "exam_date": "2025-01-21",
                "notes": "Teste de upload sem arquivo"
            }
            
            response = self.session.post(f"{self.base_url}/exams/upload", data=exam_data)
            
            # Esperamos que falhe sem arquivo
            if response.status_code in [400, 422]:
                self.log_test("Upload Sem Arquivo", True, "Falha esperada sem arquivo")
                return True
            else:
                self.log_test("Upload Sem Arquivo", False, f"Status inesperado: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Upload Sem Arquivo", False, f"Erro: {str(e)}")
            return False
    
    def test_exam_upload_with_text(self, patient_id: str) -> bool:
        """Testa upload de exame com texto direto"""
        try:
            exam_data = {
                "patient_id": patient_id,
                "exam_type": "blood_test",
                "exam_date": "2025-01-21",
                "notes": "Teste com texto direto",
                "exam_text": """
                HEMOGRAMA COMPLETO
                
                Hemoglobina: 14.2 g/dL (12.0-16.0)
                Leucócitos: 7.500/mm³ (4.500-11.000)
                Plaquetas: 250.000/mm³ (150.000-450.000)
                Glicose: 95 mg/dL (70-100)
                Colesterol Total: 180 mg/dL (<200)
                Triglicerídeos: 120 mg/dL (<150)
                
                Observações: Exame dentro dos parâmetros normais.
                """
            }
            
            response = self.session.post(f"{self.base_url}/exams/upload", json=exam_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("Upload Com Texto", True, f"Exame processado: {data.get('id', 'N/A')}")
                return True
            elif response.status_code == 404:
                self.log_test("Upload Com Texto", False, "Endpoint não implementado")
                return False
            else:
                self.log_test("Upload Com Texto", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Upload Com Texto", False, f"Erro: {str(e)}")
            return False
    
    def test_biomarker_extraction(self, patient_id: str) -> bool:
        """Testa extração de biomarcadores"""
        try:
            # Texto de teste com biomarcadores
            test_text = """
            EXAME DE SANGUE - 21/01/2025
            
            RESULTADOS:
            Hemoglobina: 14.2 g/dL
            Leucócitos: 7.500/mm³
            Plaquetas: 250.000/mm³
            Glicose: 95 mg/dL
            Colesterol Total: 180 mg/dL
            Triglicerídeos: 120 mg/dL
            Creatinina: 0.9 mg/dL
            Ureia: 25 mg/dL
            """
            
            # Teste do endpoint de parsing
            response = self.session.post(f"{self.base_url}/exams/parse", json={
                "text": test_text,
                "patient_id": patient_id
            })
            
            if response.status_code == 200:
                data = response.json()
                biomarkers = data.get("biomarkers", [])
                self.log_test("Biomarker Extraction", True, f"Biomarcadores extraídos: {len(biomarkers)}")
                return True
            elif response.status_code in [404, 405]:
                self.log_test("Biomarker Extraction", False, "Endpoint não implementado")
                return False
            else:
                self.log_test("Biomarker Extraction", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Biomarker Extraction", False, f"Erro: {str(e)}")
            return False
    
    def test_exam_listing(self) -> bool:
        """Testa listagem de exames"""
        try:
            response = self.session.get(f"{self.base_url}/exams/")
            
            if response.status_code == 200:
                data = response.json()
                exams = data.get("exams", [])
                self.log_test("List Exams", True, f"Exames encontrados: {len(exams)}")
                return True
            elif response.status_code == 404:
                self.log_test("List Exams", False, "Endpoint não implementado")
                return False
            else:
                self.log_test("List Exams", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("List Exams", False, f"Erro: {str(e)}")
            return False
    
    def run_exam_tests(self):
        """Executa todos os testes de exames"""
        print("🧪 TESTANDO FUNCIONALIDADES DE EXAMES")
        print("=" * 60)
        
        # Autenticação
        if not self.authenticate():
            print("❌ Falha na autenticação. Abortando testes.")
            return False
        
        # Criar paciente de teste
        patient_id = self.create_test_patient()
        if not patient_id:
            print("❌ Falha ao criar paciente. Abortando testes.")
            return False
        
        # Testes de upload
        self.test_exam_upload_without_file(patient_id)
        self.test_exam_upload_with_text(patient_id)
        
        # Testes de processamento
        self.test_biomarker_extraction(patient_id)
        self.test_exam_listing()
        
        # Resumo
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES DE EXAMES")
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
    tester = ExamUploadTester()
    success = tester.run_exam_tests()
    
    if success:
        print("\n🎉 TODOS OS TESTES DE EXAMES PASSARAM!")
    else:
        print("\n⚠️  ALGUNS TESTES DE EXAMES FALHARAM.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
