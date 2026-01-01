import reflex as rx
from app.pages.collections_home_page import collections_home_page
from app.pages.collection_page import collection_page
from app.pages.settings_page import (
    settings_page,
    settings_general_page,
    settings_appearance_page,
    settings_entities_page,
    settings_collections_page,
)
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

# Main index route - collections home page
# Initialize both collections and entities on load
app.add_page(collections_home_page, route="/", on_load=CollectionsState.on_load)

# Collection pages - dynamic route for individual collections
app.add_page(
    collection_page,
    route="/collections/[collection_id]",
    on_load=CollectionsState.on_load,
)

# Settings pages - redirect /settings to /settings/general
# Initialize collections on settings pages too for faster loading
app.add_page(settings_general_page, route="/settings", on_load=CollectionsState.on_load)
app.add_page(settings_general_page, route="/settings/general", on_load=CollectionsState.on_load)
app.add_page(settings_appearance_page, route="/settings/appearance", on_load=CollectionsState.on_load)
app.add_page(settings_entities_page, route="/settings/entities", on_load=CollectionsState.on_load)
app.add_page(settings_collections_page, route="/settings/collections", on_load=CollectionsState.on_load)