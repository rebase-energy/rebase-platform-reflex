import reflex as rx
from app.states.state import DashboardState


def add_site_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.trigger(rx.fragment()),
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            ),
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title(
                    "Add New Site", class_name="text-white font-semibold text-lg"
                ),
                rx.radix.primitives.dialog.description(
                    "Fill in the details below to add a new energy site.",
                    class_name="text-gray-400 text-sm mt-1 mb-4",
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label(
                            "Site Name", class_name="text-gray-300 text-sm font-medium"
                        ),
                        rx.el.input(
                            name="site_name",
                            placeholder="e.g., Iceloss Wind Farm",
                            class_name="w-full bg-gray-800 border border-gray-600 rounded-md px-3 py-2 text-white mt-1 focus:outline-none focus:ring-1 focus:ring-blue-500",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Site Type", class_name="text-gray-300 text-sm font-medium"
                        ),
                        rx.el.select(
                            rx.el.option("Wind", value="Wind"),
                            rx.el.option("Solar", value="Solar"),
                            rx.el.option("Load", value="Load"),
                            name="site_type",
                            class_name="w-full bg-gray-800 border border-gray-600 rounded-md px-3 py-2 text-white mt-1 focus:outline-none focus:ring-1 focus:ring-blue-500 appearance-none",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Capacity (kW)",
                            class_name="text-gray-300 text-sm font-medium",
                        ),
                        rx.el.input(
                            name="capacity",
                            type="number",
                            placeholder="e.g., 150000",
                            class_name="w-full bg-gray-800 border border-gray-600 rounded-md px-3 py-2 text-white mt-1 focus:outline-none focus:ring-1 focus:ring-blue-500",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.radix.primitives.dialog.close(
                            rx.el.button(
                                "Cancel",
                                type_="button",
                                class_name="bg-gray-700 text-white px-4 py-2 rounded-md font-medium hover:bg-gray-600",
                            )
                        ),
                        rx.el.button(
                            "Create Site",
                            type_="submit",
                            class_name="bg-blue-600 text-white px-4 py-2 rounded-md font-medium hover:bg-blue-700",
                        ),
                        class_name="flex justify-end gap-3 mt-6",
                    ),
                    on_submit=DashboardState.add_site,
                    reset_on_submit=True,
                    class_name="mt-4",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-gray-800 border border-gray-700 rounded-lg p-6 w-full max-w-md z-50 shadow-2xl",
            ),
        ),
        open=DashboardState.show_add_site_modal,
        on_open_change=DashboardState.set_show_add_site_modal,
    )