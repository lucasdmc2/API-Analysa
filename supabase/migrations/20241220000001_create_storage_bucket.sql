-- =====================================================
-- CRIAÇÃO DO BUCKET DE STORAGE PARA EXAMES MÉDICOS
-- =====================================================

-- Insere o bucket na tabela storage.buckets
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'exames-medicos',
    'exames-medicos',
    false, -- bucket privado por padrão
    52428800, -- 50MB em bytes
    ARRAY['application/pdf', 'image/jpeg', 'image/png', 'image/tiff', 'image/bmp']
) ON CONFLICT (id) DO NOTHING;

-- Cria política RLS para o bucket
CREATE POLICY "Users can upload their own exam files" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'exames-medicos' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can view their own exam files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'exames-medicos' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can update their own exam files" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'exames-medicos' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can delete their own exam files" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'exames-medicos' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Verifica se o bucket foi criado
SELECT 
    id,
    name,
    public,
    file_size_limit,
    created_at
FROM storage.buckets 
WHERE id = 'exames-medicos';
