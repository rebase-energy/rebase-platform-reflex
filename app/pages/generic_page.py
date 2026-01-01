"""Generic page component that can be used for all routes."""
import reflex as rx
from app.components.main_sidebar import main_sidebar
from app.components.content_router import content_router, content_header
from app.components.create_collection_modal import create_collection_modal
from app.components.create_entity_modal import create_entity_modal
from app.states.workspace import WorkspaceState


def sidebar_toggle_button() -> rx.Component:
    """Toggle button shown when sidebar is collapsed."""
    return rx.cond(
        WorkspaceState.sidebar_collapsed,
        rx.el.button(
            rx.icon("panel-left", class_name="h-4 w-4 text-gray-400"),
            on_click=WorkspaceState.toggle_sidebar,
            class_name="p-2 hover:bg-gray-800/50 rounded-md transition-colors border border-gray-700/50 flex-shrink-0 mr-3",
            style={"backgroundColor": "rgb(23, 23, 25)"},
            title="Expand sidebar",
        ),
        rx.fragment(),
    )


def generic_page() -> rx.Component:
    """Generic page layout used for all routes - content determined by URL."""
    return rx.el.div(
        main_sidebar(),
        rx.el.div(
            # Top header row with toggle button and content header
            rx.el.div(
                sidebar_toggle_button(),
                content_header(),
                class_name="flex items-center px-6 pt-6 pb-4",
            ),
            # Content area
            rx.el.div(
                content_router(),
                class_name="px-6 pb-6",
            ),
            class_name="flex-1 h-screen overflow-y-auto",
            style={"backgroundColor": "rgb(23, 23, 25)"},
        ),
        create_collection_modal(),
        create_entity_modal(),
        class_name="flex font-['Inter']",
        style={"backgroundColor": "rgb(16, 16, 18)"},
    )

