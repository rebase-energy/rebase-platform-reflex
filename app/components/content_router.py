"""Content router component that determines what to display based on the current route."""
import reflex as rx
from app.states.collections import CollectionsState
from app.states.entities import EntitiesState
from app.states.workspace import WorkspaceState
from app.components.table_view import data_table, TableColumn
from app.components.timeseries_card_view import timeseries_card_view
from app.components.table_header import table_header
from app.components.emoji_picker import emoji_picker

# Default workspace slug - matches WorkspaceState.workspace_slug default
DEFAULT_WORKSPACE_SLUG = "rebase-energy"


def entity_badge(entity_type: str, size: str = "sm") -> rx.Component:
    """
    Render an entity type as a styled badge with mono font.
    Used consistently throughout the app to indicate entity objects.
    
    Args:
        entity_type: The entity type name
        size: Size variant - "sm" for small, "lg" for large headers
    """
    if size == "lg":
        return rx.el.span(
            entity_type,
            class_name="px-3 py-1 rounded text-base font-mono bg-gray-700/50 text-white font-semibold",
        )
    return rx.el.span(
        entity_type,
        class_name="px-2 py-0.5 rounded text-xs font-mono bg-gray-700/50 text-gray-300",
    )


def content_header() -> rx.Component:
    """
    Content header that displays the appropriate title based on current route.
    This is displayed in a row with the sidebar toggle button.
    """
    return rx.cond(
        WorkspaceState.is_menu_route,
        # Menu item header
        rx.el.div(
            rx.el.h2(
                WorkspaceState.current_menu_item_name,
                class_name="text-white font-bold text-xl",
            ),
            class_name="flex items-center",
        ),
        rx.cond(
            WorkspaceState.is_entity_route,
            # Entity header
            rx.el.div(
                entity_badge(EntitiesState.active_object_type, size="lg"),
                rx.el.span(
                    f"All {EntitiesState.active_object_type} entities",
                    class_name="text-gray-400 text-sm ml-3",
                ),
                class_name="flex items-center",
            ),
            rx.cond(
                CollectionsState.active_collection,
                # Collection header with emoji
                rx.el.div(
                    # Emoji button with picker
                    rx.el.div(
                        rx.el.button(
                            rx.el.span(
                                rx.cond(
                                    CollectionsState.active_collection["emoji"] != "",
                                    CollectionsState.active_collection["emoji"],
                                    "📋",
                                ),
                                class_name="text-2xl",
                            ),
                            on_click=CollectionsState.toggle_emoji_picker,
                            class_name="w-10 h-10 flex items-center justify-center hover:bg-gray-800 rounded-md transition-colors",
                        ),
                        emoji_picker(),
                        class_name="relative mr-3",
                    ),
                    # Collection name and type
                    rx.el.div(
                        rx.el.h2(
                            CollectionsState.active_collection["name"],
                            class_name="text-white font-bold text-xl",
                        ),
                        rx.el.span(
                            CollectionsState.active_collection.get("object_type", "TimeSeries"),
                            class_name="px-2 py-0.5 rounded text-xs font-mono bg-gray-700/50 text-gray-300 ml-2",
                        ),
                        class_name="flex items-center",
                    ),
                    class_name="flex items-center relative",
                ),
                # No collection selected - empty header
                rx.fragment(),
            ),
        ),
    )


def content_router() -> rx.Component:
    """Route-driven content display - shows the appropriate view based on the current URL path."""
    return rx.cond(
        WorkspaceState.is_menu_route,
        # Show menu item "coming soon" view
        rx.el.div(
            rx.el.span(
                f"{WorkspaceState.current_menu_item_name} coming soon",
                class_name="text-gray-400 text-sm",
            ),
            class_name="flex items-center justify-center py-12",
        ),
        rx.cond(
            WorkspaceState.is_entity_route,
            # Show entity/object type view
            _entity_view(),
            rx.cond(
                CollectionsState.active_collection,
                # Show collection view
                _collection_view(),
                # No collection selected
                rx.el.div(
                    rx.el.span(
                        "No collection selected. Select a collection to get started.",
                        class_name="text-gray-400 text-sm",
                    ),
                    class_name="flex items-center justify-center py-12",
                ),
            ),
        ),
    )


def _entity_view() -> rx.Component:
    """Display entity/object type table view."""
    return rx.cond(
        EntitiesState.is_loading,
        # Show loading spinner
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        class_name="w-8 h-8 border-4 border-gray-700 border-t-white rounded-full animate-spin",
                    ),
                    rx.el.span(
                        "Loading...",
                        class_name="text-gray-400 text-sm ml-3",
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex items-center justify-center",
            ),
            class_name="flex items-center justify-center py-12 min-h-[400px]",
        ),
        rx.cond(
            EntitiesState.active_object_type == "TimeSeries",
            _timeseries_entity_table(),
            rx.cond(
                EntitiesState.active_object_type == "Sites",
                _sites_entity_table(),
                rx.cond(
                    EntitiesState.active_object_type == "Assets",
                    _assets_entity_table(),
                    rx.el.div(
                        rx.el.span(
                            f"{EntitiesState.active_object_type} view coming soon",
                            class_name="text-gray-400 text-sm",
                        ),
                        class_name="flex items-center justify-center py-12",
                    ),
                ),
            ),
        ),
    )


# =============================================================================
# ENTITY TABLE CONFIGURATIONS
# Define column configurations for each entity type
# =============================================================================

def _get_entity_columns(entity_type: str) -> list[TableColumn]:
    """Get column configuration for an entity type."""
    from app.components.table_view import text_cell, badge_cell, status_cell, value_cell
    
    if entity_type == "TimeSeries":
        # Custom renderer for type column with conditional styling
        def type_column_render(item):
            return rx.el.span(
                item["type"],
                class_name=rx.cond(
                    item["type"] == "actual",
                    "px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-400",
                    rx.cond(
                        item["type"] == "forecast",
                        "px-2 py-0.5 rounded text-xs font-medium bg-blue-500/20 text-blue-400",
                        "px-2 py-0.5 rounded text-xs font-medium bg-yellow-500/20 text-yellow-400",
                    ),
                ),
            )
        
        return [
            {"key": "name", "label": "Name", "width": 200, "render": text_cell("name", bold=True, color="white")},
            {"key": "description", "label": "Description", "width": 250, "render": text_cell("description")},
            {"key": "unit", "label": "Unit", "width": 100, "render": text_cell("unit")},
            {"key": "site_name", "label": "Site", "width": 150, "render": text_cell("site_name")},
            {"key": "value", "label": "Value", "width": 100, "render": value_cell("value")},
            {"key": "type", "label": "Type", "width": 100, "render": type_column_render},
        ]
    
    elif entity_type == "Sites":
        return [
            {"key": "name", "label": "Name", "width": 200, "render": text_cell("name", bold=True, color="white")},
            {"key": "description", "label": "Description", "width": 250, "render": text_cell("description")},
            {"key": "site_type", "label": "Type", "width": 120, "render": badge_cell("site_type", bg_color="blue-500/20", text_color="blue-400")},
            {"key": "capacity", "label": "Capacity (kW)", "width": 120, "render": value_cell("capacity")},
            {"key": "location", "label": "Location", "width": 180, "render": text_cell("location")},
            {"key": "status", "label": "Status", "width": 100, "render": status_cell("status", active_value="Active")},
        ]
    
    elif entity_type == "Assets":
        return [
            {"key": "name", "label": "Name", "width": 200, "render": text_cell("name", bold=True, color="white")},
            {"key": "description", "label": "Description", "width": 250, "render": text_cell("description")},
            {"key": "asset_type", "label": "Asset Type", "width": 140, "render": badge_cell("asset_type", bg_color="purple-500/20", text_color="purple-400")},
            {"key": "site_name", "label": "Site", "width": 180, "render": text_cell("site_name")},
            {"key": "status", "label": "Status", "width": 100, "render": status_cell("status", active_value="Active")},
        ]
    
    # Default columns for unknown entity types
    return [
        {"key": "name", "label": "Name", "width": 200, "render": text_cell("name", bold=True, color="white")},
        {"key": "description", "label": "Description", "width": 300, "render": text_cell("description")},
    ]


def _entity_table(
    entity_type: str,
    items: list,
    resize_id_suffix: str,
) -> rx.Component:
    """
    Unified entity table component (header is in content_header).
    
    Args:
        entity_type: The type of entity (TimeSeries, Sites, Assets)
        items: The list of entities to display
        resize_id_suffix: Suffix for resize input IDs to ensure uniqueness
    """
    columns = _get_entity_columns(entity_type)
    
    return rx.el.div(
        # Search, Sort, Filter header
        table_header(),
        # Data table from centralized component
        data_table(
            items=items,
            columns=columns,
            on_column_width_change=CollectionsState.set_column_width,
            on_add_item=CollectionsState.toggle_add_item_modal,
            resize_input_id=f"column-resize-input-{resize_id_suffix}",
            resize_handle_class=f"resize-handle-{resize_id_suffix}",
        ),
        class_name="w-full",
    )


def _timeseries_entity_table() -> rx.Component:
    """Table view for TimeSeries entities."""
    return _entity_table(
        entity_type="TimeSeries",
        items=EntitiesState.all_time_series_entities,
        resize_id_suffix="timeseries",
    )


def _sites_entity_table() -> rx.Component:
    """Table view for Site entities."""
    return _entity_table(
        entity_type="Sites",
        items=EntitiesState.all_site_entities,
        resize_id_suffix="sites",
    )


def _assets_entity_table() -> rx.Component:
    """Table view for Asset entities."""
    return _entity_table(
        entity_type="Assets",
        items=EntitiesState.all_asset_entities,
        resize_id_suffix="assets",
    )


def _collection_view() -> rx.Component:
    """Display collection view - either time series cards or table view (header is in content_header)."""
    return rx.el.div(
        # Check view type and render accordingly
        rx.cond(
            CollectionsState.active_collection_view_type == "time_series_cards",
            # Time Series Card Layout using centralized view component
            timeseries_card_view(
                items=CollectionsState.esett_card_data,
                columns=CollectionsState.timeseries_card_columns,
                on_column_toggle=CollectionsState.toggle_timeseries_card_columns,
                show_column_toggle=True,
            ),
            # Default table view using centralized table component
            _collection_table_view(),
        ),
    )


def _collection_table_view() -> rx.Component:
    """Table view for collection items using centralized table_view component."""
    from app.components.table_view import text_cell, value_cell
    
    # Custom renderer for type column with conditional styling
    def type_column_render(item):
        return rx.el.span(
            item["type"],
            class_name=rx.cond(
                item["type"] == "actual",
                "px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-400",
                rx.cond(
                    item["type"] == "forecast",
                    "px-2 py-0.5 rounded text-xs font-medium bg-blue-500/20 text-blue-400",
                    "px-2 py-0.5 rounded text-xs font-medium bg-yellow-500/20 text-yellow-400",
                ),
            ),
        )
    
    columns: list[TableColumn] = [
        {"key": "name", "label": "Name", "width": CollectionsState.column_width_name, "render": text_cell("name", bold=True, color="white")},
        {"key": "description", "label": "Description", "width": CollectionsState.column_width_description, "render": text_cell("description")},
        {"key": "unit", "label": "Unit", "width": CollectionsState.column_width_unit, "render": text_cell("unit")},
        {"key": "site_name", "label": "Site", "width": CollectionsState.column_width_site_name, "render": text_cell("site_name")},
        {"key": "value", "label": "Value", "width": CollectionsState.column_width_value, "render": value_cell("value")},
        {"key": "type", "label": "Type", "width": CollectionsState.column_width_type, "render": type_column_render},
    ]
    
    return rx.el.div(
        # Search, Sort, Filter header
        table_header(),
        # Data table from centralized component
        data_table(
            items=CollectionsState.selected_collection_entities,
            columns=columns,
            on_column_width_change=CollectionsState.set_column_width,
            on_add_item=CollectionsState.toggle_add_item_modal,
            resize_input_id="column-resize-input-collection",
            resize_handle_class="resize-handle-collection",
        ),
        class_name="w-full",
    )

