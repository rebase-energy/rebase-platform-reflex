import reflex as rx
from typing import Any, Callable, TypedDict


class TableColumn(TypedDict):
    """Table column configuration."""
    key: str
    label: str
    width: int
    render: Callable[[Any], rx.Component] | None  # Optional custom renderer


# =============================================================================
# REUSABLE CELL RENDERERS - Use these in your column definitions
# =============================================================================

def text_cell(key: str, bold: bool = False, mono: bool = False, color: str = "gray-300"):
    """
    Create a text cell renderer.
    
    Args:
        key: The data key to display
        bold: Whether to use semibold font
        mono: Whether to use monospace font
        color: Tailwind color class (e.g., "white", "gray-300", "green-400")
    """
    font_weight = "font-semibold" if bold else ""
    font_family = "font-mono" if mono else ""
    
    def renderer(item):
        return rx.el.span(
            item[key],
            class_name=f"text-{color} text-sm {font_weight} {font_family}".strip(),
            style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
        )
    return renderer


def badge_cell(key: str, bg_color: str = "gray-800", text_color: str = "gray-400"):
    """
    Create a badge/tag cell renderer.
    
    Args:
        key: The data key to display
        bg_color: Tailwind background color (e.g., "gray-800")
        text_color: Tailwind text color (e.g., "gray-400")
    """
    def renderer(item):
        return rx.el.span(
            item[key],
            class_name=f"text-{text_color} text-xs font-mono bg-{bg_color} px-2 py-1 rounded",
        )
    return renderer


def status_cell(key: str, active_value: str = "Active"):
    """
    Create a status badge cell renderer with conditional coloring.
    
    Args:
        key: The data key to display
        active_value: The value that indicates "active" status (shows green)
    """
    def renderer(item):
        return rx.el.span(
            item[key],
            class_name=rx.cond(
                item[key] == active_value,
                "px-2 py-1 rounded text-xs font-medium bg-green-500/20 text-green-400",
                "px-2 py-1 rounded text-xs font-medium bg-yellow-500/20 text-yellow-400",
            ),
        )
    return renderer


def value_cell(key: str, color: str = "green-400"):
    """
    Create a numeric value cell renderer with monospace font.
    
    Args:
        key: The data key to display
        color: Tailwind text color for the value
    """
    def renderer(item):
        return rx.el.span(
            item[key],
            class_name=f"text-{color} text-sm font-mono font-semibold",
            style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
        )
    return renderer


def data_table(
    items: list[Any],
    columns: list[TableColumn],
    on_column_width_change: Callable[[str], None],
    on_add_item: Callable[[], None] | None = None,
    resize_input_id: str = "column-resize-input",
    resize_handle_class: str = "resize-handle",
) -> rx.Component:
    """
    Reusable data table with resizable columns.
    
    Args:
        items: List of items to display in the table
        columns: List of column configurations with keys, labels, and widths
        on_column_width_change: Handler for column width changes
        on_add_item: Optional handler for the "+" button in the first column header
        resize_input_id: ID for the hidden input that receives resize events
        resize_handle_class: CSS class for resize handles
    
    Returns:
        Complete data table with resizable columns
    """
    
    # Calculate cumulative widths for resize handle positioning
    def get_cumulative_width(up_to_index: int) -> int:
        return sum(col["width"] for col in columns[:up_to_index + 1])
    
    return rx.el.div(
        # Hidden input for column resize updates
        rx.el.input(
            type="hidden",
            id=resize_input_id,
            on_change=on_column_width_change,
        ),
        # Table container with column resize JavaScript and table structure
        rx.el.div(
            # JavaScript for column resizing
            rx.el.script(
                f"""
                window.initColumnResize{resize_input_id.replace('-', '_')} = function() {{
                    document.querySelectorAll('.{resize_handle_class}').forEach(function(handle) {{
                        const newHandle = handle.cloneNode(true);
                        handle.parentNode.replaceChild(newHandle, handle);
                        
                        newHandle.addEventListener('mousedown', function(e) {{
                            e.preventDefault();
                            e.stopPropagation();
                            
                            const columnKey = newHandle.getAttribute('data-column-key');
                            const tableContainer = newHandle.closest('[data-table-container]');
                            if (!tableContainer) return;
                            
                            const headerCells = tableContainer.querySelectorAll('[data-column-header="' + columnKey + '"]');
                            const dataCells = tableContainer.querySelectorAll('[data-column="' + columnKey + '"]');
                            
                            if (headerCells.length === 0) return;
                            
                            const firstHeaderCell = headerCells[0];
                            const startX = e.clientX;
                            const startWidth = parseInt(window.getComputedStyle(firstHeaderCell).width, 10);
                            
                            const handleRect = newHandle.getBoundingClientRect();
                            const containerRect = tableContainer.getBoundingClientRect();
                            const startHandleLeft = handleRect.left - containerRect.left;
                            
                            function onMouseMove(e) {{
                                const diff = e.clientX - startX;
                                const newWidth = Math.max(50, startWidth + diff);
                                
                                headerCells.forEach(function(cell) {{
                                    cell.style.width = newWidth + 'px';
                                    cell.style.minWidth = newWidth + 'px';
                                    cell.style.maxWidth = newWidth + 'px';
                                }});
                                
                                dataCells.forEach(function(cell) {{
                                    cell.style.width = newWidth + 'px';
                                    cell.style.minWidth = newWidth + 'px';
                                    cell.style.maxWidth = newWidth + 'px';
                                }});
                                
                                const newHandleLeft = startHandleLeft + diff;
                                newHandle.style.left = (newHandleLeft - 2) + 'px';
                                
                                const allHandles = Array.from(tableContainer.querySelectorAll('.{resize_handle_class}'));
                                const currentIndex = allHandles.indexOf(newHandle);
                                const allHeaders = Array.from(tableContainer.querySelectorAll('[data-column-header]'));
                                
                                let cumulativeWidth = 0;
                                allHeaders.forEach(function(headerCell) {{
                                    const key = headerCell.getAttribute('data-column-header');
                                    let width = (key === columnKey) ? newWidth : parseInt(window.getComputedStyle(headerCell).width, 10);
                                    cumulativeWidth += width;
                                    
                                    const handleForColumn = allHandles.find(function(h) {{
                                        return h.getAttribute('data-column-key') === key;
                                    }});
                                    
                                    if (handleForColumn && allHandles.indexOf(handleForColumn) > currentIndex) {{
                                        handleForColumn.style.left = (cumulativeWidth - 2) + 'px';
                                    }}
                                }});
                            }}
                            
                            function onMouseUp(e) {{
                                const diff = e.clientX - startX;
                                const newWidth = Math.max(50, startWidth + diff);
                                
                                const input = document.getElementById('{resize_input_id}');
                                if (input) {{
                                    input.value = columnKey + ':' + newWidth;
                                    const event = new Event('change', {{ bubbles: true }});
                                    input.dispatchEvent(event);
                                }}
                                
                                document.removeEventListener('mousemove', onMouseMove);
                                document.removeEventListener('mouseup', onMouseUp);
                                document.body.style.cursor = '';
                                document.body.style.userSelect = '';
                            }}
                            
                            document.body.style.cursor = 'col-resize';
                            document.body.style.userSelect = 'none';
                            document.addEventListener('mousemove', onMouseMove);
                            document.addEventListener('mouseup', onMouseUp);
                        }});
                    }});
                }};
                
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', function() {{
                        setTimeout(window.initColumnResize{resize_input_id.replace('-', '_')}, 100);
                    }});
                }} else {{
                    setTimeout(window.initColumnResize{resize_input_id.replace('-', '_')}, 100);
                }}
                
                const observer = new MutationObserver(function() {{
                    setTimeout(window.initColumnResize{resize_input_id.replace('-', '_')}, 150);
                }});
                observer.observe(document.body, {{ childList: true, subtree: true }});
                """
            ),
            # Table header row
            rx.el.div(
                # Render column headers
                *[
                    rx.el.div(
                        rx.cond(
                            (i == 0) and (on_add_item is not None),
                            # First column with optional "+" button
                            rx.el.div(
                                rx.el.span(col["label"], class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                                rx.el.button(
                                    rx.icon("plus", class_name="h-3.5 w-3.5 text-gray-400 hover:text-white"),
                                    on_click=on_add_item,
                                    class_name="ml-auto opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-700/50 rounded",
                                ),
                                class_name="flex items-center justify-between",
                            ),
                            # Regular column header
                            rx.el.span(col["label"], class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                        ),
                        class_name=f"px-4 py-3 {'border-r border-gray-700 ' if i < len(columns) - 1 else ''}flex-shrink-0 group" if i == 0 else f"px-4 py-3 {'border-r border-gray-700 ' if i < len(columns) - 1 else ''}flex-shrink-0",
                        data_column_header=col["key"],
                        style={
                            "backgroundColor": "rgb(23, 23, 25)",
                            "width": f"{col['width']}px",
                            "minWidth": f"{col['width']}px",
                            "maxWidth": f"{col['width']}px",
                        },
                    )
                    for i, col in enumerate(columns)
                ],
                class_name="flex border-b border-gray-700 group relative",
                style={"backgroundColor": "rgb(23, 23, 25)"},
            ),
            # Resize handles
            rx.el.div(
                *[
                    rx.el.div(
                        class_name=f"{resize_handle_class} absolute top-0 bottom-0 cursor-col-resize hover:bg-green-500 transition-colors",
                        style={
                            "left": f"{get_cumulative_width(i) - 2}px",
                            "width": "4px",
                            "zIndex": 50,
                            "pointerEvents": "auto",
                            "backgroundColor": "rgba(34, 197, 94, 0.1)",
                        },
                        data_column_key=col["key"],
                    )
                    for i, col in enumerate(columns[:-1])  # No resize handle for last column
                ],
                class_name="absolute inset-0",
                style={"zIndex": 50, "pointerEvents": "none"},
            ),
            # Table rows
            rx.el.div(
                rx.foreach(
                    items,
                    lambda item: rx.el.div(
                        *[
                            rx.el.div(
                                # Use custom renderer if provided, otherwise render item[key]
                                col.get("render", lambda x: rx.el.span(
                                    x.get(col["key"], ""),
                                    class_name="text-white text-sm" if i == 0 else "text-gray-300 text-sm",
                                    style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
                                ))(item),
                                class_name=f"px-4 py-3 {'border-r border-gray-700 ' if i < len(columns) - 1 else ''}flex-shrink-0 flex items-center",
                                data_column=col["key"],
                                style={
                                    "backgroundColor": "rgb(23, 23, 25)",
                                    "width": f"{col['width']}px",
                                    "minWidth": f"{col['width']}px",
                                    "maxWidth": f"{col['width']}px",
                                    "overflow": "hidden",
                                },
                            )
                            for i, col in enumerate(columns)
                        ],
                        class_name="flex border-b border-gray-700/50 hover:opacity-90 transition-opacity",
                        style={"backgroundColor": "rgb(23, 23, 25)"},
                    ),
                ),
            ),
            class_name="border border-gray-700 rounded-lg overflow-hidden relative",
            style={"backgroundColor": "rgb(23, 23, 25)"},
            data_table_container="true",
        ),
        class_name="w-full",
    )


# Legacy simple table view components (kept for backwards compatibility)
def table_view(
    items: list[Any],
    render_item: Callable[[Any], rx.Component],
    empty_message: str = "No items to display",
    class_name: str = "",
) -> rx.Component:
    """
    A simple reusable table view primitive component.
    
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
    A simple reusable table row component.
    
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
