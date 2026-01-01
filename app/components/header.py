import reflex as rx


def header() -> rx.Component:
    """Generic header component."""
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.icon("bar-chart-horizontal", class_name="h-5 w-5 text-gray-400"),
                rx.el.span("/", class_name="text-gray-400"),
                rx.el.span("dashboard", class_name="text-white font-medium"),
                class_name="flex items-center space-x-2",
            ),
            class_name="flex items-center space-x-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("clock", class_name="mr-2 h-4 w-4 text-gray-400"),
                rx.el.span("now-1d to now+4d", class_name="text-white"),
                class_name="flex items-center bg-gray-800 border border-gray-700 px-3 py-2 rounded-md text-sm font-medium",
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