# 🧪 GUIA COMPLETO DE TESTES MANUAIS - API ANALYSA

## 🚀 **TESTES BÁSICOS (Sem Autenticação)**

### **1. Health Check**
```bash
curl https://api-analysa-production.up.railway.app/health
```

**Resposta Esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "0.1.0"
}
```

### **2. Endpoint Raiz**
```bash
curl https://api-analysa-production.up.railway.app/
```

**Resposta Esperada:**
```json
{
  "message": "API de Exames Médicos",
  "version": "0.1.0",
  "status": "running"
}
```

### **3. Documentação Swagger**
Acesse no navegador: https://api-analysa-production.up.railway.app/docs

---

## 🔐 **TESTES DE AUTENTICAÇÃO**

### **1. Registro de Usuário**
```bash
curl -X POST https://api-analysa-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "Teste123!",
    "full_name": "Usuário Teste"
  }'
```

### **2. Login**
```bash
curl -X POST https://api-analysa-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "Teste123!"
  }'
```

**Resposta Esperada:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

**⚠️ IMPORTANTE:** Guarde o `access_token` para usar nos próximos testes!

---

## 👥 **TESTES DE PACIENTES (Com Autenticação)**

### **1. Criar Paciente**
```bash
curl -X POST https://api-analysa-production.up.railway.app/api/v1/patients/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "full_name": "João Silva",
    "date_of_birth": "1990-01-01",
    "cpf": "12345678901",
    "email": "joao.silva@example.com",
    "phone": "+5511999999999"
  }'
```

### **2. Listar Pacientes**
```bash
curl -X GET https://api-analysa-production.up.railway.app/api/v1/patients/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 📋 **TESTES DE EXAMES (Com Autenticação)**

### **1. Upload de Exame com Texto**
```bash
curl -X POST https://api-analysa-production.up.railway.app/api/v1/exams/upload \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "patient_id": "ID_DO_PACIENTE",
    "exam_type": "blood_test",
    "exam_date": "2025-01-21",
    "notes": "Teste de upload",
    "exam_text": "HEMOGRAMA COMPLETO\n\nHemoglobina: 14.2 g/dL\nLeucócitos: 7.500/mm³\nPlaquetas: 250.000/mm³"
  }'
```

### **2. Extração de Biomarcadores**
```bash
curl -X POST https://api-analysa-production.up.railway.app/api/v1/exams/parse \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "text": "Hemoglobina: 14.2 g/dL\nLeucócitos: 7.500/mm³\nPlaquetas: 250.000/mm³",
    "patient_id": "ID_DO_PACIENTE"
  }'
```

### **3. Listar Exames**
```bash
curl -X GET https://api-analysa-production.up.railway.app/api/v1/exams/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 🧪 **TESTES AUTOMATIZADOS**

### **1. Teste Completo da API**
```bash
python scripts/test_production_api.py
```

### **2. Teste Específico de Exames**
```bash
python scripts/test_exam_upload.py
```

---

## 🌐 **TESTES VIA NAVEGADOR**

### **1. Swagger UI**
- URL: https://api-analysa-production.up.railway.app/docs
- Permite testar todos os endpoints interativamente
- Inclui autenticação automática

### **2. ReDoc**
- URL: https://api-analysa-production.up.railway.app/redoc
- Documentação mais legível

---

## 📱 **TESTES VIA POSTMAN/INSOMNIA**

### **1. Collection de Testes**
Crie uma collection com os seguintes requests:

#### **Health Check**
- Method: GET
- URL: `https://api-analysa-production.up.railway.app/health`

#### **Registro**
- Method: POST
- URL: `https://api-analysa-production.up.railway.app/api/v1/auth/register`
- Body (JSON):
```json
{
  "email": "teste@example.com",
  "password": "Teste123!",
  "full_name": "Usuário Teste"
}
```

#### **Login**
- Method: POST
- URL: `https://api-analysa-production.up.railway.app/api/v1/auth/login`
- Body (JSON):
```json
{
  "email": "teste@example.com",
  "password": "Teste123!"
}
```

#### **Criar Paciente**
- Method: POST
- URL: `https://api-analysa-production.up.railway.app/api/v1/patients/`
- Headers: `Authorization: Bearer {{token}}`
- Body (JSON):
```json
{
  "full_name": "João Silva",
  "date_of_birth": "1990-01-01",
  "cpf": "12345678901",
  "email": "joao.silva@example.com",
  "phone": "+5511999999999"
}
```

#### **Upload de Exame**
- Method: POST
- URL: `https://api-analysa-production.up.railway.app/api/v1/exams/upload`
- Headers: `Authorization: Bearer {{token}}`
- Body (JSON):
```json
{
  "patient_id": "{{patient_id}}",
  "exam_type": "blood_test",
  "exam_date": "2025-01-21",
  "notes": "Teste via Postman",
  "exam_text": "HEMOGRAMA COMPLETO\n\nHemoglobina: 14.2 g/dL\nLeucócitos: 7.500/mm³"
}
```

### **2. Variáveis de Ambiente**
Configure as seguintes variáveis:
- `base_url`: `https://api-analysa-production.up.railway.app`
- `token`: (será preenchido automaticamente após login)
- `patient_id`: (será preenchido após criar paciente)

---

## 🔍 **VALIDAÇÃO DE OUTPUTS**

### **1. Resposta de Paciente Criado**
```json
{
  "id": "uuid-do-paciente",
  "full_name": "João Silva",
  "date_of_birth": "1990-01-01",
  "cpf": "12345678901",
  "email": "joao.silva@example.com",
  "phone": "+5511999999999",
  "created_at": "2025-01-21T10:00:00Z"
}
```

### **2. Resposta de Exame Processado**
```json
{
  "id": "uuid-do-exame",
  "patient_id": "uuid-do-paciente",
  "exam_type": "blood_test",
  "exam_date": "2025-01-21",
  "notes": "Teste via Postman",
  "status": "processed",
  "biomarkers": [
    {
      "name": "Hemoglobina",
      "value": "14.2",
      "unit": "g/dL",
      "reference_range": "12.0-16.0"
    },
    {
      "name": "Leucócitos",
      "value": "7.500",
      "unit": "/mm³",
      "reference_range": "4.500-11.000"
    }
  ],
  "created_at": "2025-01-21T10:00:00Z"
}
```

---

## 🚨 **CENÁRIOS DE ERRO PARA TESTAR**

### **1. Autenticação Inválida**
```bash
curl -X GET https://api-analysa-production.up.railway.app/api/v1/patients/ \
  -H "Authorization: Bearer token_invalido"
```

**Resposta Esperada:** 401 Unauthorized

### **2. Dados Inválidos**
```bash
curl -X POST https://api-analysa-production.up.railway.app/api/v1/patients/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "full_name": "",
    "email": "email_invalido"
  }'
```

**Resposta Esperada:** 422 Validation Error

### **3. Recurso Não Encontrado**
```bash
curl -X GET https://api-analysa-production.up.railway.app/api/v1/patients/999999 \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

**Resposta Esperada:** 404 Not Found

---

## 📊 **CHECKLIST DE TESTES**

### **✅ Testes Básicos**
- [ ] Health check responde
- [ ] Endpoint raiz funciona
- [ ] Swagger docs acessível

### **✅ Testes de Autenticação**
- [ ] Registro de usuário
- [ ] Login e obtenção de token
- [ ] Token inválido rejeitado

### **✅ Testes de Pacientes**
- [ ] Criação de paciente
- [ ] Listagem de pacientes
- [ ] Validação de dados

### **✅ Testes de Exames**
- [ ] Upload com texto
- [ ] Extração de biomarcadores
- [ ] Listagem de exames

### **✅ Testes de Erro**
- [ ] Autenticação inválida
- [ ] Dados inválidos
- [ ] Recursos não encontrados

---

## 🎯 **PRÓXIMOS PASSOS**

1. **Execute os testes básicos** para verificar conectividade
2. **Teste a autenticação** para obter um token
3. **Crie um paciente de teste** para usar nos testes de exames
4. **Teste o upload de exames** com diferentes tipos de texto
5. **Valide os outputs** para garantir que o parsing está funcionando
6. **Use o Swagger UI** para testes interativos
7. **Execute os scripts automatizados** para validação completa

---

**🌐 URL da API**: https://api-analysa-production.up.railway.app  
**📚 Documentação**: https://api-analysa-production.up.railway.app/docs  
**🔧 Status**: ✅ **FUNCIONANDO EM PRODUÇÃO**
