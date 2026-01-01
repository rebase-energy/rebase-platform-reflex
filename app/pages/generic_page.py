"""Generic page component that can be used for all routes."""
import reflex as rx
from app.components.collections_sidebar import collections_sidebar
from app.components.content_router import content_router
from app.components.create_collection_modal import create_collection_modal
from app.components.add_item_modal import add_item_modal


def generic_page() -> rx.Component:
    """Generic page layout used for all routes - content determined by URL."""
    return rx.el.div(
        collections_sidebar(),
        rx.el.div(
            rx.el.div(
                content_router(),
                class_name="p-6 pt-6",
            ),
            class_name="flex-1 h-screen overflow-y-auto",
            style={"backgroundColor": "rgb(23, 23, 25)"},
        ),
        create_collection_modal(),
        add_item_modal(),
        class_name="flex font-['Inter']",
        style={"backgroundColor": "rgb(16, 16, 18)"},
    )

