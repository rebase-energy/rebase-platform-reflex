import reflex as rx
import httpx
from typing import TypedDict, Literal
from datetime import datetime
from app.services.timedb_api import TimeDBAPI


# Object Types that can be stored in collections
ObjectType = Literal["TimeSeries", "Site", "Asset"]


# TimeSeries entity
class TimeSeries(TypedDict):
    id: str
    name: str
    description: str
    unit: str
    site_name: str
    timestamp: str
    value: float
    type: str  # "actual", "forecast", "capacity"
    tags: list[str]


# Site entity
class Site(TypedDict):
    id: str
    name: str
    description: str
    site_type: str  # "Wind", "Solar", "Hydro", "Load"
    capacity: float
    status: str  # "Active", "Inactive", "Maintenance"
    location: str
    tags: list[str]


# Asset entity
class Asset(TypedDict):
    id: str
    name: str
    description: str
    asset_type: str  # "Turbine", "Panel", "Transformer", etc.
    site_id: str
    site_name: str
    status: str  # "Active", "Inactive", "Maintenance"
    tags: list[str]


# Entity State Management
class EntitiesState(rx.State):
    """State management for entities (TimeSeries, Sites, Assets, etc.)."""
    
    # Entity data storage (collection_id -> list of entities)
    _time_series_entities: dict[str, list[TimeSeries]] = {}
    
    # Site and Asset entities (workspace-level, not per-collection)
    _site_entities: list[Site] = []
    _asset_entities: list[Asset] = []
    
    # Track if entities have been loaded from DB
    _entities_loaded: bool = False
    
    # Selected object type for entity browsing
    selected_object_type: str = ""
    
    # Loading state
    is_loading: bool = False
    
    # API configuration
    timedb_api_key: str = ""  # Optional API key for authentication
    
    # Search query for filtering entities
    entity_search_query: str = ""
    
    def _load_entities_from_db(self):
        """Load entities from Supabase and organize by collection."""
        if self._entities_loaded:
            return
        
        try:
            from app.services.supabase_service import SupabaseService
            
            # Get workspace
            workspace = SupabaseService.get_workspace("rebase-energy")
            if not workspace:
                self._entities_loaded = True
                return
            
            workspace_id = workspace.get("id", "")
            
            # Load all TimeSeries entities for this workspace
            db_timeseries = SupabaseService.get_entities_by_type("TimeSeries", workspace_id)
            
            # Create a mapping of entity_id -> entity for TimeSeries
            entity_map: dict[str, TimeSeries] = {}
            for db_entity in db_timeseries:
                entity_data = db_entity.get("data", {})
                entity: TimeSeries = {
                    "id": db_entity.get("id", ""),
                    "name": entity_data.get("name", ""),
                    "description": entity_data.get("description", ""),
                    "unit": entity_data.get("unit", ""),
                    "site_name": entity_data.get("site_name", ""),
                    "timestamp": entity_data.get("timestamp", ""),
                    "value": entity_data.get("value", 0.0),
                    "type": entity_data.get("type", "actual"),
                    "tags": entity_data.get("tags", []),
                }
                entity_map[entity["id"]] = entity
            
            # Get all collections and their entity mappings
            collections = SupabaseService.get_collections(workspace_id)
            entities_by_collection: dict[str, list[TimeSeries]] = {}
            
            for collection in collections:
                collection_id = collection.get("id", "")
                entity_ids = SupabaseService.get_entity_ids_for_collection(collection_id)
                entities_by_collection[collection_id] = [
                    entity_map[eid] for eid in entity_ids if eid in entity_map
                ]
            
            self._time_series_entities = entities_by_collection
            
            # Load Site entities
            db_sites = SupabaseService.get_entities_by_type("Site", workspace_id)
            sites: list[Site] = []
            for db_entity in db_sites:
                entity_data = db_entity.get("data", {})
                site: Site = {
                    "id": db_entity.get("id", ""),
                    "name": entity_data.get("name", ""),
                    "description": entity_data.get("description", ""),
                    "site_type": entity_data.get("site_type", "Wind"),
                    "capacity": entity_data.get("capacity", 0.0),
                    "status": entity_data.get("status", "Active"),
                    "location": entity_data.get("location", ""),
                    "tags": entity_data.get("tags", []),
                }
                sites.append(site)
            self._site_entities = sites
            
            # Load Asset entities
            db_assets = SupabaseService.get_entities_by_type("Asset", workspace_id)
            assets: list[Asset] = []
            for db_entity in db_assets:
                entity_data = db_entity.get("data", {})
                asset: Asset = {
                    "id": db_entity.get("id", ""),
                    "name": entity_data.get("name", ""),
                    "description": entity_data.get("description", ""),
                    "asset_type": entity_data.get("asset_type", ""),
                    "site_id": entity_data.get("site_id", ""),
                    "site_name": entity_data.get("site_name", ""),
                    "status": entity_data.get("status", "Active"),
                    "tags": entity_data.get("tags", []),
                }
                assets.append(asset)
            self._asset_entities = assets
            
            self._entities_loaded = True
        except Exception as e:
            print(f"Failed to load entities from database: {e}")
            self._entities_loaded = True
    
    def _save_entity_to_db(self, entity: TimeSeries, collection_id: str):
        """Save a single entity to Supabase and add it to a collection."""
        try:
            from app.services.supabase_service import SupabaseService
            
            # Get workspace
            workspace = SupabaseService.get_workspace("rebase-energy")
            if not workspace:
                return
            
            workspace_id = workspace.get("id", "")
            
            # Save the entity
            data = {
                "workspace_id": workspace_id,
                "entity_type": "TimeSeries",
                "data": {
                    "name": entity.get("name", ""),
                    "description": entity.get("description", ""),
                    "unit": entity.get("unit", ""),
                    "site_name": entity.get("site_name", ""),
                    "timestamp": entity.get("timestamp", ""),
                    "value": entity.get("value", 0.0),
                    "type": entity.get("type", "actual"),
                    "tags": entity.get("tags", []),
                },
            }
            SupabaseService.upsert_entity(entity.get("id", ""), data)
            
            # Add entity to collection
            if collection_id:
                SupabaseService.add_entity_to_collection(collection_id, entity.get("id", ""))
        except Exception as e:
            print(f"Failed to save entity to database: {e}")
    
    def _save_entities_to_db(self, collection_id: str):
        """Save all entities for a collection to Supabase."""
        try:
            from app.services.supabase_service import SupabaseService
            
            # Get workspace
            workspace = SupabaseService.get_workspace("rebase-energy")
            if not workspace:
                return
            
            workspace_id = workspace.get("id", "")
            
            entities = self._time_series_entities.get(collection_id, [])
            db_entities = []
            entity_ids = []
            
            for entity in entities:
                entity_id = entity.get("id", "")
                entity_ids.append(entity_id)
                
                db_entity = {
                    "id": entity_id,
                    "workspace_id": workspace_id,
                    "entity_type": "TimeSeries",
                    "data": {
                        "name": entity.get("name", ""),
                        "description": entity.get("description", ""),
                        "unit": entity.get("unit", ""),
                        "site_name": entity.get("site_name", ""),
                        "timestamp": entity.get("timestamp", ""),
                        "value": entity.get("value", 0.0),
                        "type": entity.get("type", "actual"),
                        "tags": entity.get("tags", []),
                    },
                }
                db_entities.append(db_entity)
            
            # Save entities
            if db_entities:
                SupabaseService.bulk_upsert_entities(db_entities)
            
            # Update collection-entity mappings
            if collection_id and entity_ids:
                SupabaseService.set_collection_entities(collection_id, entity_ids)
        except Exception as e:
            print(f"Failed to save entities to database: {e}")
    
    @rx.event
    def on_load(self):
        """Initialize entity storage for default collections."""
        # Try to load from database first
        self._load_entities_from_db()
        
        # If nothing loaded, initialize with defaults
        if not self._time_series_entities:
            # Initialize empty storage for default collections
            self._time_series_entities["default-timeseries"] = []
            
            # Create TimeSeries entities for esett-data collection (4 cards = 4 time series)
            esett_entities = [
                {
                    "id": "blackfjallet",
                    "name": "Blackfjället",
                    "description": "Blackfjället wind farm",
                    "unit": "MW",
                    "site_name": "Blackfjället",
                    "timestamp": datetime.now().isoformat(),
                    "value": 90.2,
                    "type": "capacity",
                    "tags": [],
                },
                {
                    "id": "ranasjo",
                    "name": "Ranasjo",
                    "description": "Ranasjo wind farm",
                    "unit": "MW",
                    "site_name": "Ranasjo",
                    "timestamp": datetime.now().isoformat(),
                    "value": 150.0,
                    "type": "capacity",
                    "tags": [],
                },
                {
                    "id": "storberget",
                    "name": "Storberget",
                    "description": "Storberget wind farm",
                    "unit": "MW",
                    "site_name": "Storberget",
                    "timestamp": datetime.now().isoformat(),
                    "value": 75.5,
                    "type": "capacity",
                    "tags": [],
                },
                {
                    "id": "vindpark-nord",
                    "name": "Vindpark Nord",
                    "description": "Vindpark Nord wind farm",
                    "unit": "MW",
                    "site_name": "Northern Region",
                    "timestamp": datetime.now().isoformat(),
                    "value": 200.0,
                    "type": "capacity",
                    "tags": [],
                },
            ]
            self._time_series_entities["esett-data"] = esett_entities
            
            # Save default entities to database
            self._save_entities_to_db("esett-data")
    
    @rx.event
    def on_load_entity_page(self):
        """Initialize entities and set active entity type from route."""
        # Reset flag to force fresh load from Supabase
        self._entities_loaded = False
        # Load entities from Supabase
        self._load_entities_from_db()
        
        # Get entity name from route params
        try:
            entity_name = self.router.url.params.get("entity_name", "")  # type: ignore
        except Exception:
            entity_name = ""
        
        # Fallback: extract from path if params didn't work
        if not entity_name:
            try:
                path = self.router.url.path  # type: ignore
                if "/entities/" in path:
                    parts = path.split("/entities/")
                    if len(parts) > 1:
                        entity_name = parts[1].split("/")[0]
            except Exception:
                pass
        
        if entity_name:
            # Map URL entity names to internal object types
            entity_type_map = {
                "timeseries": "TimeSeries",
                "sites": "Sites",
                "assets": "Assets",
            }
            object_type = entity_type_map.get(entity_name.lower(), entity_name)
            self.selected_object_type = object_type
            self.is_loading = False
    
    @rx.var
    def all_time_series_entities(self) -> list[TimeSeries]:
        """Get all TimeSeries entities from all collections."""
        all_items = []
        for collection_id, items in self._time_series_entities.items():
            all_items.extend(items)
        # Apply search filter
        if self.entity_search_query:
            query = self.entity_search_query.lower()
            all_items = [
                item for item in all_items
                if query in item.get("name", "").lower()
                or query in item.get("description", "").lower()
                or query in item.get("unit", "").lower()
                or query in item.get("site_name", "").lower()
                or query in str(item.get("value", "")).lower()
                or query in item.get("type", "").lower()
            ]
        return all_items
    
    @rx.var
    def time_series_entities_by_collection(self) -> dict[str, list[TimeSeries]]:
        """Get all time series entities organized by collection_id."""
        return self._time_series_entities
    
    @rx.var
    def all_site_entities(self) -> list[Site]:
        """Get all Site entities with search filter applied."""
        sites = self._site_entities
        if self.entity_search_query:
            query = self.entity_search_query.lower()
            sites = [
                site for site in sites
                if query in site.get("name", "").lower()
                or query in site.get("description", "").lower()
                or query in site.get("site_type", "").lower()
                or query in site.get("location", "").lower()
                or query in site.get("status", "").lower()
            ]
        return sites
    
    @rx.var
    def all_asset_entities(self) -> list[Asset]:
        """Get all Asset entities with search filter applied."""
        assets = self._asset_entities
        if self.entity_search_query:
            query = self.entity_search_query.lower()
            assets = [
                asset for asset in assets
                if query in asset.get("name", "").lower()
                or query in asset.get("description", "").lower()
                or query in asset.get("asset_type", "").lower()
                or query in asset.get("site_name", "").lower()
                or query in asset.get("status", "").lower()
            ]
        return assets
    
    @rx.var
    def collection_entry_counts_dict(self) -> dict[str, int]:
        """Get entry counts for each collection (collection_id -> count)."""
        return {
            collection_id: len(entities)
            for collection_id, entities in self._time_series_entities.items()
        }

    @rx.var
    def active_object_type(self) -> str:
        """Get the active entity type."""
        return self.selected_object_type
    
    @rx.event
    def select_object_type(self, object_type: str):
        """Navigate to an entity type page."""
        self.selected_object_type = object_type
        entity_name_map = {
            "TimeSeries": "timeseries",
            "Sites": "sites",
            "Assets": "assets",
        }
        entity_name = entity_name_map.get(object_type, object_type.lower())
        workspace_slug = "rebase-energy"
        return rx.redirect(f"/{workspace_slug}/entities/{entity_name}")
    
    @rx.event
    def load_entity_page(self, object_type: str):
        """Set entity type and load data without redirecting."""
        self.selected_object_type = object_type
        
        if object_type == "TimeSeries":
            self.is_loading = True
            return self.load_timeseries_async()
        
        self.is_loading = False
    
    @rx.event
    def load_timeseries_async(self):
        """Load time series entities asynchronously."""
        yield
        self._load_timeseries_data()
    
    def _load_timeseries_data(self):
        """Internal method to load time series data from API."""
        try:
            api = TimeDBAPI(api_key=self.timedb_api_key if self.timedb_api_key else None)
            timeseries_map = api.list_timeseries()
            
            items: list[TimeSeries] = []
            for series_id, value in timeseries_map.items():
                # Handle different response formats
                if isinstance(value, dict):
                    # If value is a dict, extract series_key and metadata
                    series_key = value.get("series_key", str(series_id))
                    metadata = value.get("metadata", {})
                    
                    # Extract name, description, and unit from metadata (or top-level if available)
                    # Priority: metadata fields > top-level fields > fallback
                    name = (
                        metadata.get("name") or 
                        value.get("name") or 
                        series_key.replace("_", " ").title()
                    )
                    description = (
                        metadata.get("description") or 
                        value.get("description") or 
                        ""
                    )
                    unit = (
                        metadata.get("unit") or 
                        value.get("unit") or 
                        "kW"
                    )
                else:
                    # If value is a string (series_key)
                    series_key = str(value)
                    name = series_key.replace("_", " ").title()
                    description = ""
                    unit = "kW"
                
                item: TimeSeries = {
                    "id": series_id,
                    "name": name,
                    "description": description,
                    "unit": unit,
                    "site_name": "",
                    "timestamp": datetime.now().isoformat(),
                    "value": 0.0,
                    "type": "actual",
                    "tags": [],
                }
                items.append(item)
            
            # Store in default collection cache for object type browsing
            default_collection_id = "default-timeseries"
            # Initialize if not exists
            if default_collection_id not in self._time_series_entities:
                self._time_series_entities[default_collection_id] = []
            self._time_series_entities[default_collection_id] = items
            
            # Also ensure esett-data is initialized
            if "esett-data" not in self._time_series_entities:
                self._time_series_entities["esett-data"] = []
            
            self.is_loading = False
        except Exception as e:
            self.is_loading = False
            print(f"Failed to load time series: {e}")
    
    @rx.event
    def refresh_timeseries_entities(self):
        """Refresh the time series entities from the API."""
        self.is_loading = True
        yield
        self._load_timeseries_data()
        item_count = len(self._time_series_entities.get("default-timeseries", []))
        yield rx.toast.success(f"Refreshed {item_count} time series")
    
    @rx.event
    def create_entity(self, form_data: dict):
        """Create a new entity based on the active object type."""
        import uuid
        
        name = form_data.get("name", "").strip()
        if not name:
            return rx.toast.error("Name is required")
        
        description = form_data.get("description", "").strip()
        entity_type = self.selected_object_type
        
        try:
            entity_id = str(uuid.uuid4())
            
            if entity_type == "TimeSeries":
                unit = form_data.get("unit", "kW").strip()
                new_entity: TimeSeries = {
                    "id": entity_id,
                    "name": name,
                    "description": description,
                    "unit": unit,
                    "site_name": "",
                    "timestamp": datetime.now().isoformat(),
                    "value": 0.0,
                    "type": "actual",
                    "tags": [],
                }
                # Add to local cache
                target_collection_id = "default-timeseries"
                if target_collection_id not in self._time_series_entities:
                    self._time_series_entities[target_collection_id] = []
                self._time_series_entities[target_collection_id].append(new_entity)
                # Save to Supabase
                self._save_entity_to_db(new_entity, target_collection_id)
                
            elif entity_type == "Sites":
                site_type = form_data.get("site_type", "Wind").strip()
                capacity = float(form_data.get("capacity", 0) or 0)
                location = form_data.get("location", "").strip()
                new_site: Site = {
                    "id": entity_id,
                    "name": name,
                    "description": description,
                    "site_type": site_type,
                    "capacity": capacity,
                    "status": "Active",
                    "location": location,
                    "tags": [],
                }
                self._site_entities.append(new_site)
                # Save to Supabase
                self._save_site_to_db(new_site)
                
            elif entity_type == "Assets":
                asset_type = form_data.get("asset_type", "").strip()
                site_name = form_data.get("site_name", "").strip()
                new_asset: Asset = {
                    "id": entity_id,
                    "name": name,
                    "description": description,
                    "asset_type": asset_type,
                    "site_id": "",
                    "site_name": site_name,
                    "status": "Active",
                    "tags": [],
                }
                self._asset_entities.append(new_asset)
                # Save to Supabase
                self._save_asset_to_db(new_asset)
            else:
                return rx.toast.error(f"Unknown entity type: {entity_type}")
            
            # Close modal
            from app.states.collections import CollectionsState
            yield CollectionsState.close_add_item_modal
            
            return rx.toast.success(f"{entity_type} '{name}' created successfully!")
            
        except Exception as e:
            error_msg = str(e)
            return rx.toast.error(f"Failed to create {entity_type}: {error_msg}")
    
    def _save_site_to_db(self, site: Site):
        """Save a Site entity to Supabase."""
        try:
            from app.services.supabase_service import SupabaseService
            
            workspace = SupabaseService.get_workspace("rebase-energy")
            if not workspace:
                print("Failed to save site: workspace not found")
                return
            
            workspace_id = workspace.get("id", "")
            entity_id = site["id"]
            
            db_entity = {
                "workspace_id": workspace_id,
                "entity_type": "Site",
                "data": {
                    "name": site.get("name", ""),
                    "description": site.get("description", ""),
                    "site_type": site.get("site_type", ""),
                    "capacity": site.get("capacity", 0),
                    "status": site.get("status", "Active"),
                    "location": site.get("location", ""),
                    "tags": site.get("tags", []),
                },
            }
            result = SupabaseService.upsert_entity(entity_id, db_entity)
            print(f"Saved site to database: {result}")
        except Exception as e:
            print(f"Failed to save site to database: {e}")
    
    def _save_asset_to_db(self, asset: Asset):
        """Save an Asset entity to Supabase."""
        try:
            from app.services.supabase_service import SupabaseService
            
            workspace = SupabaseService.get_workspace("rebase-energy")
            if not workspace:
                print("Failed to save asset: workspace not found")
                return
            
            workspace_id = workspace.get("id", "")
            entity_id = asset["id"]
            
            db_entity = {
                "workspace_id": workspace_id,
                "entity_type": "Asset",
                "data": {
                    "name": asset.get("name", ""),
                    "description": asset.get("description", ""),
                    "asset_type": asset.get("asset_type", ""),
                    "site_id": asset.get("site_id", ""),
                    "site_name": asset.get("site_name", ""),
                    "status": asset.get("status", "Active"),
                    "tags": asset.get("tags", []),
                },
            }
            result = SupabaseService.upsert_entity(entity_id, db_entity)
            print(f"Saved asset to database: {result}")
        except Exception as e:
            print(f"Failed to save asset to database: {e}")
    
    @rx.event
    def set_entity_search_query(self, query: str):
        """Set the search query for filtering entities."""
        self.entity_search_query = query

