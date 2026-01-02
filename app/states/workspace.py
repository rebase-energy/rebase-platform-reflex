import reflex as rx
import base64


# Workspace State Management
class WorkspaceState(rx.State):
    """State management for workspace UI, navigation, and settings."""
    
    # Database ID (set after loading from Supabase)
    workspace_id: str = ""
    
    # Workspace configuration
    workspace_name: str = "rebase-energy"
    workspace_slug: str = "rebase-energy"
    default_collection_id: str = ""  # Collection to show on login/start

    # Workspace branding
    workspace_logo_data_url: str = ""  # data:image/png;base64,...
    show_logo_upload_modal: bool = False
    _db_supports_logo_data_url: bool = False
    
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
    
    # Loading/sync state
    _workspace_loaded: bool = False
    
    @rx.var
    def current_settings_section_from_route(self) -> str:
        """Get current settings section from route."""
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
    def current_path(self) -> str:
        """Get current URL path."""
        try:
            return self.router.url.path  # type: ignore[attr-defined]
        except Exception:
            return f"/{self.workspace_slug}"
    
    @rx.var
    def is_entity_route(self) -> bool:
        """Check if on an entity route."""
        path = self.current_path
        return path.startswith(f"/{self.workspace_slug}/entities/")
    
    @rx.var
    def is_collection_route(self) -> bool:
        """Check if on a collection route."""
        path = self.current_path
        return path.startswith(f"/{self.workspace_slug}/collections/")
    
    @rx.var
    def is_menu_route(self) -> bool:
        """Check if on a menu item route."""
        path = self.current_path
        menu_routes = [
            f"/{self.workspace_slug}/projects",
            f"/{self.workspace_slug}/workflows",
            f"/{self.workspace_slug}/dashboards",
            f"/{self.workspace_slug}/notebooks",
            f"/{self.workspace_slug}/models",
            f"/{self.workspace_slug}/datasets",
            f"/{self.workspace_slug}/notifications",
            f"/{self.workspace_slug}/reports",
        ]
        return path in menu_routes
    
    @rx.var
    def current_menu_item_name(self) -> str:
        """Extract menu item name from current route."""
        if self.is_menu_route:
            parts = self.current_path.split("/")
            if len(parts) >= 3:
                return parts[2].capitalize()
        return ""
    
    @rx.var
    def workspace_base_url(self) -> str:
        """Get the base URL for the workspace (e.g., '/rebase-energy')."""
        return f"/{self.workspace_slug}"
    
    @rx.var
    def get_sidebar_width_px(self) -> str:
        """Get sidebar width as a string with 'px' suffix."""
        if self.sidebar_collapsed:
            return "0px"  # Completely hidden when collapsed
        return f"{self.sidebar_width}px"
    
    @rx.var
    def current_route(self) -> str:
        """Get the current route path."""
        try:
            return self.router.url.path  # type: ignore[attr-defined]
        except Exception:
            return f"/{self.workspace_slug}"
    
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
        self._save_workspace_to_db()
    
    @rx.event
    def set_sidebar_width(self, width: str):
        """Update sidebar width from resize handle (format: 'width')."""
        try:
            width_int = int(width)
            # Clamp width between 200px and 600px
            self.sidebar_width = max(200, min(600, width_int))
            self._save_workspace_to_db()
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
        """Set the selected menu item."""
        self.selected_menu_item = menu_item
    
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
        return rx.redirect(f"/{self.workspace_slug}/settings")
    
    @rx.event
    def set_workspace_name(self, name: str):
        """Set the workspace name."""
        self.workspace_name = name
        # Update slug (convert to lowercase, replace spaces with hyphens)
        self.workspace_slug = name.lower().replace(" ", "-").replace("_", "-")
        self._save_workspace_to_db()
    
    @rx.event
    def select_settings_section(self, section: str):
        """Select a settings section."""
        self.selected_settings_section = section
    
    @rx.event
    def set_theme(self, theme: str):
        """Set the theme (Light, Dark, or System)."""
        self.theme = theme
        self._save_workspace_to_db()
    
    @rx.event
    def set_accent_color(self, color: str):
        """Set the accent color."""
        self.accent_color = color
        self.custom_accent_color = ""  # Clear custom color when selecting a preset
        self._save_workspace_to_db()
    
    @rx.event
    def set_custom_accent_color(self, color: str):
        """Set a custom accent color from hex input."""
        # Validate hex color format
        if color and (color.startswith("#") and len(color) == 7):
            self.accent_color = color
            self.custom_accent_color = color
            self._save_workspace_to_db()
    
    @rx.event
    def toggle_menu_item_visibility(self, menu_item: str):
        """Toggle visibility of a menu item."""
        if menu_item in self.menu_item_visibility:
            self.menu_item_visibility[menu_item] = not self.menu_item_visibility[menu_item]
            self._save_workspace_to_db()
    
    @rx.var
    def radio_button_background_color(self) -> str:
        """Get background color for radio buttons based on theme."""
        if self.theme == "Dark":
            return "rgb(16, 16, 18)"
        return "white"
    
    @rx.event
    def load_workspace_from_db(self):
        """Load workspace settings from Supabase."""
        if self._workspace_loaded:
            return
        
        try:
            from app.services.supabase_service import SupabaseService
            
            workspace = SupabaseService.get_workspace(self.workspace_slug)
            if workspace:
                self.workspace_id = workspace.get("id", "")
                self.workspace_name = workspace.get("name", self.workspace_name)
                self.workspace_slug = workspace.get("slug", self.workspace_slug)
                self.theme = workspace.get("theme", self.theme)
                self.accent_color = workspace.get("accent_color", self.accent_color)
                self.sidebar_collapsed = workspace.get("sidebar_collapsed", self.sidebar_collapsed)
                self.sidebar_width = workspace.get("sidebar_width", self.sidebar_width)
                self.default_collection_id = workspace.get("default_collection_id", "") or ""
                self._db_supports_logo_data_url = "logo_data_url" in workspace
                if self._db_supports_logo_data_url:
                    self.workspace_logo_data_url = workspace.get("logo_data_url", "") or ""
                
                # Load menu item visibility if present
                menu_visibility = workspace.get("menu_item_visibility")
                if menu_visibility and isinstance(menu_visibility, dict):
                    self.menu_item_visibility = menu_visibility
            else:
                # Create workspace if it doesn't exist
                self._create_workspace_in_db()
            
            self._workspace_loaded = True
        except Exception as e:
            print(f"Failed to load workspace from database: {e}")
            self._workspace_loaded = True  # Prevent retrying on every render
    
    def _create_workspace_in_db(self):
        """Create the workspace in Supabase."""
        try:
            from app.services.supabase_service import SupabaseService
            
            data = {
                "name": self.workspace_name,
                "slug": self.workspace_slug,
                "theme": self.theme,
                "accent_color": self.accent_color,
                "sidebar_collapsed": self.sidebar_collapsed,
                "sidebar_width": self.sidebar_width,
                "default_collection_id": self.default_collection_id or None,
                "menu_item_visibility": self.menu_item_visibility,
            }
            result = SupabaseService.create_workspace(data)
            if result:
                self.workspace_id = result.get("id", "")
                self._db_supports_logo_data_url = "logo_data_url" in result
                if self._db_supports_logo_data_url:
                    self.workspace_logo_data_url = result.get("logo_data_url", "") or ""
        except Exception as e:
            print(f"Failed to create workspace in database: {e}")
    
    def _save_workspace_to_db(self):
        """Save workspace settings to Supabase."""
        if not self.workspace_id:
            return
        
        try:
            from app.services.supabase_service import SupabaseService
            
            data = {
                "name": self.workspace_name,
                "slug": self.workspace_slug,
                "theme": self.theme,
                "accent_color": self.accent_color,
                "sidebar_collapsed": self.sidebar_collapsed,
                "sidebar_width": self.sidebar_width,
                "default_collection_id": self.default_collection_id or None,
                "menu_item_visibility": self.menu_item_visibility,
            }
            if self._db_supports_logo_data_url:
                data["logo_data_url"] = self.workspace_logo_data_url or None
            SupabaseService.update_workspace(self.workspace_id, data)
        except Exception as e:
            print(f"Failed to save workspace to database: {e}")
    
    @rx.event
    def set_default_collection(self, collection_id: str):
        """Set the default collection for the workspace."""
        self.default_collection_id = collection_id
        self._save_workspace_to_db()

    @rx.event
    def toggle_logo_upload_modal(self):
        """Toggle the workspace logo upload modal."""
        self.show_logo_upload_modal = not self.show_logo_upload_modal

    @rx.event
    def close_logo_upload_modal(self):
        """Close the workspace logo upload modal."""
        self.show_logo_upload_modal = False

    @rx.event
    def clear_workspace_logo(self):
        """Clear the current workspace logo."""
        self.workspace_logo_data_url = ""
        self._save_workspace_to_db()
        return rx.toast.success("Workspace logo removed.")

    @rx.event
    async def handle_workspace_logo_upload(self, files: list[rx.UploadFile]):
        """Handle PNG logo uploads from the drag-and-drop zone."""
        if not files:
            return rx.toast.error("No file received.")

        file = files[0]
        filename = (getattr(file, "filename", "") or "").lower()
        content_type = getattr(file, "content_type", "") or ""

        data = await file.read()
        if len(data) > 10 * 1024 * 1024:
            return rx.toast.error("Logo must be under 10MB.")

        # Enforce PNG (UI also restricts to PNG via accept=...)
        if content_type not in ("image/png", "") and not filename.endswith(".png"):
            return rx.toast.error("Please upload a PNG file.")
        if not filename.endswith(".png") and content_type != "image/png":
            return rx.toast.error("Please upload a PNG file.")

        b64 = base64.b64encode(data).decode("utf-8")
        self.workspace_logo_data_url = f"data:image/png;base64,{b64}"
        self.show_logo_upload_modal = False
        self._save_workspace_to_db()
        return rx.toast.success("Workspace logo updated.")

