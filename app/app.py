import reflex as rx
from app.states.state import DashboardState
from app.components.sidebar import sidebar
from app.components.header import header
from app.components.site_card import site_card
from app.components.add_site_modal import add_site_modal


def index() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.div(
            header(),
            rx.el.main(
                rx.el.div(
                    rx.foreach(DashboardState.sites, site_card),
                    class_name="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6",
                )
            ),
            class_name="flex-1 h-screen overflow-y-auto",
        ),
        add_site_modal(),
        class_name="flex bg-gray-900 font-['Inter']",
    )


app = rx.App(
    theme=rx.theme(
        appearance="light", has_background=True, radius="medium", accent_color="gray"
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
app.add_page(index, route="/", on_load=DashboardState.on_load)