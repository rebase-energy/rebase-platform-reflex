-- Supabase Schema for Rebase Platform
-- Run this SQL in Supabase SQL Editor: https://supabase.com/dashboard/project/vycbrbohhqywmtgssfbe/sql

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Table: workspaces
-- Stores workspace configuration and settings
-- ============================================
CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    logo_data_url TEXT DEFAULT NULL,
    logo_url TEXT DEFAULT NULL,
    theme TEXT DEFAULT 'Dark',
    accent_color TEXT DEFAULT '#10b981',
    sidebar_collapsed BOOLEAN DEFAULT FALSE,
    sidebar_width INTEGER DEFAULT 256,
    default_collection_id TEXT DEFAULT NULL,  -- The collection to show on login/start
    menu_item_visibility JSONB DEFAULT '{
        "Projects": true,
        "Workflows": true,
        "Dashboards": true,
        "Notebooks": true,
        "Models": true,
        "Datasets": true,
        "Notifications": true,
        "Reports": true
    }'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add default_collection_id column if it doesn't exist (for existing tables)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='workspaces' AND column_name='default_collection_id') THEN
        ALTER TABLE workspaces ADD COLUMN default_collection_id TEXT DEFAULT NULL;
    END IF;
END $$;

-- Add logo_data_url column if it doesn't exist (for existing tables)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='workspaces' AND column_name='logo_data_url') THEN
        ALTER TABLE workspaces ADD COLUMN logo_data_url TEXT DEFAULT NULL;
    END IF;
END $$;

-- Add logo_url column if it doesn't exist (for existing tables)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='workspaces' AND column_name='logo_url') THEN
        ALTER TABLE workspaces ADD COLUMN logo_url TEXT DEFAULT NULL;
    END IF;
END $$;

-- Create index on slug for faster lookups
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON workspaces(slug);

-- ============================================
-- Supabase Storage: Workspace logos bucket
-- Stores workspace logos in Supabase Storage and persists URL in workspaces.logo_url
-- ============================================
-- This is safe to run multiple times.
INSERT INTO storage.buckets (id, name, public)
VALUES ('workspace-logos', 'workspace-logos', TRUE)
ON CONFLICT (id) DO UPDATE SET public = EXCLUDED.public;

-- ============================================
-- Grants (required in addition to RLS policies)
-- If you use the anon key (no auth), PostgREST runs as role "anon".
-- These GRANTs allow that role to access tables; the RLS policies below then allow the operations.
-- ============================================
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO anon, authenticated, service_role;

-- ============================================
-- Storage policies for workspace logos (no auth / anon access)
-- Note: This makes uploads possible without login. If you want stricter control,
-- use the service_role key server-side or add auth.
-- ============================================
-- NOTE:
-- The SQL in this repo is intended to be runnable via a normal DB user (e.g. postgres.<project-ref>)
-- using `supabase_apply_schema.py`. That user is NOT the owner of `storage.objects`, so statements
-- like `ALTER TABLE storage.objects ...` or `CREATE POLICY ON storage.objects ...` may fail with:
--   "must be owner of table objects"
--
-- Recommended approach for this app:
-- - Keep the bucket PUBLIC (done above)
-- - Use a server-side key (service_role) for Storage uploads from the Reflex backend.
--
-- If you want to enforce public/anon uploads via Storage RLS, create the policies using an owner
-- context (e.g. Supabase SQL editor as the elevated role) or a proper migration pipeline.

-- ============================================
-- Table: entities
-- Stores entity data (TimeSeries, Sites, Assets)
-- Entities exist independently of collections
-- ============================================
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL DEFAULT 'TimeSeries',
    data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_entities_workspace ON entities(workspace_id);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);

-- ============================================
-- Table: collections
-- Stores collection configurations
-- ============================================
CREATE TABLE IF NOT EXISTS collections (
    id TEXT PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    object_type TEXT NOT NULL DEFAULT 'TimeSeries',
    attributes JSONB DEFAULT '[]'::jsonb,
    emoji TEXT DEFAULT '📋',
    view_type TEXT DEFAULT 'table',
    created_by TEXT DEFAULT '',
    is_favorite BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_collections_workspace ON collections(workspace_id);
CREATE INDEX IF NOT EXISTS idx_collections_object_type ON collections(object_type);

-- ============================================
-- Table: collection_entities (Junction Table)
-- Maps many-to-many relationship between collections and entities
-- When a collection is deleted, only the mapping is removed, not the entity
-- ============================================
CREATE TABLE IF NOT EXISTS collection_entities (
    collection_id TEXT REFERENCES collections(id) ON DELETE CASCADE,
    entity_id TEXT REFERENCES entities(id) ON DELETE CASCADE,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (collection_id, entity_id)
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_collection_entities_collection ON collection_entities(collection_id);
CREATE INDEX IF NOT EXISTS idx_collection_entities_entity ON collection_entities(entity_id);

-- ============================================
-- Row Level Security (RLS) - Allow all for service role
-- Since we're using service role key, allow all operations
-- ============================================

-- Enable RLS on all tables
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE collections ENABLE ROW LEVEL SECURITY;
ALTER TABLE collection_entities ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for clean re-runs)
DROP POLICY IF EXISTS "Allow all operations on workspaces" ON workspaces;
DROP POLICY IF EXISTS "Allow all operations on entities" ON entities;
DROP POLICY IF EXISTS "Allow all operations on collections" ON collections;
DROP POLICY IF EXISTS "Allow all operations on collection_entities" ON collection_entities;

-- Create policies that allow all operations (since we're using service role key)
DROP POLICY IF EXISTS "Allow all operations on workspaces" ON workspaces;
CREATE POLICY "Allow all operations on workspaces" ON workspaces
    FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all operations on entities" ON entities;
CREATE POLICY "Allow all operations on entities" ON entities
    FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all operations on collections" ON collections;
CREATE POLICY "Allow all operations on collections" ON collections
    FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow all operations on collection_entities" ON collection_entities;
CREATE POLICY "Allow all operations on collection_entities" ON collection_entities
    FOR ALL USING (true) WITH CHECK (true);

-- Also grant permissions to authenticated and anon roles (for API access)
GRANT ALL ON workspaces TO authenticated, anon;
GRANT ALL ON entities TO authenticated, anon;
GRANT ALL ON collections TO authenticated, anon;
GRANT ALL ON collection_entities TO authenticated, anon;

-- ============================================
-- Function to update updated_at timestamp
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at columns
DROP TRIGGER IF EXISTS update_workspaces_updated_at ON workspaces;
CREATE TRIGGER update_workspaces_updated_at
    BEFORE UPDATE ON workspaces
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_entities_updated_at ON entities;
CREATE TRIGGER update_entities_updated_at
    BEFORE UPDATE ON entities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
