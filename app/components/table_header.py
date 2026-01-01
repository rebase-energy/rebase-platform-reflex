import reflex as rx
from app.states.collections import CollectionsState


def table_header() -> rx.Component:
    """Header component with search, sort, and filter buttons (Attio style) for table view."""
    return rx.el.div(
        rx.el.div(
            # Free-form search input
            rx.el.div(
                rx.icon(
                    "search",
                    class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                ),
                rx.el.input(
                    placeholder="Search...",
                    value=CollectionsState.collection_search_query,
                    on_change=CollectionsState.set_collection_search_query,
                    class_name="w-64 bg-gray-800/50 border border-gray-700 pl-9 pr-3 py-2 rounded-md text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500",
                ),
                class_name="relative",
            ),
            # Separator
            rx.el.div(class_name="w-px h-6 bg-gray-700"),
            # Sort button (Attio style)
            rx.el.button(
                rx.el.div(
                    rx.icon(
                        "arrow-up-down",
                        class_name="h-4 w-4 text-gray-400",
                    ),
                    rx.el.span("Sort", class_name="text-gray-300 text-sm font-medium ml-2"),
                    class_name="flex items-center",
                ),
                on_click=CollectionsState.toggle_sort_modal,
                class_name="flex items-center px-3 py-2 rounded-md border border-dashed border-gray-600 hover:border-gray-500 hover:bg-gray-800/50 transition-colors",
            ),
            # Filter button (Attio style)
            rx.el.button(
                rx.el.div(
                    rx.icon(
                        "filter",
                        class_name="h-4 w-4 text-gray-400",
                    ),
                    rx.el.span("Filter", class_name="text-gray-300 text-sm font-medium ml-2"),
                    class_name="flex items-center",
                ),
                on_click=CollectionsState.toggle_filter_modal,
                class_name="flex items-center px-3 py-2 rounded-md border border-dashed border-gray-600 hover:border-gray-500 hover:bg-gray-800/50 transition-colors",
            ),
            class_name="flex items-center space-x-3",
        ),
        class_name="mb-4",
    )

