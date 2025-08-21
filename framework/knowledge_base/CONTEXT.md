# API de Exames Médicos - Contexto do Projeto

## Visão Geral
API para médicos processar exames (PDF/imagens/texto) via OCR, normalizar biomarcadores, comparar ranges, gerar resumo JSON. MVP foca em determinismo, segurança (LGPD), stack: FastAPI, Supabase, Tesseract.

## Stack Tecnológico
- **Backend**: FastAPI (Python 3.11)
- **Database**: Supabase (PostgreSQL + RLS)
- **Storage**: Supabase Storage
- **Auth**: Supabase Auth (JWT)
- **OCR**: Tesseract (local integration)
- **Deploy**: Railway
- **Testing**: Pytest

## Arquitetura
```
src/
├── api/           # FastAPI endpoints
├── core/          # Configurações e utilities
├── database/      # Models e conexões Supabase
├── models/        # Pydantic models
├── services/      # Business logic (OCR, parser)
└── utils/         # Helpers
```

## Roadmap - Sprints
- **Sprint 1**: Setup infra (GitHub, Railway, Supabase, Auth)
- **Sprint 2**: Upload/Processamento (OCR, parser básico)
- **Sprint 3**: Biomarcadores (normalização, comparação, resumo)
- **Sprint 4**: Gestão (CRUD pacientes, RLS)
- **Sprint 5**: Testes/Docs (CI/CD, Swagger)

## Requisitos Críticos
- **LGPD Compliance**: RLS, storage criptografado, logs anonimizados
- **Determinismo**: Mesmo input → mesmo output (OCR/parser)
- **Performance**: OCR <5s, API <1s, DB <500ms
- **Segurança**: Links assinados expiram em 24h

## Status Atual
- **Fase**: Phase 0 - Context Analysis
- **Próximo**: Phase 1 - Specification refinement
- **Especialistas**: database_architect, api_architect, expert_developer, test_engineer, delivery_reviewer

## Especificação Base
Documento principal: `docs/api_exames_specification.markdown`
Especificação runtime: `framework/runtime/specification.md` (será criada)

---
*Última atualização: Início do projeto - Context Manager*
