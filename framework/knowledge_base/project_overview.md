# Project Overview - API de Exames Médicos

## Arquitetura Geral
API FastAPI para processamento de exames médicos via OCR, com foco em LGPD compliance, determinismo e escalabilidade.

## Stack Tecnológico
- **Backend**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL + RLS)
- **Storage**: Supabase Storage
- **Auth**: Supabase Auth (JWT)
- **OCR**: Tesseract (local integration)
- **Deploy**: Railway
- **Testing**: Pytest + Coverage

## Estrutura de Diretórios
```
src/
├── api/                    # FastAPI endpoints
│   ├── __init__.py
│   ├── auth.py            # Auth endpoints (login/register)
│   ├── exams.py           # Exam endpoints (upload/result)
│   ├── patients.py        # Patient CRUD endpoints
│   └── dependencies.py    # FastAPI dependencies
├── core/                   # Configurações e utilities
│   ├── __init__.py
│   ├── config.py          # Configurações de ambiente
│   ├── supabase_client.py # Cliente Supabase
│   ├── auth_middleware.py # JWT middleware
│   ├── resilience.py      # Circuit breaker, retry patterns
│   └── logging.py         # Logging anonimizado
├── database/               # Database models e conexões
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy models
│   └── migrations/        # SQL migrations
├── models/                 # Pydantic models
│   ├── __init__.py
│   ├── auth.py            # Auth request/response models
│   ├── exam.py            # Exam models
│   ├── patient.py         # Patient models
│   └── biomarker.py       # Biomarker models
├── services/               # Business logic
│   ├── __init__.py
│   ├── storage_service.py # Supabase Storage service
│   ├── ocr_service.py     # Tesseract OCR service
│   ├── parser_service.py  # Biomarker parser service
│   └── exam_service.py    # Exam processing service
└── utils/                  # Helpers e utilities
    ├── __init__.py
    ├── validators.py      # Validações customizadas
    └── helpers.py         # Funções auxiliares
```

## Padrões de Design
1. **Repository Pattern**: Separação entre lógica de negócio e acesso a dados
2. **Service Layer**: Business logic isolada em services
3. **Dependency Injection**: FastAPI dependencies para injeção de dependências
4. **Circuit Breaker**: Resilience patterns para integrações externas
5. **Retry Pattern**: Exponential backoff para operações que podem falhar

## Configurações de Ambiente
- **Development**: `.env.local`
- **Production**: Railway environment variables
- **Testing**: `.env.test`

## Estratégia de Testes
- **Unit Tests**: Pytest para lógica de negócio
- **Integration Tests**: Testes com Supabase local
- **Performance Tests**: Testes de OCR e upload
- **Security Tests**: Validação de RLS e JWT

## LGPD Compliance
- **RLS**: Row Level Security no Supabase
- **Data Encryption**: Storage criptografado
- **Audit Logs**: Timestamps de todas as operações
- **Anonymized Logging**: Logs sem dados pessoais
- **Access Control**: Médicos só acessam seus dados

## Performance Targets
- **OCR**: <5 segundos para arquivos <5MB
- **API Response**: <1 segundo
- **Database Queries**: <500ms
- **File Upload**: <10 segundos para 5MB

## Monitoring e Observability
- **Structured Logging**: structlog para logs estruturados
- **Metrics**: Tempo de OCR, taxa de sucesso
- **Health Checks**: Endpoints de saúde da API
- **Error Tracking**: Captura e log de erros

## Deploy Strategy
- **CI/CD**: GitHub Actions → Railway
- **Environment**: Staging e Production
- **Database Migrations**: Automáticas no deploy
- **Health Checks**: Validação pós-deploy

---
*Project Overview criado pelo expert_developer*
