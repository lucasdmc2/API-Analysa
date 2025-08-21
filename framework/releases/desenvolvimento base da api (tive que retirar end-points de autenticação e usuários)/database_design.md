# Database Design - API de Exames Médicos

## Visão Geral
Design do banco de dados Supabase para API de exames médicos com foco em LGPD compliance, RLS (Row Level Security), e estrutura escalável para biomarcadores.

## Stack
- **Database**: Supabase (PostgreSQL 15+)
- **ORM**: Supabase-py (Python client)
- **Security**: RLS (Row Level Security)
- **Compliance**: LGPD para dados de saúde

## Schema Design

### 1. Tabela: users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    crm VARCHAR(20) UNIQUE, -- CRM do médico
    specialty VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policy: Usuários só veem seus próprios dados
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);
```

### 2. Tabela: patients
```sql
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE, -- CPF do paciente
    birth_date DATE,
    gender VARCHAR(10),
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policy: Médicos só veem seus próprios pacientes
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Doctors can view own patients" ON patients
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = patients.user_id 
            AND users.id::text = auth.uid()::text
        )
    );

CREATE POLICY "Doctors can manage own patients" ON patients
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = patients.user_id 
            AND users.id::text = auth.uid()::text
        )
    );
```

### 3. Tabela: exams
```sql
CREATE TABLE exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL, -- Supabase Storage path
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- PDF, PNG, JPG, TXT
    mime_type VARCHAR(100),
    ocr_text TEXT, -- Texto extraído via Tesseract
    ocr_confidence DECIMAL(5,2), -- Confiança do OCR (0-100)
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policy: Médicos só veem exames de seus pacientes
ALTER TABLE exams ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Doctors can view own patient exams" ON exams
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM patients 
            WHERE patients.id = exams.patient_id 
            AND patients.user_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Doctors can manage own patient exams" ON exams
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM patients 
            WHERE patients.id = exams.patient_id 
            AND patients.user_id::text = auth.uid()::text
        )
    );
```

### 4. Tabela: biomarkers
```sql
CREATE TABLE biomarkers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL, -- Nome do biomarcador (ex: Hemoglobina)
    normalized_name VARCHAR(255) NOT NULL, -- Nome normalizado (ex: Hb)
    value DECIMAL(10,3) NOT NULL, -- Valor numérico
    unit VARCHAR(50) NOT NULL, -- Unidade (ex: g/dL)
    reference_range_id UUID REFERENCES reference_ranges(id),
    status VARCHAR(20) NOT NULL, -- normal, altered, critical
    confidence_score DECIMAL(5,2), -- Confiança da extração
    raw_text TEXT, -- Texto original extraído
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policy: Herda do exam
ALTER TABLE biomarkers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Doctors can view biomarkers from own exams" ON biomarkers
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM exams 
            WHERE exams.id = biomarkers.exam_id 
            AND EXISTS (
                SELECT 1 FROM patients 
                WHERE patients.id = exams.patient_id 
                AND patients.user_id::text = auth.uid()::text
            )
        )
    );
```

### 5. Tabela: reference_ranges
```sql
CREATE TABLE reference_ranges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    biomarker_name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255) NOT NULL,
    min_value DECIMAL(10,3),
    max_value DECIMAL(10,3),
    unit VARCHAR(50) NOT NULL,
    gender VARCHAR(10), -- NULL para ambos, 'M' para masculino, 'F' para feminino
    age_min INTEGER, -- Idade mínima em anos
    age_max INTEGER, -- Idade máxima em anos
    is_active BOOLEAN DEFAULT true,
    source VARCHAR(255), -- Fonte dos dados (ex: "Sociedade Brasileira de Patologia")
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policy: Referências são públicas para médicos autenticados
ALTER TABLE reference_ranges ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view reference ranges" ON reference_ranges
    FOR SELECT USING (auth.role() = 'authenticated');
```

## Índices para Performance
```sql
-- Índices para queries frequentes
CREATE INDEX idx_exams_patient_id ON exams(patient_id);
CREATE INDEX idx_exams_user_id ON exams(user_id);
CREATE INDEX idx_exams_status ON exams(status);
CREATE INDEX idx_biomarkers_exam_id ON biomarkers(exam_id);
CREATE INDEX idx_biomarkers_normalized_name ON biomarkers(normalized_name);
CREATE INDEX idx_reference_ranges_normalized_name ON reference_ranges(normalized_name);
CREATE INDEX idx_patients_user_id ON patients(user_id);
CREATE INDEX idx_patients_cpf ON patients(cpf);
```

## Funções de Trigger para Auditoria
```sql
-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para auditoria
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exams_updated_at BEFORE UPDATE ON exams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reference_ranges_updated_at BEFORE UPDATE ON reference_ranges
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Seed Data para Reference Ranges
```sql
-- Dados brasileiros comuns (Sprint 3)
INSERT INTO reference_ranges (biomarker_name, normalized_name, min_value, max_value, unit, gender, age_min, age_max, source) VALUES
('Hemoglobina', 'Hb', 12.0, 16.0, 'g/dL', 'F', 18, 65, 'Sociedade Brasileira de Patologia'),
('Hemoglobina', 'Hb', 13.0, 17.0, 'g/dL', 'M', 18, 65, 'Sociedade Brasileira de Patologia'),
('Glicose', 'Glu', 70.0, 100.0, 'mg/dL', NULL, 18, 65, 'Sociedade Brasileira de Diabetes'),
('Creatinina', 'Cr', 0.6, 1.1, 'mg/dL', 'F', 18, 65, 'Sociedade Brasileira de Nefrologia'),
('Creatinina', 'Cr', 0.7, 1.3, 'mg/dL', 'M', 18, 65, 'Sociedade Brasileira de Nefrologia'),
('Colesterol Total', 'CT', 0.0, 200.0, 'mg/dL', NULL, 18, 65, 'Sociedade Brasileira de Cardiologia');
```

## Migrations
```sql
-- Migration 001: Initial schema
-- Executar na ordem das tabelas acima

-- Migration 002: Add indexes
-- Executar após criação das tabelas

-- Migration 003: Add seed data
-- Executar após criação das tabelas
```

## LGPD Compliance Features
1. **RLS**: Acesso restrito por usuário
2. **Auditoria**: Timestamps de criação/atualização
3. **Cascade Delete**: Dados relacionados são removidos automaticamente
4. **Minimal Data**: Apenas dados essenciais são armazenados
5. **Access Control**: Médicos só acessam seus próprios dados

---
*Design criado pelo database_architect - Pronto para implementação*
