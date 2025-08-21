# API de Exames Médicos

API para processamento de exames médicos via OCR com LGPD compliance, desenvolvida em FastAPI + Supabase + Tesseract.

## 🚀 Características

- **OCR Determinístico**: Processamento consistente de PDFs e imagens
- **LGPD Compliance**: RLS, logs anonimizados, dados criptografados
- **Resilience**: Circuit breaker, retry patterns, timeouts
- **Performance**: OCR <5s, API <1s, DB <500ms
- **Stack Moderno**: FastAPI, Supabase, Tesseract, Railway

## 🏗️ Arquitetura

```
src/
├── api/           # FastAPI endpoints
├── core/          # Configurações e utilities
├── database/      # Models e conexões Supabase
├── models/        # Pydantic models
├── services/      # Business logic (OCR, parser)
└── utils/         # Helpers e utilities
```

## 🛠️ Tecnologias

- **Backend**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL + RLS)
- **Storage**: Supabase Storage
- **Auth**: Supabase Auth (JWT)
- **OCR**: Tesseract (local integration)
- **Deploy**: Railway
- **Testing**: Pytest + Coverage

## 📋 Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Conta Supabase
- Tesseract OCR instalado

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/api-exames-medicos/api.git
cd api
```

### 2. Configure as variáveis de ambiente
```bash
cp env.example .env
# Edite .env com suas configurações do Supabase
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Execute com Docker
```bash
docker-compose up --build
```

### 5. Execute localmente
```bash
uvicorn src.main:app --reload
```

## 🔧 Configuração

### Variáveis de Ambiente Obrigatórias
- `SUPABASE_URL`: URL do seu projeto Supabase
- `SUPABASE_ANON_KEY`: Chave anônima do Supabase
- `SUPABASE_SERVICE_ROLE_KEY`: Chave de serviço (opcional)

### Configurações Opcionais
- `DEBUG`: Modo debug (padrão: false)
- `LOG_LEVEL`: Nível de logging (padrão: INFO)
- `MAX_FILE_SIZE`: Tamanho máximo de arquivo (padrão: 5MB)

## 📚 Uso

### Endpoints Principais

- `GET /`: Informações da API
- `GET /health`: Verificação de saúde
- `POST /api/v1/auth/register`: Registro de médico
- `POST /api/v1/auth/login`: Login de médico
- `POST /api/v1/exams/upload`: Upload de exame
- `GET /api/v1/exams/{id}/result`: Resultado do exame

### Exemplo de Upload
```bash
curl -X POST "http://localhost:8000/api/v1/exams/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@exame.pdf" \
  -F "patient_id=123"
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com coverage
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/test_ocr.py
```

## 📊 Roadmap

- **Sprint 1**: ✅ Setup infra (GitHub, Railway, Supabase, Auth)
- **Sprint 2**: 🔄 Upload/Processamento (OCR, parser básico)
- **Sprint 3**: ⏳ Biomarcadores (normalização, comparação, resumo)
- **Sprint 4**: ⏳ Gestão (CRUD pacientes, RLS)
- **Sprint 5**: ⏳ Testes/Docs (CI/CD, Swagger)

## 🔒 Segurança

- **RLS**: Row Level Security no Supabase
- **JWT**: Autenticação com tokens
- **LGPD**: Compliance com legislação brasileira
- **Logs Anonimizados**: Sem dados pessoais nos logs
- **Storage Criptografado**: Arquivos seguros no Supabase

## 📈 Performance

- **OCR**: <5 segundos para arquivos <5MB
- **API Response**: <1 segundo
- **Database Queries**: <500ms
- **File Upload**: <10 segundos para 5MB

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

- **Email**: team@api-exames.com
- **Issues**: [GitHub Issues](https://github.com/api-exames-medicos/api/issues)
- **Documentação**: [Wiki](https://github.com/api-exames-medicos/api/wiki)

## 🙏 Agradecimentos

- FastAPI por um framework incrível
- Supabase por infraestrutura robusta
- Tesseract por OCR de qualidade
- Comunidade Python por suporte contínuo

---

**Desenvolvido com ❤️ pela equipe API de Exames Médicos**
