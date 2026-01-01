import reflex as rx
from typing import TypedDict, Literal
from datetime import datetime
from app.states.entities import ObjectType, TimeSeries


# Attribute/Column configuration for collections
class ListAttribute(TypedDict):
    name: str  # Display name of the attribute
    key: str  # Key to access the value in the entity
    type: Literal["text", "number", "date", "status", "tags"]  # How to render it
    visible: bool  # Whether to show this column


# Collection configuration
class ListConfig(TypedDict):
    id: str
    name: str
    object_type: ObjectType
    attributes: list[ListAttribute]  # Configurable columns
    created_at: str
    emoji: str  # Emoji icon for the collection
    view_type: Literal["table", "time_series_cards"]  # View layout type


# Collection State Management
class CollectionsState(rx.State):
    """State management for collections (lists/views that group entities)."""
    
    # Collections storage
    _collections: list[ListConfig] = []
    
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
    def collections(self) -> list[ListConfig]:
        """Get all collections."""
        return self._collections
    
    @rx.var
    def selected_collection(self) -> ListConfig | None:
        """Get the currently selected collection."""
        if not self.selected_collection_id:
            return None
        for collection in self._collections:
            if collection["id"] == self.selected_collection_id:
                return collection
        return None
    
    @rx.var
    def selected_collection_view_type(self) -> str:
        """Get the view type of the selected collection, defaulting to 'table'."""
        if not self.selected_collection_id:
            return "table"
        for collection in self._collections:
            if collection["id"] == self.selected_collection_id:
                # Check if view_type exists in the dict
                if "view_type" in collection:
                    return collection["view_type"]
                return "table"
        return "table"
    
    @rx.var
    def selected_collection_entities(self) -> list[TimeSeries]:
        """Get entities for the selected collection, with search filter applied."""
        if not self.selected_collection_id:
            return []
        
        # Get entities from EntitiesState - access the underlying dictionary directly
        from app.states.entities import EntitiesState
        # Access the private attribute directly to avoid Var chaining issues
        entities_dict = EntitiesState._time_series_entities
        # Use .get() which returns [] if key doesn't exist (lazy initialization)
        items = entities_dict.get(self.selected_collection_id, [])
        
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
            {"name": "Salsjo", "capacity": 86.8},
            {"name": "Åskälen", "capacity": 288.0},
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
        # Initialize with a default TimeSeries collection
        default_collection: ListConfig = {
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
        }
        
        # Create Esett data collection with Time Series Card Layout
        esett_collection: ListConfig = {
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
        }
        
        self._collections = [default_collection, esett_collection]
        self.selected_collection_id = "default-timeseries"
        
        # Entity storage will be initialized lazily when entities are first accessed
        # This is handled in EntitiesState when entities are loaded
    
    @rx.event
    def create_collection(self, form_data: dict):
        """Create a new collection."""
        import uuid
        
        collection_id = str(uuid.uuid4())
        object_type = form_data.get("object_type", "TimeSeries")
        
        # Default attributes based on object type
        default_attributes = self._get_default_attributes(object_type)
        
        new_collection: ListConfig = {
            "id": collection_id,
            "name": form_data["collection_name"],
            "object_type": object_type,
            "attributes": default_attributes,
            "created_at": datetime.now().isoformat(),
            "emoji": form_data.get("emoji", "📋"),
            "view_type": "table",
        }
        
        self._collections.append(new_collection)
        self.selected_collection_id = collection_id
        
        # Initialize empty entity storage for this collection
        # This will be handled by EntitiesState when entities are first accessed
        self.show_create_collection_modal = False
        return rx.toast.success(f"Collection '{new_collection['name']}' created successfully!")
    
    def _get_default_attributes(self, object_type: ObjectType) -> list[ListAttribute]:
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
        """Select a collection and optionally load its entities."""
        # Set selection immediately for instant feedback
        self.selected_collection_id = collection_id
        
        # Clear other selections
        from app.states.entities import EntitiesState
        from app.states.workspace import WorkspaceState
        EntitiesState.selected_object_type = ""
        WorkspaceState.selected_menu_item = ""
        
        # Load entities lazily if this collection needs it and doesn't have it yet
        # This will be handled by the component that uses select_collection
        return None
    
    @rx.event
    def toggle_create_collection_modal(self):
        """Toggle the create collection modal."""
        self.show_create_collection_modal = not self.show_create_collection_modal
    
    @rx.event
    def toggle_add_item_modal(self):
        """Toggle the add item modal."""
        self.show_add_item_modal = not self.show_add_item_modal
    
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

