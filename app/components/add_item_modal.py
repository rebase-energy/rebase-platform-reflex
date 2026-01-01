import reflex as rx
from app.states.collections import CollectionsState
from app.states.entities import EntitiesState


def add_item_modal() -> rx.Component:
    """Modal for adding TimeSeries items."""
    return rx.cond(
        CollectionsState.show_add_item_modal,
        rx.el.div(
            # Overlay
            rx.el.div(
                on_click=CollectionsState.toggle_add_item_modal,
                class_name="fixed inset-0 z-40",
                style={"backgroundColor": "rgba(16, 16, 18, 0.8)"},
            ),
            # Modal content
            rx.el.div(
                # Header with title and close button
                rx.el.div(
                    rx.el.div(
                        rx.icon("zap", class_name="h-5 w-5 text-gray-400 mr-2"),
                        rx.el.h2(
                            "Create TimeSeries",
                            class_name="text-white font-semibold text-lg",
                        ),
                        class_name="flex items-center",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-5 w-5 text-gray-400 hover:text-white"),
                        on_click=CollectionsState.toggle_add_item_modal,
                        class_name="hover:bg-gray-800 rounded-md p-1 transition-colors",
                    ),
                    class_name="flex items-center justify-between mb-6",
                ),
                # Tabs
                rx.el.div(
                    rx.el.button(
                        "All",
                        class_name="px-3 py-1.5 text-sm font-medium text-white border-b-2 border-green-500",
                    ),
                    rx.el.button(
                        "Create templates",
                        class_name="px-3 py-1.5 text-sm font-medium text-gray-400 hover:text-white border-b-2 border-transparent",
                    ),
                    class_name="flex space-x-1 mb-6 border-b border-gray-700",
                ),
                # Form
                rx.el.form(
                    # Name field
                    rx.el.div(
                        rx.el.label(
                            "Name",
                            class_name="block text-gray-400 text-xs font-medium mb-1.5 uppercase tracking-wide",
                        ),
                        rx.el.input(
                            name="name",
                            placeholder="Set Name...",
                            class_name="w-full border border-gray-700 rounded-md px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500",
                            style={"backgroundColor": "rgb(23, 23, 25)"},
                        ),
                        class_name="mb-4",
                    ),
                    # Description field
                    rx.el.div(
                        rx.el.label(
                            "Description",
                            class_name="block text-gray-400 text-xs font-medium mb-1.5 uppercase tracking-wide",
                        ),
                        rx.el.textarea(
                            name="description",
                            placeholder="Set Description...",
                            rows=3,
                            class_name="w-full border border-gray-700 rounded-md px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500 resize-none",
                            style={"backgroundColor": "rgb(23, 23, 25)"},
                        ),
                        class_name="mb-4",
                    ),
                    # Unit field
                    rx.el.div(
                        rx.el.label(
                            "Unit",
                            class_name="block text-gray-400 text-xs font-medium mb-1.5 uppercase tracking-wide",
                        ),
                        rx.el.input(
                            name="unit",
                            placeholder="Set Unit...",
                            default_value="kW",
                            class_name="w-full border border-gray-700 rounded-md px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500",
                            style={"backgroundColor": "rgb(23, 23, 25)"},
                        ),
                        class_name="mb-6",
                    ),
                    # Footer with "Create more" toggle and "Create record" button
                    rx.el.div(
                        rx.el.label(
                            rx.el.input(
                                type="checkbox",
                                name="create_more",
                                class_name="w-4 h-4 text-green-600 bg-gray-700 border-gray-600 rounded focus:ring-green-500 focus:ring-2",
                            ),
                            rx.el.span(
                                "Create more",
                                class_name="ml-2 text-sm text-gray-300",
                            ),
                            class_name="flex items-center cursor-pointer",
                        ),
                        rx.el.button(
                            rx.el.span("Create record"),
                            rx.el.span(
                                "⌘⏎",
                                class_name="ml-2 text-xs text-gray-400",
                            ),
                            type="submit",
                            class_name="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center font-medium",
                        ),
                        class_name="flex items-center justify-between",
                    ),
                    on_submit=EntitiesState.create_time_series_entity,
                    class_name="w-full",
                ),
                class_name="relative bg-gray-800 rounded-lg p-6 max-w-lg w-full mx-4 shadow-xl z-50",
                style={"backgroundColor": "rgb(23, 23, 25)"},
            ),
            class_name="fixed inset-0 flex items-center justify-center z-50",
        ),
    )

