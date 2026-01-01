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

-- Create index on slug for faster lookups
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON workspaces(slug);

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
-- Row Level Security (RLS) - DISABLED for single user
-- Since we're not using authentication, we disable RLS
-- ============================================

-- Enable RLS on all tables
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE collections ENABLE ROW LEVEL SECURITY;
ALTER TABLE collection_entities ENABLE ROW LEVEL SECURITY;

-- Create policies that allow all operations (since we're using service role key)
CREATE POLICY "Allow all operations on workspaces" ON workspaces
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on entities" ON entities
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on collections" ON collections
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on collection_entities" ON collection_entities
    FOR ALL USING (true) WITH CHECK (true);

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
