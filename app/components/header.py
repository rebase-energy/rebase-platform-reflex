import reflex as rx
from app.states.state import DashboardState


def header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.icon("bar-chart-horizontal", class_name="h-5 w-5 text-gray-400"),
                rx.el.span("/", class_name="text-gray-400"),
                rx.el.span("sites", class_name="text-white font-medium"),
                class_name="flex items-center space-x-2",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("plus", class_name="mr-2 h-4 w-4"),
                    "Add site",
                    on_click=DashboardState.toggle_add_site_modal,
                    class_name="flex items-center bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-600",
                ),
                class_name="flex-grow",
            ),
            class_name="flex items-center space-x-4",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("download", class_name="mr-2 h-4 w-4"),
                "Download",
                on_click=DashboardState.download_all_sites_data,
                class_name="flex items-center text-gray-300 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-800",
            ),
            rx.el.div(
                rx.icon("clock", class_name="mr-2 h-4 w-4 text-gray-400"),
                rx.el.span("now-1d to now+4d", class_name="text-white"),
                class_name="flex items-center bg-gray-800 border border-gray-700 px-3 py-2 rounded-md text-sm font-medium",
            ),
            rx.el.div(
                rx.icon(
                    "search",
                    class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                ),
                rx.el.input(
                    placeholder="Search site by name or ID...",
                    on_change=DashboardState.set_search_query.debounce(300),
                    class_name="w-64 bg-gray-800 border border-gray-700 pl-9 pr-3 py-2 rounded-md text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-blue-500",
                ),
                class_name="relative",
            ),
            rx.el.div(class_name="w-px h-6 bg-gray-700"),
            rx.el.div(
                rx.el.span("demo@rebase.energy", class_name="text-gray-300 text-sm"),
                rx.icon("user", class_name="h-6 w-6 text-gray-400"),
                class_name="flex items-center space-x-2",
            ),
            class_name="flex items-center space-x-4",
        ),
        class_name="flex items-center justify-between p-4 bg-gray-900 border-b border-gray-800",
    )