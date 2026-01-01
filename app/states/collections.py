import reflex as rx
from typing import TypedDict, Literal
from datetime import datetime
from app.states.entities import ObjectType, TimeSeries


# Table column configuration for collections
class TableColumn(TypedDict):
    name: str  # Display name of the column
    key: str  # Key to access the value in the entity
    type: Literal["text", "number", "date", "status", "tags"]  # How to render it
    visible: bool  # Whether to show this column


# Collection configuration
class CollectionConfig(TypedDict, total=False):
    id: str
    name: str
    object_type: ObjectType
    attributes: list[TableColumn]  # Configurable table columns
    created_at: str
    emoji: str  # Emoji icon for the collection
    view_type: Literal["table", "time_series_cards"]  # View layout type
    created_by: str  # User who created the collection
    is_favorite: bool  # Whether collection is favorited
    is_default: bool  # Whether this is the default collection shown on login


# Collection State Management
class CollectionsState(rx.State):
    """State management for collections (lists/views that group entities)."""
    
    # Collections storage - initialize with default collections for immediate availability
    _collections: list[CollectionConfig] = []
    
    # Track if collections have been loaded from DB
    _collections_loaded: bool = False
    
    def _initialize_default_collections(self):
        """Initialize default collections if not already initialized."""
        if len(self._collections) > 0:
            return  # Already initialized
        
        # Try to load from Supabase first
        if self._load_collections_from_db():
            return
        
        from datetime import datetime
        # Initialize with a default TimeSeries collection
        default_collection: CollectionConfig = {
            "id": "default-timeseries",
            "name": "Time Series",
            "object_type": "TimeSeries",
            "attributes": [
                {"name": "Name", "key": "name", "type": "text", "visible": True},
                {"name": "Description", "key": "description", "type": "text", "visible": True},
                {"name": "Unit", "key": "unit", "type": "text", "visible": True},
                {"name": "Site", "key": "site_name", "type": "text", "visible": True},
                {"name": "Timestamp", "key": "timestamp", "type": "date", "visible": True},
                {"name": "Value", "key": "value", "type": "number", "visible": True},
                {"name": "Type", "key": "type", "type": "status", "visible": True},
                {"name": "Tags", "key": "tags", "type": "tags", "visible": True},
            ],
            "created_at": datetime.now().isoformat(),
            "emoji": "📊",
            "view_type": "table",
            "created_by": "Sebastian Haglund",
            "is_favorite": False,
            "is_default": True,
        }
        
        # Create Esett data collection with Time Series Card Layout
        esett_collection: CollectionConfig = {
            "id": "esett-data",
            "name": "Esett data",
            "object_type": "TimeSeries",
            "attributes": [
                {"name": "Name", "key": "name", "type": "text", "visible": True},
                {"name": "Description", "key": "description", "type": "text", "visible": True},
                {"name": "Unit", "key": "unit", "type": "text", "visible": True},
            ],
            "created_at": datetime.now().isoformat(),
            "emoji": "📈",
            "view_type": "time_series_cards",
            "created_by": "Sebastian Haglund",
            "is_favorite": True,
            "is_default": False,
        }
        
        self._collections = [default_collection, esett_collection]
        
        # Save default collections to Supabase
        self._save_collections_to_db()
    
    def _load_collections_from_db(self) -> bool:
        """Load collections from Supabase. Returns True if collections were loaded."""
        if self._collections_loaded:
            return len(self._collections) > 0
        
        try:
            from app.services.supabase_service import SupabaseService
            from app.states.workspace import WorkspaceState
            
            # Get workspace ID (use default slug if workspace not loaded yet)
            workspace = SupabaseService.get_workspace("rebase-energy")
            if not workspace:
                self._collections_loaded = True
                return False
            
            workspace_id = workspace.get("id", "")
            if not workspace_id:
                self._collections_loaded = True
                return False
            
            # Load collections for this workspace
            db_collections = SupabaseService.get_collections(workspace_id)
            if db_collections:
                # Convert DB format to CollectionConfig
                self._collections = []
                for db_col in db_collections:
                    collection: CollectionConfig = {
                        "id": db_col.get("id", ""),
                        "name": db_col.get("name", ""),
                        "object_type": db_col.get("object_type", "TimeSeries"),
                        "attributes": db_col.get("attributes", []),
                        "created_at": db_col.get("created_at", ""),
                        "emoji": db_col.get("emoji", "📋"),
                        "view_type": db_col.get("view_type", "table"),
                        "created_by": db_col.get("created_by", ""),
                        "is_favorite": db_col.get("is_favorite", False),
                        "is_default": db_col.get("is_default", False),
                    }
                    self._collections.append(collection)
                self._collections_loaded = True
                return True
            
            self._collections_loaded = True
            return False
        except Exception as e:
            print(f"Failed to load collections from database: {e}")
            self._collections_loaded = True
            return False
    
    def _save_collections_to_db(self):
        """Save all collections to Supabase."""
        try:
            from app.services.supabase_service import SupabaseService
            
            # Get workspace
            workspace = SupabaseService.get_workspace("rebase-energy")
            if not workspace:
                return
            
            workspace_id = workspace.get("id", "")
            if not workspace_id:
                return
            
            # Save each collection
            for collection in self._collections:
                data = {
                    "workspace_id": workspace_id,
                    "name": collection.get("name", ""),
                    "object_type": collection.get("object_type", "TimeSeries"),
                    "attributes": collection.get("attributes", []),
                    "emoji": collection.get("emoji", "📋"),
                    "view_type": collection.get("view_type", "table"),
                    "created_by": collection.get("created_by", ""),
                    "is_favorite": collection.get("is_favorite", False),
                    "is_default": collection.get("is_default", False),
                }
                SupabaseService.upsert_collection(collection.get("id", ""), data)
        except Exception as e:
            print(f"Failed to save collections to database: {e}")
    
    def _save_collection_to_db(self, collection_id: str):
        """Save a single collection to Supabase."""
        try:
            from app.services.supabase_service import SupabaseService
            
            # Find the collection
            collection = None
            for col in self._collections:
                if col.get("id") == collection_id:
                    collection = col
                    break
            
            if not collection:
                return
            
            # Get workspace
            workspace = SupabaseService.get_workspace("rebase-energy")
            if not workspace:
                return
            
            workspace_id = workspace.get("id", "")
            if not workspace_id:
                return
            
            data = {
                "workspace_id": workspace_id,
                "name": collection.get("name", ""),
                "object_type": collection.get("object_type", "TimeSeries"),
                "attributes": collection.get("attributes", []),
                "emoji": collection.get("emoji", "📋"),
                "view_type": collection.get("view_type", "table"),
                "created_by": collection.get("created_by", ""),
                "is_favorite": collection.get("is_favorite", False),
                "is_default": collection.get("is_default", False),
            }
            SupabaseService.upsert_collection(collection_id, data)
        except Exception as e:
            print(f"Failed to save collection to database: {e}")
    
    # Selected collection
    selected_collection_id: str = ""
    
    # Collection UI state
    show_create_collection_modal: bool = False
    show_add_item_modal: bool = False
    show_emoji_picker: bool = False
    emoji_search_query: str = ""
    emoji_selected_category: str = "Smileys & Emotion"
    
    # Collection view controls
    collection_search_query: str = ""
    show_sort_modal: bool = False
    show_filter_modal: bool = False
    
    # Settings page search
    settings_collections_search_query: str = ""
    
    # Collection view settings
    # Column widths (stored as dict: column_key -> width in pixels)
    column_widths: dict[str, int] = {}
    
    # Chart legend visibility state for timeseries cards (card_id -> {series_name: visible})
    timeseries_chart_legend_visibility: dict[str, dict[str, bool]] = {}
    
    # Column layout for timeseries card grid (1 or 2 columns)
    timeseries_card_columns: int = 2
    
    # Default column widths
    _default_column_widths = {
        "name": 200,
        "description": 250,
        "unit": 100,
        "site_name": 180,
        "timestamp": 180,
        "value": 120,
        "type": 120,
        "tags": 150,
    }
    
    @rx.var
    def collections(self) -> list[CollectionConfig]:
        """Get all collections."""
        # Ensure collections are initialized
        self._initialize_default_collections()
        return self._collections
    
    @rx.var
    def active_collection_id(self) -> str:
        """Get the currently active collection ID."""
        return self.selected_collection_id
    
    @rx.var
    def active_collection(self) -> CollectionConfig | None:
        """Get the currently active collection."""
        self._initialize_default_collections()
        collection_id = self.active_collection_id
        if not collection_id:
            return None
        for collection in self._collections:
            if collection["id"] == collection_id:
                return collection
        return None
    
    @rx.var
    def selected_collection(self) -> CollectionConfig | None:
        """Alias for active_collection for backward compatibility."""
        return self.active_collection
    
    @rx.var
    def active_collection_view_type(self) -> str:
        """Get the view type of the active collection, defaulting to 'table'."""
        collection = self.active_collection
        if not collection:
            return "table"
        return collection.get("view_type", "table")
    
    @rx.var
    def selected_collection_view_type(self) -> str:
        """Alias for active_collection_view_type for backward compatibility."""
        return self.active_collection_view_type
    
    @rx.var
    def selected_collection_entities(self) -> list[TimeSeries]:
        """Get entities for the selected collection with search filter applied."""
        collection_id = self.active_collection_id
        if not collection_id:
            return []
        
        # Access entities dictionary directly from EntitiesState
        from app.states.entities import EntitiesState
        items = EntitiesState._time_series_entities.get(collection_id, [])
        
        # Apply search filter
        if self.collection_search_query:
            query = self.collection_search_query.lower()
            items = [
                item for item in items
                if query in item.get("name", "").lower()
                or query in item.get("description", "").lower()
                or query in item.get("unit", "").lower()
                or query in item.get("site_name", "").lower()
                or query in str(item.get("value", "")).lower()
                or query in item.get("type", "").lower()
            ]
        return items
    
    
    @rx.var
    def esett_card_data(self) -> list[dict]:
        """Get time series card data for Esett data collection."""
        # For now, return sample data matching the screenshot
        # Later this will be populated from TimeDB API
        import random
        from datetime import datetime, timedelta
        
        cards = []
        locations = [
            {"name": "Blackfjället", "capacity": 90.2},
            {"name": "Ranasjo", "capacity": 150.0},
            {"name": "Storberget", "capacity": 75.5},
            {"name": "Vindpark Nord", "capacity": 200.0},
        ]
        
        for loc in locations:
            data_points = []
            now = datetime.now()
            start_time = now - timedelta(days=1)
            end_time = now + timedelta(days=4)
            current_time = start_time
            
            while current_time <= end_time:
                hour = current_time.hour
                base = loc["capacity"] * 0.6
                variation = loc["capacity"] * 0.3 * (0.5 + (hour % 12) / 12)
                actual = base + variation + (loc["capacity"] * 0.1 * random.uniform(-1, 1))
                forecast = actual * (1 + random.uniform(-0.1, 0.1))
                
                data_points.append({
                    "time": current_time.strftime("%a %d/%m %H:%M"),
                    "capacity": loc["capacity"],
                    "actual": max(0, min(loc["capacity"], actual)),
                    "forecast": max(0, min(loc["capacity"], forecast)),
                    "iceaware": None,
                    "iceblind": None,
                    "iceloss": None,
                })
                current_time += timedelta(hours=1)
            
            cards.append({
                "id": loc["name"].lower().replace(" ", "-"),
                "name": loc["name"],
                "capacity_mw": loc["capacity"],
                "data": data_points,
                "view_tabs": ["Default view", "Iceloss", "Iceloss pct", "Iceloss weather"],
            })
        
        return cards
    
    @rx.var
    def get_column_width(self) -> dict[str, int]:
        """Get column widths, using defaults if not set."""
        if not self.column_widths:
            return self._default_column_widths.copy()
        # Merge with defaults to ensure all columns have widths
        result = self._default_column_widths.copy()
        result.update(self.column_widths)
        return result
    
    @rx.var
    def column_width_name(self) -> int:
        """Get width for 'name' column."""
        widths = self.get_column_width
        return widths.get("name", 200)
    
    @rx.var
    def column_width_site_name(self) -> int:
        """Get width for 'site_name' column."""
        widths = self.get_column_width
        return widths.get("site_name", 180)
    
    @rx.var
    def column_width_value(self) -> int:
        """Get width for 'value' column."""
        widths = self.get_column_width
        return widths.get("value", 120)
    
    @rx.var
    def column_width_type(self) -> int:
        """Get width for 'type' column."""
        widths = self.get_column_width
        return widths.get("type", 120)
    
    @rx.var
    def column_width_description(self) -> int:
        """Get width for 'description' column."""
        widths = self.get_column_width
        return widths.get("description", 250)
    
    @rx.var
    def column_width_unit(self) -> int:
        """Get width for 'unit' column."""
        widths = self.get_column_width
        return widths.get("unit", 100)
    
    @rx.event
    def on_load(self):
        """Initialize default collections on app load."""
        self._initialize_default_collections()
        
        # Set default collection only if no collection is selected
        if not self.selected_collection_id:
            self.selected_collection_id = "default-timeseries"
    
    @rx.event
    def on_load_collection_page(self):
        """Initialize collections and set active collection from route."""
        self._initialize_default_collections()
        
        # Get collection_id from URL params
        try:
            collection_id = self.router.url.params.get("collection_id", "")  # type: ignore[attr-defined]
        except Exception:
            collection_id = ""
        
        # Always set the collection from URL (overriding any previous selection)
        if collection_id:
            self.selected_collection_id = collection_id
        else:
            # Fallback: try to extract from path
            try:
                path = self.router.url.path  # type: ignore[attr-defined]
                if "/collections/" in path:
                    parts = path.split("/collections/")
                    if len(parts) > 1:
                        self.selected_collection_id = parts[1].split("/")[0]
            except Exception:
                pass
    
    @rx.event
    def create_collection(self, form_data: dict):
        """Create a new collection."""
        import uuid
        
        collection_id = str(uuid.uuid4())
        object_type = form_data.get("object_type", "TimeSeries")
        
        # Default attributes based on object type
        default_attributes = self._get_default_attributes(object_type)
        
        new_collection: CollectionConfig = {
            "id": collection_id,
            "name": form_data["collection_name"],
            "object_type": object_type,
            "attributes": default_attributes,
            "created_at": datetime.now().isoformat(),
            "emoji": form_data.get("emoji", "📋"),
            "view_type": "table",
            "created_by": "Sebastian Haglund",  # TODO: Get from actual user session
            "is_favorite": False,
            "is_default": False,
        }
        
        self._collections.append(new_collection)
        self.selected_collection_id = collection_id
        
        # Save to database
        self._save_collection_to_db(collection_id)
        
        # Initialize empty entity storage for this collection
        # This will be handled by EntitiesState when entities are first accessed
        self.show_create_collection_modal = False
        return rx.toast.success(f"Collection '{new_collection['name']}' created successfully!")
    
    def _get_default_attributes(self, object_type: ObjectType) -> list[TableColumn]:
        """Get default attributes for an object type."""
        if object_type == "TimeSeries":
            return [
                {"name": "Name", "key": "name", "type": "text", "visible": True},
                {"name": "Site", "key": "site_name", "type": "text", "visible": True},
                {"name": "Timestamp", "key": "timestamp", "type": "date", "visible": True},
                {"name": "Value", "key": "value", "type": "number", "visible": True},
                {"name": "Unit", "key": "unit", "type": "text", "visible": True},
                {"name": "Type", "key": "type", "type": "status", "visible": True},
            ]
        elif object_type == "Site":
            return [
                {"name": "Name", "key": "name", "type": "text", "visible": True},
                {"name": "Type", "key": "type", "type": "status", "visible": True},
                {"name": "Capacity", "key": "capacity", "type": "text", "visible": True},
                {"name": "Status", "key": "status", "type": "status", "visible": True},
            ]
        return []
    
    @rx.event
    def select_collection(self, collection_id: str):
        """Select a collection and navigate to its page."""
        # Route is the source of truth for what renders. Just navigate.
        self.selected_collection_id = collection_id
        # Use workspace slug (default value - could be made dynamic in future)
        workspace_slug = "rebase-energy"
        return rx.redirect(f"/{workspace_slug}/collections/{collection_id}")
    
    @rx.event
    def load_collection_page(self, collection_id: str):
        """Load a collection page - sets the collection without redirecting."""
        # Keep state in sync when called from UI. Rendering is still route-driven.
        self.selected_collection_id = collection_id
        yield
    
    @rx.event
    def toggle_create_collection_modal(self):
        """Toggle the create collection modal."""
        self.show_create_collection_modal = not self.show_create_collection_modal
    
    @rx.event
    def toggle_add_item_modal(self):
        """Toggle the add item modal."""
        self.show_add_item_modal = not self.show_add_item_modal
    
    @rx.event
    def close_add_item_modal(self):
        """Close the add item modal."""
        self.show_add_item_modal = False
    
    @rx.event
    def toggle_emoji_picker(self):
        """Toggle the emoji picker."""
        self.show_emoji_picker = not self.show_emoji_picker
        if not self.show_emoji_picker:
            self.emoji_search_query = ""
    
    @rx.event
    def set_emoji_search_query(self, query: str):
        """Set the emoji search query."""
        self.emoji_search_query = query
    
    @rx.event
    def set_emoji_category(self, category: str):
        """Set the emoji category."""
        self.emoji_selected_category = category
    
    @rx.var
    def current_emoji_list(self) -> list[str]:
        """Get emojis for the currently selected category."""
        # Define emoji categories here to avoid circular imports
        emoji_categories = {
            "Smileys & Emotion": ["😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂", "🙂", "🙃", "😉", "😊", "😇", "🥰", "😍", "🤩", "😘", "😗", "😚", "😙", "😋", "😛", "😜", "🤪", "😝", "🤑", "🤗", "🤭", "🤫", "🤔", "🤐", "🤨", "😐", "😑", "😶", "😏", "😒", "🙄", "😬", "🤥", "😌", "😔", "😪", "🤤", "😴", "😷", "🤒", "🤕", "🤢", "🤮", "🤧", "🥵", "🥶", "😵", "🤯", "🤠", "🥳", "😎", "🤓", "🧐"],
            "Objects": ["⌚", "📱", "📲", "💻", "⌨️", "🖥️", "🖨️", "🖱️", "🖲️", "🕹️", "💾", "💿", "📀", "📷", "📸", "📹", "🎥", "📞", "☎️", "📺", "📻", "🎙️", "⏰", "🕰️", "⌛", "⏳", "📡", "🔋", "🔌", "💡", "🔦", "🕯️", "🧯", "💸", "💵", "💴", "💶", "💷", "💰", "💳", "💎", "⚖️", "🧰", "🪛", "🔧", "🔨", "🛠️", "⛏️", "🔩", "⚙️", "🧱", "⛓️", "🧲", "💣", "🧨", "🪓", "🔪", "🗡️", "⚔️", "🛡️", "🔮", "📿", "🧿", "💈", "⚗️", "🔭", "🔬", "🕳️", "🩹", "🩺", "💊", "💉", "🩸", "🧬", "🦠", "🧫", "🧪", "🌡️", "🧹", "🪠", "🧺", "🧻", "🚽", "🚰", "🚿", "🛁", "🛀", "🧼", "🪒", "🧽", "🪣", "🧴", "🛎️", "🔑", "🗝️", "🚪", "🪑", "🛋️", "🛏️", "🛌", "🧸", "🖼️", "🪞", "🪟", "🛍️", "🛒", "🎁", "🎈", "🎏", "🎀", "🪄", "🪅", "🎊", "🎉", "🎎", "🏮", "🎐", "🧧", "✉️", "📩", "📨", "📧", "💌", "📥", "📤", "📦", "🪧", "📪", "📫", "📬", "📭", "📮", "📯", "📜", "📃", "📄", "📑", "🧾", "📊", "📈", "📉", "🗒️", "🗓️", "📆", "📅", "🗑️", "📇", "🗃️", "🗳️", "🗄️", "📋", "📁", "📂", "🗂️", "📓", "📔", "📒", "📕", "📗", "📘", "📙", "📚", "📖", "🔖", "🧷", "🔗", "📎", "🖇️", "📐", "📏", "🧮", "📌", "📍", "✂️", "🖊️", "🖋️", "✒️", "🖌️", "🖍️", "📝", "✏️", "🔍", "🔎", "🔏", "🔐", "🔒", "🔓"],
            "Symbols": ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔", "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "☮️", "✝️", "☪️", "🕉️", "☸️", "🕎", "🔯", "🪯", "🛐", "⛎", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓", "🆔", "⚛️", "🉑", "☢️", "☣️", "📴", "📳", "🈶", "🈚", "🈸", "🈺", "🈷️", "✴️", "🆚", "💮", "🉐", "㊙️", "㊗️", "🈴", "🈵", "🈹", "🈲", "🅰️", "🅱️", "🆎", "🆑", "🅾️", "🆘", "❌", "⭕", "🛑", "⛔", "📛", "🚫", "💯", "💢", "♨️", "🚷", "🚯", "🚳", "🚱", "🔞", "📵", "🚭", "❗", "❓", "❕", "❔", "‼️", "⁉️", "🔅", "🔆", "〽️", "⚠️", "🚸", "🔱", "⚜️", "🔰", "♻️", "✅", "🈯", "💹", "❇️", "✳️", "❎", "🌐", "💠", "Ⓜ️", "🌀", "💤", "🏧", "🚾", "♿", "🅿️", "🈳", "🈂️", "🛂", "🛃", "🛄", "🛅", "🚹", "🚺", "🚼", "🚻", "🚮", "🎦", "📶", "🈁", "🔣", "ℹ️", "🔤", "🔡", "🔠", "🔢", "🔟", "#️⃣", "*️⃣", "0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "🔺", "🔻", "💱", "💲"],
        }
        return emoji_categories.get(self.emoji_selected_category, emoji_categories["Smileys & Emotion"])
    
    @rx.event
    def set_collection_emoji(self, emoji: str):
        """Set emoji for the selected collection."""
        if not self.selected_collection_id:
            return
        # Update the emoji in the collection
        for i, collection in enumerate(self._collections):
            if collection["id"] == self.selected_collection_id:
                updated_collection = collection.copy()
                updated_collection["emoji"] = emoji
                self._collections[i] = updated_collection
                break
        
        # Save to database
        self._save_collection_to_db(self.selected_collection_id)
        
        self.show_emoji_picker = False
        return rx.toast.success(f"Emoji updated!")
    
    @rx.event
    def toggle_timeseries_chart_series(self, card_id: str, series_name: str):
        """Toggle visibility of a chart series in timeseries cards."""
        if card_id not in self.timeseries_chart_legend_visibility:
            self.timeseries_chart_legend_visibility[card_id] = {
                "Capacity": True,
                "Actual": True,
                "Forecast": True,
            }
        current_value = self.timeseries_chart_legend_visibility[card_id].get(series_name, True)
        self.timeseries_chart_legend_visibility[card_id][series_name] = not current_value
    
    def get_timeseries_chart_series_visible(self, card_id: str, series_name: str) -> bool:
        """Get visibility state of a chart series in timeseries cards."""
        if card_id not in self.timeseries_chart_legend_visibility:
            return True
        return self.timeseries_chart_legend_visibility[card_id].get(series_name, True)
    
    @rx.event
    def toggle_timeseries_card_columns(self):
        """Toggle between 1 and 2 columns for timeseries card grid."""
        self.timeseries_card_columns = 1 if self.timeseries_card_columns == 2 else 2
    
    @rx.event
    def set_collection_search_query(self, query: str):
        """Set the search query for filtering collection entities."""
        self.collection_search_query = query
    
    @rx.event
    def set_settings_collections_search_query(self, query: str):
        """Set the search query for filtering collections in settings page."""
        self.settings_collections_search_query = query
    
    @rx.var
    def filtered_collections_for_settings(self) -> list[CollectionConfig]:
        """Get collections filtered by search query for settings page."""
        # Ensure collections are initialized first
        self._initialize_default_collections()
        collections = self._collections
        if not self.settings_collections_search_query:
            return collections
        query = self.settings_collections_search_query.lower()
        return [
            collection for collection in collections
            if query in collection.get("name", "").lower()
            or query in collection.get("created_by", "").lower()
        ]
    
    
    @rx.event
    def toggle_sort_modal(self):
        """Toggle the sort modal."""
        self.show_sort_modal = not self.show_sort_modal
    
    @rx.event
    def toggle_filter_modal(self):
        """Toggle the filter modal."""
        self.show_filter_modal = not self.show_filter_modal
    
    @rx.event
    def set_column_width(self, value: str):
        """Update column width from hidden input value (format: 'column_key:width')."""
        if value and ":" in value:
            parts = value.split(":", 1)
            if len(parts) == 2:
                column_key = parts[0]
                try:
                    width = int(parts[1])
                    if not self.column_widths:
                        self.column_widths = {}
                    self.column_widths[column_key] = max(50, width)  # Minimum width of 50px
                except ValueError:
                    pass
    
    @rx.event
    def toggle_collection_favorite(self, collection_id: str):
        """Toggle favorite status for a collection."""
        for i, collection in enumerate(self._collections):
            if collection["id"] == collection_id:
                updated_collection = collection.copy()
                updated_collection["is_favorite"] = not collection.get("is_favorite", False)
                self._collections[i] = updated_collection
                break
        
        # Save to database
        self._save_collection_to_db(collection_id)
    
    @rx.event
    def set_default_collection(self, collection_id: str):
        """Set a collection as the default (only one can be default at a time)."""
        # First, unset all other collections as default
        for i, collection in enumerate(self._collections):
            if collection.get("is_default", False):
                updated_collection = collection.copy()
                updated_collection["is_default"] = False
                self._collections[i] = updated_collection
                # Save to database
                self._save_collection_to_db(collection.get("id", ""))
        
        # Then set the selected collection as default
        for i, collection in enumerate(self._collections):
            if collection["id"] == collection_id:
                updated_collection = collection.copy()
                updated_collection["is_default"] = True
                self._collections[i] = updated_collection
                break
        
        # Save the new default collection to database
        self._save_collection_to_db(collection_id)

