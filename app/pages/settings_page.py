import reflex as rx
from app.components.settings_sidebar import settings_sidebar
from app.components.settings_content import settings_content
from app.components.create_collection_modal import create_collection_modal
from app.states.workspace import WorkspaceState


def _settings_page_content(selected_section: str) -> rx.Component:
    """Shared settings page content."""
    return rx.el.div(
        settings_sidebar(selected_section),
        rx.el.div(
            rx.el.div(
                settings_content(selected_section),
                class_name="p-6 pt-6",
            ),
            class_name="flex-1 h-screen overflow-y-auto",
            style={"backgroundColor": "rgb(23, 23, 25)"},
        ),
        create_collection_modal(),
        class_name="flex font-['Inter']",
        style={"backgroundColor": "rgb(16, 16, 18)"},
    )


def settings_page() -> rx.Component:
    """Settings page - defaults to General."""
    return _settings_page_content("General")


def settings_general_page() -> rx.Component:
    """Settings General page."""
    return _settings_page_content("General")


def settings_appearance_page() -> rx.Component:
    """Settings Appearance page."""
    return _settings_page_content("Appearance")


def settings_entities_page() -> rx.Component:
    """Settings Entities page."""
    return _settings_page_content("Entities")


def settings_collections_page() -> rx.Component:
    """Settings Collections page."""
    return _settings_page_content("Collections")

