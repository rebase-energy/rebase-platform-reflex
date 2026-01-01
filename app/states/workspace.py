import reflex as rx


# Workspace State Management
class WorkspaceState(rx.State):
    """State management for workspace UI, navigation, and settings."""
    
    # Sidebar state
    sidebar_collapsed: bool = False
    sidebar_width: int = 256  # Default 256px = w-64
    
    # Sidebar section expansion states
    favorites_expanded: bool = True
    objects_expanded: bool = True
    collections_expanded: bool = True
    
    # Navigation state
    selected_menu_item: str = ""  # Projects, Workflows, etc.
    
    # Workspace dropdown state
    workspace_dropdown_open: bool = False
    
    # Settings page state
    selected_settings_section: str = "General"
    
    @rx.var
    def current_settings_section_from_route(self) -> str:
        """Get current settings section from route using JavaScript."""
        # This will be set by JavaScript reading the URL
        # Default to General if not set
        return self.selected_settings_section
    
    # Appearance settings state
    theme: str = "Dark"  # "Light", "Dark", or "System"
    accent_color: str = "#10b981"  # Default green
    custom_accent_color: str = ""
    menu_item_visibility: dict[str, bool] = {
        "Projects": True,
        "Workflows": True,
        "Dashboards": True,
        "Notebooks": True,
        "Models": True,
        "Datasets": True,
        "Notifications": True,
        "Reports": True,
    }
    
    @rx.var
    def get_sidebar_width_px(self) -> str:
        """Get sidebar width as a string with 'px' suffix."""
        if self.sidebar_collapsed:
            return "64px"
        return f"{self.sidebar_width}px"
    
    @rx.var
    def visible_menu_items(self) -> list[tuple[str, str]]:
        """Get list of visible menu items as (name, icon) tuples."""
        all_items = [
            ("Projects", "folder"),
            ("Workflows", "git-branch"),
            ("Dashboards", "layout-dashboard"),
            ("Notebooks", "book"),
            ("Models", "brain"),
            ("Datasets", "database"),
            ("Notifications", "bell"),
            ("Reports", "bar-chart"),
        ]
        return [
            item for item in all_items
            if self.menu_item_visibility.get(item[0], True)
        ]
    
    @rx.var
    def menu_items_with_visibility(self) -> list[tuple[str, str, bool]]:
        """Get list of menu items with their visibility status as (name, icon, visible) tuples."""
        all_items = [
            ("Projects", "folder"),
            ("Workflows", "git-branch"),
            ("Dashboards", "layout-dashboard"),
            ("Notebooks", "book"),
            ("Models", "brain"),
            ("Datasets", "database"),
            ("Notifications", "bell"),
            ("Reports", "bar-chart"),
        ]
        return [
            (item[0], item[1], self.menu_item_visibility.get(item[0], True))
            for item in all_items
        ]
    
    @rx.event
    def toggle_sidebar(self):
        """Toggle sidebar collapsed state."""
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
    def toggle_favorites(self):
        """Toggle favorites section expansion."""
        self.favorites_expanded = not self.favorites_expanded
    
    @rx.event
    def toggle_objects(self):
        """Toggle objects section expansion."""
        self.objects_expanded = not self.objects_expanded
    
    @rx.event
    def toggle_collections(self):
        """Toggle collections section expansion."""
        self.collections_expanded = not self.collections_expanded
    
    @rx.event
    def select_menu_item(self, menu_item: str):
        """Select a menu item (Projects, Workflows, etc.)."""
        # Set selection immediately for instant feedback
        self.selected_menu_item = menu_item
        
        # Clear other selections
        from app.states.entities import EntitiesState
        from app.states.collections import CollectionsState
        EntitiesState.selected_object_type = ""
        CollectionsState.selected_collection_id = ""
        EntitiesState.is_loading = False
    
    @rx.event
    def toggle_workspace_dropdown(self):
        """Toggle the workspace dropdown menu."""
        self.workspace_dropdown_open = not self.workspace_dropdown_open
    
    @rx.event
    def close_workspace_dropdown(self):
        """Close the workspace dropdown menu."""
        self.workspace_dropdown_open = False
    
    @rx.event
    def navigate_to_settings(self):
        """Navigate to settings page."""
        self.workspace_dropdown_open = False
        return rx.redirect("/settings")
    
    @rx.event
    def select_settings_section(self, section: str):
        """Select a settings section."""
        self.selected_settings_section = section
    
    @rx.event
    def set_theme(self, theme: str):
        """Set the theme (Light, Dark, or System)."""
        self.theme = theme
    
    @rx.event
    def set_accent_color(self, color: str):
        """Set the accent color."""
        self.accent_color = color
        self.custom_accent_color = ""  # Clear custom color when selecting a preset
    
    @rx.event
    def set_custom_accent_color(self, color: str):
        """Set a custom accent color from hex input."""
        # Validate hex color format
        if color and (color.startswith("#") and len(color) == 7):
            self.accent_color = color
            self.custom_accent_color = color
    
    @rx.event
    def toggle_menu_item_visibility(self, menu_item: str):
        """Toggle visibility of a menu item."""
        if menu_item in self.menu_item_visibility:
            self.menu_item_visibility[menu_item] = not self.menu_item_visibility[menu_item]
    
    @rx.var
    def radio_button_background_color(self) -> str:
        """Get background color for radio buttons based on theme."""
        if self.theme == "Dark":
            return "rgb(16, 16, 18)"
        return "white"

