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
            rx.el.div(
                rx.el.span(
                    f"{EntitiesState.active_object_type} view coming soon",
                    class_name="text-gray-400 text-sm",
                ),
                class_name="flex items-center justify-center py-12",
            ),
        ),
    )


def _timeseries_entity_table() -> rx.Component:
    """Table view for TimeSeries entities using centralized table_view component."""
    
    # Define columns for the TimeSeries entity table
    def name_column_render(item):
        return rx.el.span(
            item["name"],
            class_name="text-white text-sm",
            style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
        )
    
    def description_column_render(item):
        return rx.el.span(
            item["description"],
            class_name="text-gray-300 text-sm",
            style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
        )
    
    def unit_column_render(item):
        return rx.el.span(
            item["unit"],
            class_name="text-gray-300 text-sm",
            style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
        )
    
    def site_column_render(item):
        return rx.el.span(
            item["site_name"],
            class_name="text-gray-300 text-sm",
            style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
        )
    
    def value_column_render(item):
        return rx.el.span(
            rx.cond(
                item["value"] != 0,
                item["value"],
                "0.00",
            ),
            class_name="text-gray-300 text-sm font-mono",
            style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
        )
    
    def type_column_render(item):
        return rx.el.span(
            item["type"],
            class_name=rx.cond(
                item["type"] == "actual",
                "px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-400",
                rx.cond(
                    item["type"] == "forecast",
                    "px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-400",
                    "px-2 py-0.5 rounded text-xs font-medium bg-yellow-500/20 text-yellow-400",
                ),
            ),
        )
    
    columns: list[TableColumn] = [
        {"key": "name", "label": "Name", "width": CollectionsState.column_width_name, "render": name_column_render},
        {"key": "description", "label": "Description", "width": CollectionsState.column_width_description, "render": description_column_render},
        {"key": "unit", "label": "Unit", "width": CollectionsState.column_width_unit, "render": unit_column_render},
        {"key": "site_name", "label": "Site", "width": CollectionsState.column_width_site_name, "render": site_column_render},
        {"key": "value", "label": "Value", "width": CollectionsState.column_width_value, "render": value_column_render},
        {"key": "type", "label": "Type", "width": CollectionsState.column_width_type, "render": type_column_render},
    ]
    
    return rx.el.div(
        # Entity header with name
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "TimeSeries",
                    class_name="text-white font-bold text-xl",
                ),
                rx.el.span(
                    "All TimeSeries items",
                    class_name="text-gray-400 text-sm ml-2",
                ),
                class_name="flex items-center",
            ),
            class_name="mb-6",
        ),
        # Search, Sort, Filter header
        table_header(),
        # Data table from centralized component
        data_table(
            items=EntitiesState.all_time_series_entities,
            columns=columns,
            on_column_width_change=CollectionsState.set_column_width,
            on_add_item=CollectionsState.toggle_add_item_modal,
            resize_input_id="column-resize-input-entity",
            resize_handle_class="resize-handle-entity",
        ),
        class_name="w-full",
    )


def _collection_view() -> rx.Component:
    """Display collection view - either time series cards or table view."""
    return rx.el.div(
        # Collection header with name and emoji
        rx.el.div(
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
                    # Emoji picker (positioned relative to button)
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
            class_name="mb-6",
        ),
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
    
    # Define columns for the collection table
    def name_column_render(item):
        return rx.el.span(
            item["name"],
            class_name="text-white text-sm",
            style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
        )
    
    def description_column_render(item):
        return rx.el.span(
            item["description"],
            class_name="text-gray-300 text-sm",
            style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
        )
    
    def unit_column_render(item):
        return rx.el.span(
            item["unit"],
            class_name="text-gray-300 text-sm",
            style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
        )
    
    def site_column_render(item):
        return rx.el.span(
            item["site_name"],
            class_name="text-gray-300 text-sm",
            style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
        )
    
    def value_column_render(item):
        return rx.el.span(
            rx.cond(
                item["value"] != 0,
                item["value"],
                "0.00",
            ),
            class_name="text-gray-300 text-sm font-mono",
            style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
        )
    
    def type_column_render(item):
        return rx.el.span(
            item["type"],
            class_name=rx.cond(
                item["type"] == "actual",
                "px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-400",
                rx.cond(
                    item["type"] == "forecast",
                    "px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-400",
                    "px-2 py-0.5 rounded text-xs font-medium bg-yellow-500/20 text-yellow-400",
                ),
            ),
        )
    
    columns: list[TableColumn] = [
        {"key": "name", "label": "Name", "width": CollectionsState.column_width_name, "render": name_column_render},
        {"key": "description", "label": "Description", "width": CollectionsState.column_width_description, "render": description_column_render},
        {"key": "unit", "label": "Unit", "width": CollectionsState.column_width_unit, "render": unit_column_render},
        {"key": "site_name", "label": "Site", "width": CollectionsState.column_width_site_name, "render": site_column_render},
        {"key": "value", "label": "Value", "width": CollectionsState.column_width_value, "render": value_column_render},
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

