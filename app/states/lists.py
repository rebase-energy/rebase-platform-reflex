import reflex as rx
import httpx
from typing import TypedDict, Literal, Any
from datetime import datetime
from app.services.timedb_api import TimeDBAPI


# Object Types that can be stored in lists
ObjectType = Literal["TimeSeries", "Site", "Asset"]


# Attribute/Column configuration for lists
class ListAttribute(TypedDict):
    name: str  # Display name of the attribute
    key: str  # Key to access the value in the object
    type: Literal["text", "number", "date", "status", "tags"]  # How to render it
    visible: bool  # Whether to show this column


# List configuration
class ListConfig(TypedDict):
    id: str
    name: str
    object_type: ObjectType
    attributes: list[ListAttribute]  # Configurable columns
    created_at: str
    emoji: str  # Emoji icon for the list
    view_type: Literal["table", "time_series_cards"]  # View layout type


# TimeSeries object (example of what can be stored in a list)
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


# List State Management
class ListsState(rx.State):
    _lists: list[ListConfig] = []
    _time_series_items: dict[str, list[TimeSeries]] = {}  # list_id -> items
    selected_list_id: str = ""
    show_create_list_modal: bool = False
    show_add_item_modal: bool = False
    show_emoji_picker: bool = False
    emoji_search_query: str = ""
    emoji_selected_category: str = "Smileys & Emotion"
    
    # Dropdown states for sidebar
    favorites_expanded: bool = True
    objects_expanded: bool = True
    lists_expanded: bool = True
    
    # Sidebar collapse state
    sidebar_collapsed: bool = False
    
    # Sidebar width in pixels (default 256px = w-64)
    sidebar_width: int = 256
    
    # Selected object type
    selected_object_type: str = ""
    
    # Selected menu item (Projects, Workflows, etc.)
    selected_menu_item: str = ""
    
    # Loading state
    is_loading: bool = False
    
    # List view controls
    list_search_query: str = ""
    show_sort_modal: bool = False
    show_filter_modal: bool = False
    
    # API configuration
    timedb_api_key: str = ""  # Optional API key for authentication
    
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
    def lists(self) -> list[ListConfig]:
        return self._lists

    @rx.var
    def selected_list(self) -> ListConfig | None:
        if not self.selected_list_id:
            return None
        for lst in self._lists:
            if lst["id"] == self.selected_list_id:
                return lst
        return None
    
    @rx.var
    def selected_list_view_type(self) -> str:
        """Get the view type of the selected list, defaulting to 'table'."""
        if not self.selected_list_id:
            return "table"
        for lst in self._lists:
            if lst["id"] == self.selected_list_id:
                # Check if view_type exists in the dict
                if "view_type" in lst:
                    return lst["view_type"]
                return "table"
        return "table"
    
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
    def selected_list_items(self) -> list[TimeSeries]:
        if not self.selected_list_id:
            return []
        items = self._time_series_items.get(self.selected_list_id, [])
        # Apply search filter
        if self.list_search_query:
            query = self.list_search_query.lower()
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
    def get_sidebar_width_px(self) -> str:
        """Get sidebar width as a string with 'px' suffix."""
        if self.sidebar_collapsed:
            return "64px"
        return f"{self.sidebar_width}px"
    
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
        # Initialize with a default TimeSeries list
        default_list: ListConfig = {
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
        esett_list: ListConfig = {
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
        
        self._lists = [default_list, esett_list]
        self.selected_list_id = "default-timeseries"
        self._time_series_items["esett-data"] = []  # Initialize empty for now
        
        # Load time series from API
        try:
            api = TimeDBAPI(api_key=self.timedb_api_key if self.timedb_api_key else None)
            timeseries_map = api.list_timeseries()
            
            # Convert API response to TimeSeries items
            # API returns dict: {series_id: series_key} or {series_id: {series_key: ..., metadata: ...}}
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
            
            self._time_series_items["default-timeseries"] = items
        except Exception as e:
            # If API fails, use empty list
            print(f"Failed to load time series from API: {e}")
            self._time_series_items["default-timeseries"] = []

    @rx.event
    def create_list(self, form_data: dict):
        import uuid
        
        list_id = str(uuid.uuid4())
        object_type = form_data.get("object_type", "TimeSeries")
        
        # Default attributes based on object type
        default_attributes = self._get_default_attributes(object_type)
        
        new_list: ListConfig = {
            "id": list_id,
            "name": form_data["list_name"],
            "object_type": object_type,
            "attributes": default_attributes,
            "created_at": datetime.now().isoformat(),
            "emoji": form_data.get("emoji", "📋"),
        }
        
        self._lists.append(new_list)
        self._time_series_items[list_id] = []
        self.selected_list_id = list_id
        self.show_create_list_modal = False
        return rx.toast.success(f"List '{new_list['name']}' created successfully!")

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
    def select_list(self, list_id: str):
        # Set selection immediately for instant feedback
        self.selected_list_id = list_id
        self.selected_object_type = ""  # Clear object selection when selecting list
        self.selected_menu_item = ""  # Clear menu item selection when selecting list
        self.is_loading = False  # Clear loading state

    @rx.event
    def toggle_create_list_modal(self):
        self.show_create_list_modal = not self.show_create_list_modal

    @rx.event
    def toggle_add_item_modal(self):
        self.show_add_item_modal = not self.show_add_item_modal
    
    @rx.event
    def toggle_emoji_picker(self):
        self.show_emoji_picker = not self.show_emoji_picker
        if not self.show_emoji_picker:
            self.emoji_search_query = ""
    
    @rx.event
    def set_emoji_search_query(self, query: str):
        self.emoji_search_query = query
    
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
    def set_emoji_category(self, category: str):
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
    def set_list_emoji(self, emoji: str):
        """Set emoji for the selected list."""
        if not self.selected_list_id:
            return
        # Update the emoji in the list
        for i, lst in enumerate(self._lists):
            if lst["id"] == self.selected_list_id:
                updated_list = lst.copy()
                updated_list["emoji"] = emoji
                self._lists[i] = updated_list
                break
        self.show_emoji_picker = False
        return rx.toast.success(f"Emoji updated!")

    @rx.event
    def add_time_series_item(self, form_data: dict):
        import uuid
        import re
        
        # Allow creation if either a list is selected OR TimeSeries object type is selected
        if not self.selected_list_id and self.selected_object_type != "TimeSeries":
            return rx.toast.error("Please select a list or TimeSeries object type first")
        
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
            # Note: series_key is used for both 'series_key' and 'name' in the API
            api_response = api.create_series(
                series_key=series_key,
                metadata=metadata,
            )
            
            # Get series_id from response
            series_id = api_response.get("series_id", str(uuid.uuid4()))
            
            # Create local item representation
            new_item: TimeSeries = {
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
            
            # Add to local cache
            if self.selected_list_id:
                if self.selected_list_id not in self._time_series_items:
                    self._time_series_items[self.selected_list_id] = []
                self._time_series_items[self.selected_list_id].append(new_item)
            elif self.selected_object_type == "TimeSeries":
                # When viewing by object type, add to default list cache
                # The all_time_series_items var will pick it up
                default_list_id = "default-timeseries"
                if default_list_id not in self._time_series_items:
                    self._time_series_items[default_list_id] = []
                self._time_series_items[default_list_id].append(new_item)
            
            self.show_add_item_modal = False
            # Refresh the list from API to ensure we have the latest data
            self.refresh_timeseries_list()
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
    def toggle_favorites(self):
        self.favorites_expanded = not self.favorites_expanded

    @rx.event
    def toggle_objects(self):
        self.objects_expanded = not self.objects_expanded

    @rx.event
    def toggle_lists(self):
        self.lists_expanded = not self.lists_expanded

    @rx.event
    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed
    
    @rx.event
    def set_sidebar_width(self, width: str):
        """Update sidebar width from resize handle (format: 'width')."""
        try:
            width_int = int(width)
            # Clamp width between 200px and 600px
            self.sidebar_width = max(200, min(600, width_int))
        except ValueError:
            pass

    @rx.event
    def select_menu_item(self, menu_item: str):
        """Select a menu item (Projects, Workflows, etc.)."""
        # Set selection immediately for instant feedback
        self.selected_menu_item = menu_item
        self.selected_object_type = ""  # Clear object selection
        self.selected_list_id = ""  # Clear list selection
        self.is_loading = False  # Clear loading state
    
    @rx.event
    def select_object_type(self, object_type: str):
        # Set selection immediately for instant feedback
        self.selected_object_type = object_type
        self.selected_list_id = ""  # Clear list selection when selecting object
        self.selected_menu_item = ""  # Clear menu item selection
        
        # Load items from API when selecting TimeSeries object type
        if object_type == "TimeSeries":
            self.is_loading = True
            # Trigger async loading - this will happen after UI updates
            return self.load_timeseries_async()
    
    @rx.event
    def load_timeseries_async(self):
        """Load time series data asynchronously."""
        # Yield to allow UI to update with loading state
        yield
        # Now load the data (this blocks, but UI has already shown loading spinner)
        self._load_timeseries_data()

    @rx.var
    def all_time_series_items(self) -> list[TimeSeries]:
        """Get all TimeSeries items from all lists."""
        all_items = []
        for list_id, items in self._time_series_items.items():
            all_items.extend(items)
        # Apply search filter
        if self.list_search_query:
            query = self.list_search_query.lower()
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
    
    @rx.event
    def set_list_search_query(self, query: str):
        self.list_search_query = query
    
    @rx.event
    def toggle_sort_modal(self):
        self.show_sort_modal = not self.show_sort_modal
    
    @rx.event
    def toggle_filter_modal(self):
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
            
            # Store in appropriate location based on current view
            if self.selected_list_id:
                self._time_series_items[self.selected_list_id] = items
            elif self.selected_object_type == "TimeSeries":
                # When viewing by object type, store in default list cache
                default_list_id = "default-timeseries"
                self._time_series_items[default_list_id] = items
            else:
                # Fallback to default list
                default_list_id = "default-timeseries"
                self._time_series_items[default_list_id] = items
            
            self.is_loading = False
        except Exception as e:
            self.is_loading = False
            print(f"Failed to load time series: {e}")
    
    @rx.event
    def refresh_timeseries_list(self):
        """Refresh the time series list from the API."""
        self.is_loading = True
        yield
        self._load_timeseries_data()
        item_count = len(self._time_series_items.get("default-timeseries", []))
        yield rx.toast.success(f"Refreshed {item_count} time series")

