import reflex as rx
from app.states.collections import CollectionsState
from app.states.entities import EntitiesState


def entity_badge(entity_type: rx.Var[str] | str) -> rx.Component:
    """
    Render an entity type as a styled badge with mono font.
    Used consistently throughout the app to indicate entity objects.
    """
    return rx.el.span(
        entity_type,
        class_name="px-2 py-0.5 rounded text-xs font-mono bg-gray-700/50 text-gray-300",
    )


def _form_field(name: str, label: str, placeholder: str, field_type: str = "input", default_value: str = "") -> rx.Component:
    """Reusable form field component."""
    input_class = "w-full border border-gray-700 rounded-md px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-green-500"
    input_style = {"backgroundColor": "rgb(16, 16, 18)"}
    
    if field_type == "textarea":
        return rx.el.div(
            rx.el.label(label, class_name="block text-gray-300 text-sm font-medium mb-2"),
            rx.el.textarea(
                name=name,
                placeholder=placeholder,
                rows=3,
                class_name=f"{input_class} resize-none",
                style=input_style,
            ),
            class_name="mb-4",
        )
    elif field_type == "select":
        return rx.el.div(
            rx.el.label(label, class_name="block text-gray-300 text-sm font-medium mb-2"),
            rx.el.select(
                rx.el.option("Wind", value="Wind"),
                rx.el.option("Solar", value="Solar"),
                rx.el.option("Hydro", value="Hydro"),
                rx.el.option("Load", value="Load"),
                name=name,
                class_name=input_class,
                style=input_style,
            ),
            class_name="mb-4",
        )
    else:
        return rx.el.div(
            rx.el.label(label, class_name="block text-gray-300 text-sm font-medium mb-2"),
            rx.el.input(
                name=name,
                placeholder=placeholder,
                default_value=default_value,
                class_name=input_class,
                style=input_style,
            ),
            class_name="mb-4",
        )


def _timeseries_fields() -> rx.Component:
    """Form fields specific to TimeSeries entities."""
    return rx.fragment(
        _form_field("unit", "Unit", "Enter unit...", default_value="kW"),
    )


def _site_fields() -> rx.Component:
    """Form fields specific to Site entities."""
    return rx.fragment(
        _form_field("site_type", "Site Type", "", field_type="select"),
        _form_field("capacity", "Capacity (kW)", "Enter capacity..."),
        _form_field("location", "Location", "Enter location..."),
    )


def _asset_fields() -> rx.Component:
    """Form fields specific to Asset entities."""
    return rx.fragment(
        _form_field("asset_type", "Asset Type", "e.g., Turbine, Panel, Transformer..."),
        _form_field("site_name", "Site", "Enter site name..."),
    )


def create_entity_modal() -> rx.Component:
    """Modal for creating a new entity (TimeSeries, Site, Asset)."""
    return rx.cond(
        CollectionsState.show_add_item_modal,
        rx.el.div(
            # Modal content
            rx.el.div(
                rx.el.div(
                    # Header with title and close button
                    rx.el.div(
                        rx.el.div(
                            rx.icon("plus", class_name="h-5 w-5 text-gray-400 mr-2"),
                            rx.el.span(
                                "Create ",
                                class_name="text-white font-semibold text-lg",
                            ),
                            entity_badge(EntitiesState.active_object_type),
                            class_name="flex items-center gap-1",
                        ),
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5 text-gray-400 hover:text-white"),
                            on_click=CollectionsState.toggle_add_item_modal,
                            type="button",
                            class_name="hover:bg-gray-800 rounded-md p-1 transition-colors",
                        ),
                        class_name="flex items-center justify-between mb-6",
                    ),
                    # Form
                    rx.el.form(
                        # Common fields: Name and Description
                        _form_field("name", "Name", "Enter name..."),
                        _form_field("description", "Description", "Enter description...", field_type="textarea"),
                        
                        # Entity-specific fields
                        rx.cond(
                            EntitiesState.active_object_type == "TimeSeries",
                            _timeseries_fields(),
                            rx.cond(
                                EntitiesState.active_object_type == "Sites",
                                _site_fields(),
                                rx.cond(
                                    EntitiesState.active_object_type == "Assets",
                                    _asset_fields(),
                                    rx.fragment(),  # No extra fields for unknown types
                                ),
                            ),
                        ),
                        
                        # Footer buttons
                        rx.el.div(
                            rx.el.button(
                                "Cancel",
                                on_click=CollectionsState.toggle_add_item_modal,
                                type="button",
                                class_name="px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-600 mr-2",
                            ),
                            rx.el.button(
                                "Create",
                                type="submit",
                                class_name="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700",
                            ),
                            class_name="flex justify-end mt-6",
                        ),
                        on_submit=EntitiesState.create_entity,
                        class_name="w-full",
                    ),
                    class_name="relative",
                ),
                class_name="rounded-lg p-6 max-w-md w-full mx-4",
                style={"backgroundColor": "rgb(23, 23, 25)"},
                on_click=rx.stop_propagation,
            ),
            class_name="fixed inset-0 flex items-center justify-center z-50",
            style={"backgroundColor": "rgba(16, 16, 18, 0.8)"},
            on_click=CollectionsState.toggle_add_item_modal,
        ),
    )

