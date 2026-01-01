import reflex as rx
from app.states.state import DashboardState, Site
from app.components.list_view import list_view, list_item
from app.components.sidebar import sidebar
from app.components.header import header


def render_site_item(site: Site) -> rx.Component:
    """Render a site as a list item."""
    return list_item(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    site["name"],
                    class_name="text-white font-semibold text-base",
                ),
                rx.el.span(
                    site["type"],
                    class_name="text-gray-400 text-sm ml-2",
                ),
                class_name="flex items-center",
            ),
            rx.el.div(
                rx.el.span(
                    rx.cond(
                        site["capacity"] != "",
                        site["capacity"],
                        "N/A",
                    ),
                    class_name="text-gray-300 text-sm",
                ),
                rx.el.span(
                    site["status"],
                    class_name="text-gray-400 text-sm ml-4",
                ),
                class_name="flex items-center mt-2",
            ),
            class_name="flex flex-col",
        ),
    )


def list_demo() -> rx.Component:
    """Demo page showing the list view primitive."""
    return rx.el.div(
        sidebar(),
        rx.el.div(
            header(),
            rx.el.main(
                rx.el.div(
                    rx.el.h1(
                        "List View Demo",
                        class_name="text-white font-bold text-2xl mb-2",
                    ),
                    rx.el.p(
                        "This is a demonstration of the list view primitive component.",
                        class_name="text-gray-400 text-sm mb-6",
                    ),
                    list_view(
                        items=DashboardState.sites,
                        render_item=render_site_item,
                        empty_message="No sites found",
                    ),
                    class_name="p-6",
                ),
            ),
            class_name="flex-1 h-screen overflow-y-auto",
        ),
        class_name="flex bg-gray-900 font-['Inter']",
    )

