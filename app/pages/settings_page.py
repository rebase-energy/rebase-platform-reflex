import reflex as rx
from app.components.settings_sidebar import settings_sidebar
from app.components.settings_content import settings_content


def settings_page() -> rx.Component:
    """Settings page with sidebar navigation and content area."""
    return rx.el.div(
        settings_sidebar(),
        rx.el.div(
            rx.el.div(
                settings_content(),
                class_name="p-6",
            ),
            class_name="flex-1 h-screen overflow-y-auto",
            style={"backgroundColor": "rgb(23, 23, 25)"},
        ),
        class_name="flex font-['Inter']",
        style={"backgroundColor": "rgb(16, 16, 18)"},
    )

