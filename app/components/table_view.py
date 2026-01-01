import reflex as rx
from typing import Callable, Any


def table_view(
    items: list[Any],
    render_item: Callable[[Any], rx.Component],
    empty_message: str = "No items to display",
    class_name: str = "",
) -> rx.Component:
    """
    A reusable table view primitive component.
    
    Args:
        items: List of items to display (can be a reactive var from rx.var)
        render_item: Function that takes an item and returns a Component to render it
        empty_message: Message to show when the list is empty
        class_name: Additional CSS classes to apply to the container
    """
    return rx.el.div(
        rx.el.div(
            rx.foreach(items, render_item),
            class_name="divide-y divide-gray-700",
        ),
        class_name=f"bg-gray-800/50 rounded-lg border border-gray-700 {class_name}",
    )


def table_row(
    content: rx.Component,
    on_click: Callable | None = None,
    is_selected: bool = False,
    class_name: str = "",
) -> rx.Component:
    """
    A reusable table row component.
    
    Args:
        content: The content to display in the table row
        on_click: Optional click handler
        is_selected: Whether this row is selected
        class_name: Additional CSS classes
    """
    base_classes = "px-4 py-3 border-b border-gray-700 last:border-b-0 transition-colors"
    selected_classes = "bg-gray-700 hover:bg-gray-600 cursor-pointer"
    unselected_classes = "bg-gray-800/30 hover:bg-gray-800/50 cursor-pointer"
    
    return rx.el.div(
        content,
        on_click=on_click,
        class_name=rx.cond(
            is_selected,
            f"{base_classes} {selected_classes} {class_name}",
            f"{base_classes} {unselected_classes} {class_name}",
        ),
    )

