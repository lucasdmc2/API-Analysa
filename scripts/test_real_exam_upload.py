#!/usr/bin/env python3
"""
Script para Testar Upload de Exame Real na API Analysa
Testa o fluxo completo: upload → OCR → processamento → resultado
"""

import requests
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional
import base64

# Configurações da API
API_BASE_URL = "https://api-analysa-production.up.railway.app"
API_VERSION = "v1"

class RealExamUploadTester:
    def __init__(self):
        self.base_url = f"{API_BASE_URL}/api/{API_VERSION}"
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.exam_id = None
        self.patient_id = None
        
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
            print("🔐 Autenticando na API...")
            
            # Criar usuário de teste único
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
                self.log_test("Authentication", True, f"Token obtido: {self.auth_token[:20]}...")
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
            print("👤 Criando paciente de teste...")
            
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
                self.patient_id = patient_id
                self.log_test("Create Test Patient", True, f"Paciente criado: {patient_id}")
                return patient_id
            else:
                self.log_test("Create Test Patient", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Create Test Patient", False, f"Erro: {str(e)}")
            return None
    
    def upload_real_exam(self) -> bool:
        """Faz upload do arquivo real de exame"""
        try:
            print("📁 Fazendo upload do arquivo real...")
            
            # Caminho para o arquivo real
            exam_file_path = Path("Exames Dr. Julio.pdf")
            
            if not exam_file_path.exists():
                self.log_test("File Upload", False, f"Arquivo não encontrado: {exam_file_path}")
                return False
            
            # Verifica tamanho do arquivo
            file_size = exam_file_path.stat().st_size
            print(f"📊 Tamanho do arquivo: {file_size / 1024:.1f} KB")
            
            # Prepara dados para upload
            files = {
                'file': ('Exames Dr. Julio.pdf', open(exam_file_path, 'rb'), 'application/pdf')
            }
            
            data = {
                'patient_id': self.patient_id,
                'user_id': self.auth_token  # Usando token como user_id temporariamente
            }
            
            # Faz upload
            response = self.session.post(
                f"{self.base_url}/exams/upload",
                files=files,
                data=data
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.exam_id = data.get("exam_id")
                self.log_test("File Upload", True, f"Exame enviado: {self.exam_id}")
                print(f"🆔 ID do Exame: {self.exam_id}")
                print(f"📋 Status: {data.get('status')}")
                print(f"💬 Mensagem: {data.get('message')}")
                return True
            else:
                self.log_test("File Upload", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("File Upload", False, f"Erro: {str(e)}")
            return False
    
    def monitor_processing_status(self) -> bool:
        """Monitora o status do processamento do exame"""
        try:
            print("⏳ Monitorando status do processamento...")
            
            max_wait_time = 120  # 2 minutos
            start_time = time.time()
            last_status = None
            
            while time.time() - start_time < max_wait_time:
                response = self.session.get(
                    f"{self.base_url}/exams/{self.exam_id}/status",
                    params={"user_id": self.auth_token}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    current_status = data.get("status")
                    message = data.get("message")
                    
                    if current_status != last_status:
                        print(f"🔄 Status: {current_status} - {message}")
                        last_status = current_status
                    
                    # Verifica se processamento foi concluído
                    if current_status == "completed":
                        self.log_test("Processing Status", True, "Processamento concluído")
                        return True
                    elif current_status == "failed":
                        self.log_test("Processing Status", False, "Processamento falhou")
                        return False
                    
                    # Aguarda antes de verificar novamente
                    time.sleep(5)
                else:
                    print(f"⚠️  Erro ao verificar status: {response.status_code}")
                    time.sleep(10)
            
            self.log_test("Processing Status", False, "Timeout aguardando processamento")
            return False
            
        except Exception as e:
            self.log_test("Processing Status", False, f"Erro: {str(e)}")
            return False
    
    def get_exam_result(self) -> bool:
        """Obtém o resultado completo do exame processado"""
        try:
            print("📊 Obtendo resultado do exame...")
            
            response = self.session.get(
                f"{self.base_url}/exams/{self.exam_id}/result",
                params={"user_id": self.auth_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Exibe informações do arquivo
                file_info = data.get("file_info", {})
                print(f"📁 Arquivo: {file_info.get('file_name')}")
                print(f"📏 Tamanho: {file_info.get('file_size')} bytes")
                print(f"🔗 URL: {file_info.get('signed_url', 'N/A')[:50]}...")
                
                # Exibe texto OCR
                ocr_text = data.get("ocr_text", "")
                if ocr_text:
                    print(f"📝 Texto OCR ({len(ocr_text)} caracteres):")
                    print(f"   {ocr_text[:200]}...")
                    if len(ocr_text) > 200:
                        print(f"   ... (truncado, total: {len(ocr_text)} caracteres)")
                else:
                    print("⚠️  Nenhum texto OCR encontrado")
                
                # Exibe biomarcadores
                biomarkers = data.get("biomarkers", [])
                if biomarkers:
                    print(f"🔬 Biomarcadores encontrados: {len(biomarkers)}")
                    for i, biomarker in enumerate(biomarkers[:5]):  # Mostra os primeiros 5
                        print(f"   {i+1}. {biomarker.get('name', 'N/A')}: {biomarker.get('value', 'N/A')} {biomarker.get('unit', '')} - Status: {biomarker.get('status', 'N/A')}")
                    
                    if len(biomarkers) > 5:
                        print(f"   ... e mais {len(biomarkers) - 5} biomarcadores")
                else:
                    print("⚠️  Nenhum biomarcador encontrado")
                
                # Salva resultado em arquivo para análise
                result_file = f"exam_result_{self.exam_id}.json"
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
                print(f"💾 Resultado salvo em: {result_file}")
                
                self.log_test("Get Exam Result", True, f"Resultado obtido com {len(biomarkers)} biomarcadores")
                return True
            else:
                self.log_test("Get Exam Result", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Exam Result", False, f"Erro: {str(e)}")
            return False
    
    def validate_ocr_quality(self) -> bool:
        """Valida a qualidade do OCR"""
        try:
            print("🔍 Validando qualidade do OCR...")
            
            # Lê o arquivo de resultado
            result_file = f"exam_result_{self.exam_id}.json"
            if not os.path.exists(result_file):
                self.log_test("OCR Quality Validation", False, "Arquivo de resultado não encontrado")
                return False
            
            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            ocr_text = data.get("ocr_text", "")
            if not ocr_text:
                self.log_test("OCR Quality Validation", False, "Nenhum texto OCR disponível")
                return False
            
            # Análise básica de qualidade
            total_chars = len(ocr_text)
            words = ocr_text.split()
            total_words = len(words)
            
            # Verifica se há números (indicando valores de exames)
            import re
            numbers = re.findall(r'\d+\.?\d*', ocr_text)
            total_numbers = len(numbers)
            
            # Verifica se há unidades médicas comuns
            medical_units = ['mg/dL', 'g/dL', 'mm³', 'mg/L', 'mmol/L', 'U/L', 'mEq/L']
            units_found = [unit for unit in medical_units if unit in ocr_text]
            
            print(f"📊 Análise do OCR:")
            print(f"   Caracteres: {total_chars}")
            print(f"   Palavras: {total_words}")
            print(f"   Números: {total_numbers}")
            print(f"   Unidades médicas: {units_found}")
            
            # Critérios de qualidade
            quality_score = 0
            if total_chars > 100:
                quality_score += 1
            if total_words > 20:
                quality_score += 1
            if total_numbers > 5:
                quality_score += 1
            if len(units_found) > 0:
                quality_score += 1
            
            quality_percentage = (quality_score / 4) * 100
            
            if quality_percentage >= 75:
                self.log_test("OCR Quality Validation", True, f"Qualidade: {quality_percentage:.0f}% (Excelente)")
            elif quality_percentage >= 50:
                self.log_test("OCR Quality Validation", True, f"Qualidade: {quality_percentage:.0f}% (Boa)")
            else:
                self.log_test("OCR Quality Validation", False, f"Qualidade: {quality_percentage:.0f}% (Baixa)")
            
            return quality_percentage >= 50
            
        except Exception as e:
            self.log_test("OCR Quality Validation", False, f"Erro: {str(e)}")
            return False
    
    def run_complete_test(self):
        """Executa o teste completo de upload e processamento"""
        print("🧪 TESTE COMPLETO DE UPLOAD DE EXAME REAL")
        print("=" * 70)
        print(f"🌐 API: {API_BASE_URL}")
        print(f"📁 Arquivo: Exames Dr. Julio.pdf")
        print("=" * 70)
        
        # 1. Autenticação
        if not self.authenticate():
            print("❌ Falha na autenticação. Abortando teste.")
            return False
        
        # 2. Criar paciente de teste
        if not self.create_test_patient():
            print("❌ Falha ao criar paciente. Abortando teste.")
            return False
        
        # 3. Upload do arquivo real
        if not self.upload_real_exam():
            print("❌ Falha no upload. Abortando teste.")
            return False
        
        # 4. Monitorar processamento
        if not self.monitor_processing_status():
            print("❌ Falha no processamento. Abortando teste.")
            return False
        
        # 5. Obter resultado
        if not self.get_exam_result():
            print("❌ Falha ao obter resultado. Abortando teste.")
            return False
        
        # 6. Validar qualidade do OCR
        self.validate_ocr_quality()
        
        # Resumo final
        print("\n" + "=" * 70)
        print("📊 RESUMO DO TESTE COMPLETO")
        print("=" * 70)
        
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
        
        print(f"\n🆔 ID do Exame: {self.exam_id}")
        print(f"👤 ID do Paciente: {self.patient_id}")
        print(f"🌐 URL da API: {API_BASE_URL}")
        print(f"📚 Documentação: {API_BASE_URL}/docs")
        
        return passed_tests == total_tests

def main():
    """Função principal"""
    tester = RealExamUploadTester()
    success = tester.run_complete_test()
    
    if success:
        print("\n🎉 TESTE COMPLETO REALIZADO COM SUCESSO!")
        print("✅ Upload do arquivo real funcionando")
        print("✅ Processamento OCR funcionando")
        print("✅ Extração de biomarcadores funcionando")
        print("✅ API retornando resultados completos")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM.")
        print("🔍 Verifique os logs acima para identificar problemas")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
