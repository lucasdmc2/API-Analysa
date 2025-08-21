# Especificação da API de Exames Médicos — Fase 1 (MVP) [Adaptada para Agent Framework]

Esta especificação é otimizada para o framework de agentes: `delivery_orchestrator` coordena; `spec_planner` refinou; `context_manager` sync context; `database_architect` para DB; `api_architect` para integrations; `expert_developer` implementa; `test_engineer` cria/executa testes; `delivery_reviewer` valida. Alinha com roadmap Sprints como milestones. Use `CONTEXT.md` como base.

---

## Executive Summary
API para médicos processar exames (PDF/imagens/texto) via OCR, normalizar biomarcadores, comparar ranges, gerar resumo JSON. MVP foca em determinismo, segurança (LGPD), stack: FastAPI, Supabase, Tesseract. Valor: Acelera interpretação clínica no Brasil.

---

## Goals and Subgoals (por Sprint/Milestone)
- **Sprint 1 (Setup):** Infra básica (GitHub, Railway, Supabase). **Sucesso**: Ambiente rodando, tabelas criadas, auth funcional. **Milestone**: Review inicial da infra.
- **Sprint 2 (Upload/Processamento):** Upload e OCR inicial. **Sucesso**: Endpoint aceita arquivos, extrai texto. **Milestone**: Testes de upload/OCR validados.
- **Sprint 3 (Biomarcadores):** Parser, comparação, resumo. **Sucesso**: JSON com status normal/alterado. **Milestone**: Resultados corretos em amostras.
- **Sprint 4 (Gestão):** CRUD pacientes/usuários, RLS. **Sucesso**: Acesso restrito. **Milestone**: RLS e auth validados.
- **Sprint 5 (Testes/Docs):** Qualidade e deploy. **Sucesso**: Cobertura 80%, CI/CD no Railway. **Milestone**: Deploy funcional.

---

## Detailed Functional Requirements
- **Upload Exame**: Aceita PDF/PNG/JPG/TXT, salva em Supabase Storage (link assinado), inicia OCR (Tesseract).
- **Resultado**: Extrai biomarcadores, compara com `reference_ranges`, gera summary textual.
- **Listar Exames**: Por paciente, com auth JWT.
- **Autenticação**: Login/register médicos via Supabase Auth.

---

## Non-Functional Requirements
- **Performance**: OCR <5s (arquivos <5MB); API responses <1s; Supabase queries <500ms.
- **Security (LGPD)**: RLS no Supabase; JWT para auth; Storage criptografado; links assinados expiram em 24h; no dados sensíveis em logs.
- **Scalability**: Supabase gerenciado; Railway para deploy escalável.
- **Observability**: Logging estruturado (structlog); métricas básicas (ex.: tempo OCR).
- **Determinismo**: Mesmo input → mesmo output (OCR/parser).

---

## Acceptance Criteria
- [ ] **Upload**: Arquivo salvo, metadados no DB, OCR extrai texto (teste com PDF/PNG real).
- [ ] **Resultado**: Biomarcadores parseados, status correto (normal/alterado), summary coerente.
- [ ] **Segurança**: RLS impede acesso indevido; links expiram; logs anonimizados.
- [ ] **Testes**: Coverage ≥80%, incluindo OCR edge cases (ex.: PDF corrompido).
- [ ] **Deploy**: CI/CD no Railway, Swagger docs acessíveis.

---

## Development Task Breakdown (por Agent/Sprint, com Status)
Tasks marcadas **PENDING**. Sub-checklist: [ ] Implementation, [ ] Tests, [ ] Docs. Testes delegados ao `test_engineer`.

### Sprint 1: Setup (Handoff to database_architect, api_architect, expert_developer)
- **Task 1**: Criar repo GitHub com FastAPI template. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Crie repo com .gitignore, requirements.txt (fastapi, supabase-py, pytesseract, pdf2image, pytest)."
- **Task 2**: Config Railway (Python 3.11). **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Setup Railway com Dockerfile e docker-compose.yml."
- **Task 3**: Config Supabase (Auth/DB/Storage). **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Configure cliente Supabase-py com env vars."
- **Task 4**: Criar tabelas/RLS. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to database_architect**: "Design Supabase tables (users, patients, exams, biomarkers, reference_ranges) com RLS para LGPD."
- **Task 5**: Auth JWT. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to api_architect**: "Design Supabase Auth integration com JWT."
- **Task 6**: Testes iniciais. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to test_engineer**: "Crie testes unitários para auth e tabelas com Pytest."
- **Milestone**: Review infra/auth (handoff to delivery_reviewer).

### Sprint 2: Upload/Processamento (Handoff to api_architect, expert_developer, test_engineer)
- **Task 1**: Endpoint /exams/upload. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Implemente endpoint async com FastAPI, aceitando PDF/PNG/JPG."
- **Task 2**: Upload Supabase Storage. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to api_architect**: "Design resilience para Supabase Storage (retries, timeouts)."
- **Task 3**: OCR Tesseract (com pdf2image). **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to api_architect**: "Design Tesseract como integração local, garantindo determinismo."
- **Task 4**: Parser básico. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Crie parser regex para extrair biomarcadores."
- **Task 5**: Testes upload/OCR. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to test_engineer**: "Crie testes com Pytest, incluindo PDF real e edge cases (ex.: arquivo corrompido)."
- **Milestone**: Review upload/OCR (handoff to delivery_reviewer).

### Sprint 3: Biomarcadores (Handoff to expert_developer, test_engineer)
- **Task 1**: Normalização/parser. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Implemente parser determinístico (ex.: Hb → Hemoglobina)."
- **Task 2**: Seed reference_ranges. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to database_architect**: "Popule reference_ranges com dados brasileiros (ex.: Hemoglobina 12-16 g/dL)."
- **Task 3**: Endpoint /exams/{id}/result. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Implemente endpoint com JSON estruturado."
- **Task 4**: Comparação/status. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Compare biomarcadores com ranges, marque normal/alterado."
- **Task 5**: Resumo textual. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Gere summary baseado em status alterado."
- **Task 6**: Testes biomarcadores. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to test_engineer**: "Crie testes para parser, comparação, e summary com Pytest."
- **Milestone**: Review resultados (handoff to delivery_reviewer).

### Sprint 4: Gestão (Handoff to expert_developer, test_engineer)
- **Task 1**: Endpoints auth/login/register. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Implemente auth com Supabase JWT."
- **Task 2**: CRUD patients. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Crie CRUD para patients com FastAPI."
- **Task 3**: Listar exames por paciente. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Implemente endpoint /patients/{id}/exams."
- **Task 4**: Validar RLS. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Configure RLS no Supabase para acesso restrito."
- **Task 5**: Testes gestão. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to test_engineer**: "Crie testes para auth, CRUD, e RLS com Pytest."
- **Milestone**: Review auth/gestão (handoff to delivery_reviewer).

### Sprint 5: Testes/Docs (Handoff to expert_developer, test_engineer, delivery_reviewer)
- **Task 1**: Testes unitários/integração. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to test_engineer**: "Crie suite completa com Pytest, mock Supabase/Tesseract."
- **Task 2**: Testes OCR com samples. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to test_engineer**: "Teste OCR com PDFs reais, incluindo edge cases."
- **Task 3**: Swagger/OpenAPI. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Gere docs com FastAPI/Swagger."
- **Task 4**: CI/CD Railway. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to expert_developer**: "Configure CI/CD no Railway via GitHub Actions."
- **Task 5**: Revisar segurança. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to delivery_reviewer**: "Valide LGPD, RLS, e links assinados."
- **Task 6**: Testes finais. **PENDING** [ ] Impl [ ] Tests [ ] Docs
  - **Handoff to test_engineer**: "Execute testes finais, garanta coverage ≥80%."
- **Milestone**: Review final e deploy (handoff to delivery_reviewer).

---

## Status Tracking Section
| Sprint | Status | Test Status | Notes |
|--------|--------|-------------|-------|
| Sprint 1 | PENDING | PENDING | Aguardando setup inicial |
| Sprint 2 | PENDING | PENDING | - |
| Sprint 3 | PENDING | PENDING | - |
| Sprint 4 | PENDING | PENDING | - |
| Sprint 5 | PENDING | PENDING | - |
| Overall | PENDING | PENDING | - |

**Update Rules**:
- `expert_developer`: Marca tasks como FINISHED/BLOCKED.
- `test_engineer`: Atualiza Test Status (PASSED/FAILED).
- `delivery_reviewer`: Valida milestones, aciona loop se issues.

---

## Agent Handoff Notes
- **To context_manager**: Iniciar com `CONTEXT.md` (Phase 0); atualizar pós-review (Phase 5).
- **To database_architect**: Design Supabase tables/RLS (Sprint 1, 3).
- **To api_architect**: Resilience para Supabase/Tesseract (Sprint 2, 4).
- **To expert_developer**: Impl por Sprint, seguir designs.
- **To test_engineer**: Criar/executar testes por Sprint, garantir coverage/LGPD.
- **To delivery_reviewer**: Validar após cada milestone/Sprint; loop para dev se necessário.

---

## Observações Finais
- **Iniciar com delivery_orchestrator**: Execute Phase 0 (triage, context sync).
- **LGPD Compliance**: RLS, encrypted storage, logs anonimizados em todas fases.
- **Determinismo**: Testar OCR/parser para consistência.
- **Deploy**: Railway CI/CD, Swagger docs.
- **Próximos Passos**: Após aprovação desta spec, `delivery_orchestrator` inicia Phase 1 (spec refinement) e avança por Sprints.

Esta spec está pronta para o framework. Use `delivery_orchestrator` para coordenar.