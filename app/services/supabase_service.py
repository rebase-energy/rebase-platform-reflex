"""Supabase service layer for database operations."""
from typing import Any
from datetime import datetime
from app.services.supabase_client import get_supabase_client, is_supabase_configured


class SupabaseService:
    """Service class for Supabase database operations."""
    
    # ==================== WORKSPACE OPERATIONS ====================
    
    @staticmethod
    def get_workspace(slug: str) -> dict | None:
        """Fetch a workspace by its slug."""
        if not is_supabase_configured():
            return None
        client = get_supabase_client()
        if client is None:
            return None
        response = client.table("workspaces").select("*").eq("slug", slug).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    @staticmethod
    def create_workspace(data: dict) -> dict:
        """Create a new workspace."""
        if not is_supabase_configured():
            return {}
        client = get_supabase_client()
        if client is None:
            return {}
        now = datetime.now().isoformat()
        data["created_at"] = now
        data["updated_at"] = now
        response = client.table("workspaces").insert(data).execute()
        return response.data[0] if response.data else {}
    
    @staticmethod
    def update_workspace(workspace_id: str, data: dict) -> dict:
        """Update an existing workspace."""
        if not is_supabase_configured():
            return {}
        client = get_supabase_client()
        if client is None:
            return {}
        data["updated_at"] = datetime.now().isoformat()
        response = client.table("workspaces").update(data).eq("id", workspace_id).execute()
        return response.data[0] if response.data else {}
    
    @staticmethod
    def upsert_workspace(slug: str, data: dict) -> dict:
        """Create or update a workspace by slug."""
        existing = SupabaseService.get_workspace(slug)
        if existing:
            return SupabaseService.update_workspace(existing["id"], data)
        else:
            data["slug"] = slug
            return SupabaseService.create_workspace(data)
    
    # ==================== COLLECTION OPERATIONS ====================
    
    @staticmethod
    def get_collections(workspace_id: str) -> list[dict]:
        """Fetch all collections for a workspace."""
        if not is_supabase_configured():
            return []
        client = get_supabase_client()
        if client is None:
            return []
        response = client.table("collections").select("*").eq("workspace_id", workspace_id).execute()
        return response.data or []
    
    @staticmethod
    def get_collection(collection_id: str) -> dict | None:
        """Fetch a single collection by ID."""
        if not is_supabase_configured():
            return None
        client = get_supabase_client()
        if client is None:
            return None
        response = client.table("collections").select("*").eq("id", collection_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    @staticmethod
    def create_collection(data: dict) -> dict:
        """Create a new collection."""
        if not is_supabase_configured():
            return {}
        client = get_supabase_client()
        if client is None:
            return {}
        now = datetime.now().isoformat()
        data["created_at"] = now
        response = client.table("collections").insert(data).execute()
        return response.data[0] if response.data else {}
    
    @staticmethod
    def update_collection(collection_id: str, data: dict) -> dict:
        """Update an existing collection."""
        if not is_supabase_configured():
            return {}
        client = get_supabase_client()
        if client is None:
            return {}
        response = client.table("collections").update(data).eq("id", collection_id).execute()
        return response.data[0] if response.data else {}
    
    @staticmethod
    def delete_collection(collection_id: str) -> bool:
        """Delete a collection by ID.
        
        Note: This only deletes the collection and its entity mappings.
        The entities themselves are preserved.
        """
        if not is_supabase_configured():
            return False
        client = get_supabase_client()
        if client is None:
            return False
        # The collection_entities mappings are automatically deleted via ON DELETE CASCADE
        client.table("collections").delete().eq("id", collection_id).execute()
        return True
    
    @staticmethod
    def upsert_collection(collection_id: str, data: dict) -> dict:
        """Create or update a collection by ID."""
        existing = SupabaseService.get_collection(collection_id)
        if existing:
            return SupabaseService.update_collection(collection_id, data)
        else:
            data["id"] = collection_id
            return SupabaseService.create_collection(data)
    
    # ==================== ENTITY OPERATIONS ====================
    
    @staticmethod
    def get_entities_for_workspace(workspace_id: str) -> list[dict]:
        """Fetch all entities for a workspace."""
        if not is_supabase_configured():
            return []
        client = get_supabase_client()
        if client is None:
            return []
        response = client.table("entities").select("*").eq("workspace_id", workspace_id).execute()
        return response.data or []
    
    @staticmethod
    def get_entities_by_type(entity_type: str, workspace_id: str | None = None) -> list[dict]:
        """Fetch all entities of a specific type, optionally filtered by workspace."""
        if not is_supabase_configured():
            return []
        client = get_supabase_client()
        if client is None:
            return []
        query = client.table("entities").select("*").eq("entity_type", entity_type)
        if workspace_id:
            query = query.eq("workspace_id", workspace_id)
        response = query.execute()
        return response.data or []
    
    @staticmethod
    def get_entity(entity_id: str) -> dict | None:
        """Fetch a single entity by ID."""
        if not is_supabase_configured():
            return None
        client = get_supabase_client()
        if client is None:
            return None
        response = client.table("entities").select("*").eq("id", entity_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    @staticmethod
    def create_entity(data: dict) -> dict:
        """Create a new entity."""
        if not is_supabase_configured():
            return {}
        client = get_supabase_client()
        if client is None:
            return {}
        now = datetime.now().isoformat()
        data["created_at"] = now
        data["updated_at"] = now
        response = client.table("entities").insert(data).execute()
        return response.data[0] if response.data else {}
    
    @staticmethod
    def update_entity(entity_id: str, data: dict) -> dict:
        """Update an existing entity."""
        if not is_supabase_configured():
            return {}
        client = get_supabase_client()
        if client is None:
            return {}
        data["updated_at"] = datetime.now().isoformat()
        response = client.table("entities").update(data).eq("id", entity_id).execute()
        return response.data[0] if response.data else {}
    
    @staticmethod
    def delete_entity(entity_id: str) -> bool:
        """Delete an entity by ID.
        
        Note: This also removes the entity from all collections via ON DELETE CASCADE.
        """
        if not is_supabase_configured():
            return False
        client = get_supabase_client()
        if client is None:
            return False
        client.table("entities").delete().eq("id", entity_id).execute()
        return True
    
    @staticmethod
    def upsert_entity(entity_id: str, data: dict) -> dict:
        """Create or update an entity by ID."""
        existing = SupabaseService.get_entity(entity_id)
        if existing:
            return SupabaseService.update_entity(entity_id, data)
        else:
            data["id"] = entity_id
            return SupabaseService.create_entity(data)
    
    @staticmethod
    def bulk_upsert_entities(entities: list[dict]) -> list[dict]:
        """Bulk create or update entities."""
        if not is_supabase_configured():
            return []
        client = get_supabase_client()
        if client is None:
            return []
        now = datetime.now().isoformat()
        for entity in entities:
            entity["updated_at"] = now
            if "created_at" not in entity:
                entity["created_at"] = now
        response = client.table("entities").upsert(entities).execute()
        return response.data or []
    
    # ==================== COLLECTION-ENTITY MAPPING OPERATIONS ====================
    
    @staticmethod
    def get_entities_for_collection(collection_id: str) -> list[dict]:
        """Fetch all entities that belong to a collection."""
        if not is_supabase_configured():
            return []
        client = get_supabase_client()
        if client is None:
            return []
        
        # Get entity IDs from junction table
        mappings = client.table("collection_entities").select("entity_id").eq("collection_id", collection_id).execute()
        if not mappings.data:
            return []
        
        entity_ids = [m["entity_id"] for m in mappings.data]
        if not entity_ids:
            return []
        
        # Fetch the actual entities
        response = client.table("entities").select("*").in_("id", entity_ids).execute()
        return response.data or []
    
    @staticmethod
    def get_entity_ids_for_collection(collection_id: str) -> list[str]:
        """Fetch all entity IDs that belong to a collection."""
        if not is_supabase_configured():
            return []
        client = get_supabase_client()
        if client is None:
            return []
        
        response = client.table("collection_entities").select("entity_id").eq("collection_id", collection_id).execute()
        if not response.data:
            return []
        return [m["entity_id"] for m in response.data]
    
    @staticmethod
    def get_collections_for_entity(entity_id: str) -> list[str]:
        """Fetch all collection IDs that contain an entity."""
        if not is_supabase_configured():
            return []
        client = get_supabase_client()
        if client is None:
            return []
        
        response = client.table("collection_entities").select("collection_id").eq("entity_id", entity_id).execute()
        if not response.data:
            return []
        return [m["collection_id"] for m in response.data]
    
    @staticmethod
    def add_entity_to_collection(collection_id: str, entity_id: str) -> bool:
        """Add an entity to a collection."""
        if not is_supabase_configured():
            return False
        client = get_supabase_client()
        if client is None:
            return False
        
        try:
            client.table("collection_entities").insert({
                "collection_id": collection_id,
                "entity_id": entity_id,
                "added_at": datetime.now().isoformat(),
            }).execute()
            return True
        except Exception:
            # Might already exist (duplicate key)
            return False
    
    @staticmethod
    def remove_entity_from_collection(collection_id: str, entity_id: str) -> bool:
        """Remove an entity from a collection."""
        if not is_supabase_configured():
            return False
        client = get_supabase_client()
        if client is None:
            return False
        
        client.table("collection_entities").delete().eq("collection_id", collection_id).eq("entity_id", entity_id).execute()
        return True
    
    @staticmethod
    def set_collection_entities(collection_id: str, entity_ids: list[str]) -> bool:
        """Set the entities for a collection (replaces existing mappings)."""
        if not is_supabase_configured():
            return False
        client = get_supabase_client()
        if client is None:
            return False
        
        # Delete existing mappings
        client.table("collection_entities").delete().eq("collection_id", collection_id).execute()
        
        # Insert new mappings
        if entity_ids:
            now = datetime.now().isoformat()
            mappings = [
                {"collection_id": collection_id, "entity_id": eid, "added_at": now}
                for eid in entity_ids
            ]
            client.table("collection_entities").insert(mappings).execute()
        
        return True
    
    @staticmethod
    def get_entity_count_for_collection(collection_id: str) -> int:
        """Get the count of entities in a collection."""
        if not is_supabase_configured():
            return 0
        client = get_supabase_client()
        if client is None:
            return 0
        
        response = client.table("collection_entities").select("entity_id", count="exact").eq("collection_id", collection_id).execute()
        return response.count or 0
