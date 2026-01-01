import reflex as rx
from app.pages.lists_page import lists_page
from app.pages.settings_page import settings_page
from app.states.collections import CollectionsState
from app.states.entities import EntitiesState


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

# Main index route - lists page
# Initialize both collections and entities on load
app.add_page(lists_page, route="/", on_load=CollectionsState.on_load)

# Settings page
app.add_page(settings_page, route="/settings")