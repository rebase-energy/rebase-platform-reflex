import reflex as rx
from app.states.workspace import WorkspaceState


def settings_sidebar() -> rx.Component:
    """Settings page sidebar with navigation items."""
    settings_items = [
        ("General", "settings"),
        ("Appearance", "palette"),
        ("Entities", "database"),
        ("Collections", "list"),
    ]
    
    return rx.el.aside(
        rx.el.div(
            # Header with back arrow and Settings title
            rx.el.div(
                rx.el.button(
                    rx.icon("chevron-left", class_name="h-5 w-5 text-white"),
                    on_click=rx.redirect("/"),
                    class_name="p-2 hover:bg-gray-800/50 rounded-md transition-colors",
                ),
                rx.el.span(
                    "Settings",
                    class_name="text-white text-sm font-medium",
                ),
                class_name="flex items-center gap-4 mb-6",
            ),
            # Search settings
            rx.el.div(
                rx.icon("search", class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400"),
                rx.el.input(
                    placeholder="Search settings...",
                    class_name="w-full border border-gray-700/50 pl-9 pr-3 py-2 rounded-md text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500",
                    style={"backgroundColor": "rgb(23, 23, 25)"},
                ),
                class_name="relative mb-4",
            ),
            # Settings navigation items
            rx.el.div(
                rx.foreach(
                    settings_items,
                    lambda item: rx.el.button(
                        rx.el.div(
                            rx.icon(item[1], class_name="h-4 w-4 text-gray-400 mr-2"),
                            rx.el.span(
                                item[0],
                                class_name="text-gray-300 text-sm",
                            ),
                            class_name="flex items-center",
                        ),
                        on_click=WorkspaceState.select_settings_section(item[0]),
                                class_name=rx.cond(
                                    WorkspaceState.selected_settings_section == item[0],
                            "w-full flex items-center px-3 py-2 bg-gray-800/50 hover:bg-gray-800/70 rounded-md text-left mb-1",
                            "w-full flex items-center px-3 py-2 hover:bg-gray-800/30 rounded-md text-left mb-1",
                        ),
                    ),
                ),
                class_name="space-y-0.5",
            ),
            class_name="p-4",
        ),
        class_name="w-64 h-screen border-r border-gray-800 flex flex-col",
        style={"backgroundColor": "rgb(16, 16, 18)"},
    )

