"""Generic page component that can be used for all routes."""
import reflex as rx
from app.components.main_sidebar import main_sidebar
from app.components.content_router import content_router
from app.components.create_collection_modal import create_collection_modal
from app.components.create_entity_modal import create_entity_modal


def generic_page() -> rx.Component:
    """Generic page layout used for all routes - content determined by URL."""
    return rx.el.div(
        main_sidebar(),
        rx.el.div(
            rx.el.div(
                content_router(),
                class_name="p-6 pt-6",
            ),
            class_name="flex-1 h-screen overflow-y-auto",
            style={"backgroundColor": "rgb(23, 23, 25)"},
        ),
        create_collection_modal(),
        create_entity_modal(),
        class_name="flex font-['Inter']",
        style={"backgroundColor": "rgb(16, 16, 18)"},
    )

