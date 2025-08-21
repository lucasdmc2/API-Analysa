-- =====================================================
-- SETUP COMPLETO DO BANCO - API de Exames Médicos
-- Execute este SQL no Supabase SQL Editor
-- =====================================================

-- 1. TABELA DE USUÁRIOS (MÉDICOS)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    crm VARCHAR(50),
    specialty VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. TABELA DE PACIENTES
CREATE TABLE IF NOT EXISTS patients (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    birth_date DATE NOT NULL,
    gender CHAR(1) NOT NULL CHECK (gender IN ('M', 'F')),
    phone VARCHAR(20),
    address TEXT,
    doctor_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. TABELA DE EXAMES
CREATE TABLE IF NOT EXISTS exams (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id UUID REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    ocr_text TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. TABELA DE BIOMARCADORES
CREATE TABLE IF NOT EXISTS biomarkers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    exam_id UUID REFERENCES exams(id) ON DELETE CASCADE,
    biomarker_name VARCHAR(100) NOT NULL,
    normalized_name VARCHAR(100) NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'normal' CHECK (status IN ('normal', 'low', 'high', 'unknown')),
    severity VARCHAR(20) DEFAULT 'none' CHECK (severity IN ('none', 'mild', 'moderate', 'severe', 'critical')),
    reference_min DECIMAL(10,2),
    reference_max DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. TABELA DE RANGES DE REFERÊNCIA
CREATE TABLE IF NOT EXISTS reference_ranges (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    biomarker_name VARCHAR(100) NOT NULL,
    normalized_name VARCHAR(100) NOT NULL,
    min_value DECIMAL(10,2) NOT NULL,
    max_value DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F') OR gender IS NULL),
    age_min INTEGER CHECK (age_min > 0),
    age_max INTEGER CHECK (age_max > age_min),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ÍNDICES PARA PERFORMANCE
-- =====================================================

-- Índices para busca rápida
CREATE INDEX IF NOT EXISTS idx_patients_doctor_id ON patients(doctor_id);
CREATE INDEX IF NOT EXISTS idx_patients_cpf ON patients(cpf);
CREATE INDEX IF NOT EXISTS idx_exams_patient_id ON exams(patient_id);
CREATE INDEX IF NOT EXISTS idx_exams_doctor_id ON exams(doctor_id);
CREATE INDEX IF NOT EXISTS idx_biomarkers_exam_id ON biomarkers(exam_id);
CREATE INDEX IF NOT EXISTS idx_reference_ranges_biomarker ON reference_ranges(biomarker_name, is_active);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) - LGPD COMPLIANCE
-- =====================================================

-- Habilita RLS em todas as tabelas
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE exams ENABLE ROW LEVEL SECURITY;
ALTER TABLE biomarkers ENABLE ROW LEVEL SECURITY;
ALTER TABLE reference_ranges ENABLE ROW LEVEL SECURITY;

-- Política para usuários (médicos só veem seus próprios dados)
CREATE POLICY "Users can only see their own data" ON users
    FOR ALL USING (auth.uid()::text = id::text);

-- Política para pacientes (médicos só veem seus pacientes)
CREATE POLICY "Doctors can only see their patients" ON patients
    FOR ALL USING (doctor_id::text = auth.uid()::text);

-- Política para exames (médicos só veem exames de seus pacientes)
CREATE POLICY "Doctors can only see exams of their patients" ON exams
    FOR ALL USING (doctor_id::text = auth.uid()::text);

-- Política para biomarcadores (médicos só veem biomarcadores de seus exames)
CREATE POLICY "Doctors can only see biomarkers of their exams" ON biomarkers
    FOR ALL USING (
        exam_id IN (
            SELECT id FROM exams WHERE doctor_id::text = auth.uid()::text
        )
    );

-- Política para ranges de referência (todos podem ler)
CREATE POLICY "Reference ranges are readable by all" ON reference_ranges
    FOR SELECT USING (is_active = true);

-- =====================================================
-- DADOS INICIAIS - RANGES DE REFERÊNCIA BRASILEIROS
-- =====================================================

INSERT INTO reference_ranges (biomarker_name, normalized_name, min_value, max_value, unit, gender, age_min, age_max) VALUES
-- Hemoglobina
('Hemoglobina', 'Hb', 12.0, 16.0, 'g/dL', 'F', 18, 65),
('Hemoglobina', 'Hb', 13.0, 17.0, 'g/dL', 'M', 18, 65),
('Hemoglobina', 'Hb', 11.0, 15.0, 'g/dL', 'F', 65, 120),
('Hemoglobina', 'Hb', 12.0, 16.0, 'g/dL', 'M', 65, 120),

-- Hematócrito
('Hematócrito', 'Ht', 36.0, 46.0, '%', 'F', 18, 65),
('Hematócrito', 'Ht', 41.0, 50.0, '%', 'M', 18, 65),

-- Glicose
('Glicose', 'Glu', 70.0, 100.0, 'mg/dL', NULL, 18, 65),
('Glicose', 'Glu', 70.0, 110.0, 'mg/dL', NULL, 65, 120),

-- Creatinina
('Creatinina', 'Cr', 0.6, 1.2, 'mg/dL', 'F', 18, 65),
('Creatinina', 'Cr', 0.8, 1.4, 'mg/dL', 'M', 18, 65),

-- Ureia
('Ureia', 'Ureia', 15.0, 45.0, 'mg/dL', NULL, 18, 65),

-- Leucócitos
('Leucócitos', 'Leuc', 4000.0, 11000.0, 'cel/μL', NULL, 18, 65),

-- Plaquetas
('Plaquetas', 'Plaq', 150000.0, 450000.0, 'cel/μL', NULL, 18, 65);

-- =====================================================
-- FUNÇÕES ÚTEIS
-- =====================================================

-- Função para atualizar timestamp de atualização
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar timestamps
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exams_updated_at BEFORE UPDATE ON exams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VERIFICAÇÃO FINAL
-- =====================================================

-- Verifica se as tabelas foram criadas
SELECT 
    table_name,
    (SELECT count(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns,
    (SELECT count(*) FROM information_schema.triggers WHERE event_object_table = t.table_name) as triggers
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_name IN ('users', 'patients', 'exams', 'biomarkers', 'reference_ranges')
ORDER BY table_name;
