import reflex as rx
from app.states.collections import CollectionsState


def create_collection_modal() -> rx.Component:
    """Modal for creating a new collection."""
    return rx.el.div(
        rx.cond(
            CollectionsState.show_create_collection_modal,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Create New Collection",
                            class_name="text-white font-bold text-xl mb-4",
                        ),
                        rx.el.form(
                            rx.el.div(
                                rx.el.label(
                                    "Collection Name",
                                    class_name="block text-gray-300 text-sm font-medium mb-2",
                                ),
                                rx.el.input(
                                    name="collection_name",
                                    placeholder="Enter collection name...",
                                    class_name="w-full border border-gray-700 rounded-md px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-green-500",
                                    style={"backgroundColor": "rgb(16, 16, 18)"},  # Lowest level background for inputs
                                ),
                                class_name="mb-4",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Object Type",
                                    class_name="block text-gray-300 text-sm font-medium mb-2",
                                ),
                                rx.el.select(
                                    rx.el.option("TimeSeries", value="TimeSeries"),
                                    rx.el.option("Site", value="Site"),
                                    rx.el.option("Asset", value="Asset"),
                                    name="object_type",
                                    default_value="TimeSeries",
                                    class_name="w-full border border-gray-700 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-green-500",
                                    style={"backgroundColor": "rgb(16, 16, 18)"},  # Lowest level background for inputs
                                ),
                                class_name="mb-6",
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Cancel",
                                    on_click=CollectionsState.toggle_create_collection_modal,
                                    class_name="px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-600 mr-2",
                                ),
                                rx.el.button(
                                    "Create Collection",
                                    type="submit",
                                    class_name="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700",
                                ),
                                class_name="flex justify-end",
                            ),
                            on_submit=CollectionsState.create_collection,
                            class_name="w-full",
                        ),
                        class_name="relative",
                    ),
                    class_name="rounded-lg p-6 max-w-md w-full mx-4",
                    style={"backgroundColor": "rgb(23, 23, 25)"},  # Component background
                ),
                class_name="fixed inset-0 flex items-center justify-center z-50",
                style={"backgroundColor": "rgba(16, 16, 18, 0.8)"},  # Overlay with lowest level background
                on_click=CollectionsState.toggle_create_collection_modal,
            ),
        ),
    )

