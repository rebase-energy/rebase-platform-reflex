import reflex as rx
import httpx
from typing import TypedDict, Literal
from datetime import datetime
from app.services.timedb_api import TimeDBAPI


# Object Types that can be stored in collections
ObjectType = Literal["TimeSeries", "Site", "Asset"]


# TimeSeries entity (example of an entity type)
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


# Entity State Management
class EntitiesState(rx.State):
    """State management for entities (TimeSeries, Sites, Assets, etc.)."""
    
    # Entity data storage (collection_id -> list of entities)
    _time_series_entities: dict[str, list[TimeSeries]] = {}
    
    # Selected object type for entity browsing
    selected_object_type: str = ""
    
    # Loading state
    is_loading: bool = False
    
    # API configuration
    timedb_api_key: str = ""  # Optional API key for authentication
    
    # Search query for filtering entities
    entity_search_query: str = ""
    
    @rx.event
    def on_load(self):
        """Initialize entity storage for default collections."""
        # Initialize empty storage for default collections
        self._time_series_entities["default-timeseries"] = []
        
        # Create TimeSeries entities for esett-data collection (2 cards = 2 time series)
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
        ]
        self._time_series_entities["esett-data"] = esett_entities
    
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
    
    @rx.event
    def select_object_type(self, object_type: str):
        """Select an object type for entity browsing."""
        # Set selection immediately for instant feedback
        self.selected_object_type = object_type
        
        # Clear other selections
        from app.states.collections import CollectionsState
        from app.states.workspace import WorkspaceState
        CollectionsState.selected_collection_id = ""
        WorkspaceState.selected_menu_item = ""
        
        # Load entities from API when selecting TimeSeries object type
        if object_type == "TimeSeries":
            self.is_loading = True
            return self.load_timeseries_async()
        
        # For other object types, clear loading state
        self.is_loading = False
    
    @rx.event
    def load_timeseries_async(self):
        """Load time series entities asynchronously."""
        # Yield to allow UI to update with loading state
        yield
        # Now load the data (this blocks, but UI has already shown loading spinner)
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
    def create_time_series_entity(self, form_data: dict):
        """Create a new TimeSeries entity."""
        import uuid
        import re
        
        name = form_data.get("name", "").strip()
        if not name:
            return rx.toast.error("Name is required")
        
        description = form_data.get("description", "").strip()
        unit = form_data.get("unit", "kW").strip()
        
        try:
            # Create API client
            api = TimeDBAPI(api_key=self.timedb_api_key if self.timedb_api_key else None)
            
            # Create series_key from name (sanitize for API - lowercase, replace spaces/special chars with underscores)
            series_key = re.sub(r'[^a-z0-9_]', '_', name.lower().replace(" ", "_"))
            # Remove multiple consecutive underscores
            series_key = re.sub(r'_+', '_', series_key).strip('_')
            
            # Validate series_key is not empty
            if not series_key:
                return rx.toast.error("Name must contain at least one alphanumeric character")
            
            # Create metadata
            metadata = {
                "name": name,
                "description": description,
                "unit": unit,
            }
            
            # Create the time series via API
            api_response = api.create_series(
                series_key=series_key,
                metadata=metadata,
            )
            
            # Get series_id from response
            series_id = api_response.get("series_id", str(uuid.uuid4()))
            
            # Create local entity representation
            new_entity: TimeSeries = {
                "id": series_id,
                "name": name,
                "description": description,
                "unit": unit,
                "site_name": "",  # Can be set later
                "timestamp": datetime.now().isoformat(),
                "value": 0.0,  # Can be set later
                "type": "actual",  # Default
                "tags": [],  # Can be set later
            }
            
            # Add to local cache - get collection_id from CollectionsState
            from app.states.collections import CollectionsState
            target_collection_id = CollectionsState.selected_collection_id or "default-timeseries"
            if target_collection_id not in self._time_series_entities:
                self._time_series_entities[target_collection_id] = []
            self._time_series_entities[target_collection_id].append(new_entity)
            
            # Close the modal
            CollectionsState.show_add_item_modal = False
            
            # Refresh the list from API to ensure we have the latest data
            self.refresh_timeseries_entities()
            return rx.toast.success(f"Time series '{name}' created successfully!")
            
        except httpx.HTTPStatusError as e:
            # Try to extract detailed error message from response
            error_detail = "Unknown error"
            try:
                if hasattr(e, 'response') and e.response:
                    error_json = e.response.json()
                    if isinstance(error_json, dict):
                        detail = error_json.get("detail", error_json.get("message", str(error_json)))
                        if isinstance(detail, list):
                            detail = "; ".join([str(d) for d in detail])
                        error_detail = str(detail)
                    else:
                        error_detail = str(error_json)
            except:
                error_detail = str(e)
            return rx.toast.error(f"Failed to create time series: {error_detail}")
        except httpx.RequestError as e:
            return rx.toast.error(f"Network error: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            return rx.toast.error(f"Failed to create time series: {error_msg}")
    
    @rx.event
    def set_entity_search_query(self, query: str):
        """Set the search query for filtering entities."""
        self.entity_search_query = query

