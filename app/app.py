import reflex as rx
from app.pages.generic_page import generic_page
# Demo pages disabled in production
# from app.pages.demo_table_view import demo_table_view_page
# from app.pages.demo_timeseries_view import demo_timeseries_view_page
from app.pages.settings_page import (
    settings_page,
    settings_general_page,
    settings_appearance_page,
    settings_entities_page,
    settings_collections_page,
)
from app.states.collections import CollectionsState
from app.states.entities import EntitiesState
from app.states.workspace import WorkspaceState


app = rx.App(
    theme=rx.theme(
        appearance="light", has_background=True, radius="medium", accent_color="green"
    ),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)


# Get the workspace slug from WorkspaceState
# Note: This is set at initialization time, so it uses the default value
WORKSPACE_SLUG = "rebase-energy"  # This will match WorkspaceState.workspace_slug default


class RootRedirectState(rx.State):
    """State for handling root redirect."""
    
    @rx.event
    def on_load(self):
        """Redirect to default collection or workspace home on load."""
        # Load workspace from database first
        from app.services.supabase_service import SupabaseService
        
        try:
            workspace = SupabaseService.get_workspace(WORKSPACE_SLUG)
            if workspace:
                default_collection_id = workspace.get("default_collection_id")
                if default_collection_id:
                    # Redirect to default collection
                    return rx.redirect(f"/{WORKSPACE_SLUG}/collections/{default_collection_id}")
        except Exception as e:
            print(f"Error loading workspace for redirect: {e}")
        
        # Fallback to workspace home
        return rx.redirect(f"/{WORKSPACE_SLUG}")


def root_redirect() -> rx.Component:
    """Redirect from root to workspace slug."""
    return rx.fragment(
        rx.text("Redirecting...", class_name="text-gray-400"),
    )


# Root redirect to workspace slug / default collection
app.add_page(root_redirect, route="/", on_load=RootRedirectState.on_load)

# Login redirect - same behavior as root (redirects to default collection)
app.add_page(root_redirect, route="/login", on_load=RootRedirectState.on_load)
app.add_page(root_redirect, route=f"/{WORKSPACE_SLUG}/login", on_load=RootRedirectState.on_load)

# Main index route - collections home page
app.add_page(generic_page, route=f"/{WORKSPACE_SLUG}", on_load=[WorkspaceState.load_workspace_from_db, CollectionsState.on_load])

# Collection pages - dynamic route for individual collections
app.add_page(
    generic_page,
    route=f"/{WORKSPACE_SLUG}/collections/[collection_id]",
    on_load=[WorkspaceState.load_workspace_from_db, CollectionsState.on_load_collection_page],
)

# Entity pages - dynamic route for entity types
app.add_page(
    generic_page,
    route=f"/{WORKSPACE_SLUG}/entities/[entity_name]",
    on_load=[WorkspaceState.load_workspace_from_db, EntitiesState.on_load_entity_page],
)

# Menu item pages
app.add_page(generic_page, route=f"/{WORKSPACE_SLUG}/projects")
app.add_page(generic_page, route=f"/{WORKSPACE_SLUG}/workflows")
app.add_page(generic_page, route=f"/{WORKSPACE_SLUG}/dashboards")
app.add_page(generic_page, route=f"/{WORKSPACE_SLUG}/notebooks")
app.add_page(generic_page, route=f"/{WORKSPACE_SLUG}/models")
app.add_page(generic_page, route=f"/{WORKSPACE_SLUG}/datasets")
app.add_page(generic_page, route=f"/{WORKSPACE_SLUG}/notifications")
app.add_page(generic_page, route=f"/{WORKSPACE_SLUG}/reports")

# Settings pages - redirect /settings to /settings/general
# Initialize workspace and collections on settings pages
app.add_page(settings_general_page, route=f"/{WORKSPACE_SLUG}/settings", on_load=[WorkspaceState.load_workspace_from_db, CollectionsState.on_load])
app.add_page(settings_general_page, route=f"/{WORKSPACE_SLUG}/settings/general", on_load=[WorkspaceState.load_workspace_from_db, CollectionsState.on_load])
app.add_page(settings_appearance_page, route=f"/{WORKSPACE_SLUG}/settings/appearance", on_load=[WorkspaceState.load_workspace_from_db, CollectionsState.on_load])
app.add_page(settings_entities_page, route=f"/{WORKSPACE_SLUG}/settings/entities", on_load=[WorkspaceState.load_workspace_from_db, CollectionsState.on_load])
app.add_page(settings_collections_page, route=f"/{WORKSPACE_SLUG}/settings/collections", on_load=[WorkspaceState.load_workspace_from_db, CollectionsState.on_load])

# Demo pages - standalone component demos (disabled in production due to prerendering issues)
# These cause 500 errors during production builds because they access state during SSR
# Uncomment for local development:
# app.add_page(demo_table_view_page, route="/demo/table-view", title="Table View Demo")
# app.add_page(demo_timeseries_view_page, route="/demo/timeseries-view", title="Time Series View Demo")