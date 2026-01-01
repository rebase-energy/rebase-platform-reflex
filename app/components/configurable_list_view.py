import reflex as rx
import random
from app.states.lists import ListsState, ListConfig, TimeSeries, ListAttribute
from app.components.list_header import list_header
from app.components.emoji_picker import emoji_picker
from app.components.timeseries_card import timeseries_card, TimeSeriesCardData, TimeSeriesDataPoint
from datetime import datetime, timedelta


def render_attribute_value(item: TimeSeries, attribute: ListAttribute, attr_key: str, attr_type: str) -> rx.Component:
    """Render a single attribute value based on its type."""
    # Use rx.cond for reactive rendering based on attribute type
    return rx.cond(
        attr_type == "text",
        rx.el.span(
            item[attr_key],
            class_name="text-gray-300 text-sm",
        ),
        rx.cond(
            attr_type == "number",
            rx.el.span(
                item[attr_key],
                class_name="text-gray-300 text-sm font-mono",
            ),
            rx.cond(
                attr_type == "date",
                rx.el.span(
                    item[attr_key],
                    class_name="text-gray-300 text-sm",
                ),
                rx.cond(
                    attr_type == "status",
                    rx.el.span(
                        item[attr_key],
                        class_name=rx.cond(
                            item[attr_key] == "actual",
                            "px-2 py-1 rounded text-xs font-medium bg-green-500/20 text-green-400",
                            rx.cond(
                                item[attr_key] == "forecast",
                                "px-2 py-1 rounded text-xs font-medium bg-green-500/20 text-green-400",
                                "px-2 py-1 rounded text-xs font-medium bg-yellow-500/20 text-yellow-400",
                            ),
                        ),
                    ),
                    rx.el.span(
                        item[attr_key],
                        class_name="text-gray-300 text-sm",
                    ),
                ),
            ),
        ),
    )


def generate_timeseries_card_data(name: str, capacity_mw: float) -> TimeSeriesCardData:
    """Generate sample time series card data for a location."""
    data_points: list[TimeSeriesDataPoint] = []
    now = datetime.now()
    start_time = now - timedelta(days=1)
    end_time = now + timedelta(days=4)
    current_time = start_time
    
    while current_time <= end_time:
        # Generate realistic wind power data
        hour = current_time.hour
        base_generation = capacity_mw * 0.6
        variation = capacity_mw * 0.3 * (0.5 + (hour % 12) / 12)
        actual = base_generation + variation + (capacity_mw * 0.1 * random.uniform(-1, 1))
        forecast = actual * (1 + random.uniform(-0.1, 0.1))
        
        data_points.append({
            "time": current_time.strftime("%a %d/%m %H:%M"),
            "capacity": capacity_mw,
            "actual": max(0, min(capacity_mw, actual)),
            "forecast": max(0, min(capacity_mw, forecast)),
            "iceaware": None,
            "iceblind": None,
            "iceloss": None,
        })
        current_time += timedelta(hours=1)
    
    return {
        "id": name.lower().replace(" ", "-"),
        "name": name,
        "capacity_mw": capacity_mw,
        "data": data_points,
        "view_tabs": ["Default view", "Iceloss", "Iceloss pct", "Iceloss weather"],
    }


def timeseries_card_grid_view(items: list[TimeSeriesCardData]) -> rx.Component:
    """Grid view showing time series cards in a 1 or 2 column layout."""
    from app.states.lists import ListsState
    return rx.el.div(
        rx.foreach(
            items,
            lambda card: timeseries_card(card),
        ),
        class_name=rx.cond(
            ListsState.timeseries_card_columns == 1,
            "grid grid-cols-1 gap-6",
            "grid grid-cols-2 gap-6",
        ),
    )


def object_list_view(object_type: str, items: list[TimeSeries]) -> rx.Component:
    """List view for displaying all items of a specific object type."""
    return rx.el.div(
        # Object header with name
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    object_type,
                    class_name="text-white font-bold text-xl",
                ),
                rx.el.span(
                    f"All {object_type} items",
                    class_name="text-gray-400 text-sm ml-2",
                ),
                class_name="flex items-center",
            ),
            class_name="mb-6",
        ),
        # Search, Sort, Filter header
        list_header(),
        # Hidden input for column resize updates
        rx.el.input(
            type="hidden",
            id="column-resize-input-object",
            on_change=ListsState.set_column_width,
        ),
        # Table view with configurable columns - Attio style
        rx.el.div(
            # JavaScript for column resizing
            rx.el.script(
                """
                window.initColumnResizeObject = function() {
                    document.querySelectorAll('.resize-handle-object').forEach(function(handle) {
                        const newHandle = handle.cloneNode(true);
                        handle.parentNode.replaceChild(newHandle, handle);
                        
                        newHandle.addEventListener('mousedown', function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            
                            const columnKey = newHandle.getAttribute('data-column-key');
                            const tableContainer = newHandle.closest('[data-table-container]');
                            if (!tableContainer) {
                                console.error('Table container not found');
                                return;
                            }
                            
                            const headerCells = tableContainer.querySelectorAll('[data-column-header="' + columnKey + '"]');
                            const dataCells = tableContainer.querySelectorAll('[data-column="' + columnKey + '"]');
                            
                            if (headerCells.length === 0) {
                                console.error('Header cells not found for', columnKey);
                                return;
                            }
                            
                            const firstHeaderCell = headerCells[0];
                            const startX = e.clientX;
                            const startWidth = parseInt(window.getComputedStyle(firstHeaderCell).width, 10);
                            
                            const handleRect = newHandle.getBoundingClientRect();
                            const containerRect = tableContainer.getBoundingClientRect();
                            const startHandleLeft = handleRect.left - containerRect.left;
                            
                            function onMouseMove(e) {
                                const diff = e.clientX - startX;
                                const newWidth = Math.max(50, startWidth + diff);
                                
                                headerCells.forEach(function(cell) {
                                    cell.style.width = newWidth + 'px';
                                    cell.style.minWidth = newWidth + 'px';
                                    cell.style.maxWidth = newWidth + 'px';
                                });
                                
                                dataCells.forEach(function(cell) {
                                    cell.style.width = newWidth + 'px';
                                    cell.style.minWidth = newWidth + 'px';
                                    cell.style.maxWidth = newWidth + 'px';
                                });
                                
                                const newHandleLeft = startHandleLeft + diff;
                                newHandle.style.left = (newHandleLeft - 2) + 'px';
                                
                                const allHandles = Array.from(tableContainer.querySelectorAll('.resize-handle-object'));
                                const currentIndex = allHandles.indexOf(newHandle);
                                const allHeaders = Array.from(tableContainer.querySelectorAll('[data-column-header]'));
                                
                                let cumulativeWidth = 0;
                                allHeaders.forEach(function(headerCell) {
                                    const key = headerCell.getAttribute('data-column-header');
                                    let width;
                                    
                                    if (key === columnKey) {
                                        width = newWidth;
                                    } else {
                                        width = parseInt(window.getComputedStyle(headerCell).width, 10);
                                    }
                                    
                                    cumulativeWidth += width;
                                    
                                    const handleForColumn = allHandles.find(function(h) {
                                        return h.getAttribute('data-column-key') === key;
                                    });
                                    
                                    if (handleForColumn && allHandles.indexOf(handleForColumn) > currentIndex) {
                                        handleForColumn.style.left = (cumulativeWidth - 2) + 'px';
                                    }
                                });
                            }
                            
                            function onMouseUp(e) {
                                const diff = e.clientX - startX;
                                const newWidth = Math.max(50, startWidth + diff);
                                
                                const input = document.getElementById('column-resize-input-object');
                                if (input) {
                                    input.value = columnKey + ':' + newWidth;
                                    const event = new Event('change', { bubbles: true });
                                    input.dispatchEvent(event);
                                }
                                
                                document.removeEventListener('mousemove', onMouseMove);
                                document.removeEventListener('mouseup', onMouseUp);
                                document.body.style.cursor = '';
                                document.body.style.userSelect = '';
                            }
                            
                            document.body.style.cursor = 'col-resize';
                            document.body.style.userSelect = 'none';
                            document.addEventListener('mousemove', onMouseMove);
                            document.addEventListener('mouseup', onMouseUp);
                        });
                    });
                };
                
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', function() {
                        setTimeout(window.initColumnResizeObject, 100);
                    });
                } else {
                    setTimeout(window.initColumnResizeObject, 100);
                }
                
                const observer = new MutationObserver(function() {
                    setTimeout(window.initColumnResizeObject, 150);
                });
                observer.observe(document.body, { childList: true, subtree: true });
                """
            ),
            # Table header row
            rx.el.div(
                # First column with "+" button in top-right
                rx.el.div(
                    rx.el.div(
                        rx.el.span("Name", class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                        rx.el.button(
                            rx.icon("plus", class_name="h-3.5 w-3.5 text-gray-400 hover:text-white"),
                            on_click=ListsState.toggle_add_item_modal,
                            class_name="ml-auto opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-700/50 rounded",
                        ),
                        class_name="flex items-center justify-between",
                    ),
                    class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 group",
                    data_column_header="name",
                    style={
                        "backgroundColor": "rgb(23, 23, 25)",
                        "width": f"{ListsState.column_width_name}px",
                        "minWidth": f"{ListsState.column_width_name}px",
                        "maxWidth": f"{ListsState.column_width_name}px",
                    },
                ),
                # Description column
                rx.el.div(
                    rx.el.span("Description", class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                    class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 relative",
                    data_column_header="description",
                    style={
                        "backgroundColor": "rgb(23, 23, 25)",
                        "width": f"{ListsState.column_width_description}px",
                        "minWidth": f"{ListsState.column_width_description}px",
                        "maxWidth": f"{ListsState.column_width_description}px",
                    },
                ),
                # Unit column
                rx.el.div(
                    rx.el.span("Unit", class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                    class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 relative",
                    data_column_header="unit",
                    style={
                        "backgroundColor": "rgb(23, 23, 25)",
                        "width": f"{ListsState.column_width_unit}px",
                        "minWidth": f"{ListsState.column_width_unit}px",
                        "maxWidth": f"{ListsState.column_width_unit}px",
                    },
                ),
                # Site column
                rx.el.div(
                    rx.el.span("Site", class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                    class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 relative",
                    data_column_header="site_name",
                    style={
                        "backgroundColor": "rgb(23, 23, 25)",
                        "width": f"{ListsState.column_width_site_name}px",
                        "minWidth": f"{ListsState.column_width_site_name}px",
                        "maxWidth": f"{ListsState.column_width_site_name}px",
                    },
                ),
                # Value column
                rx.el.div(
                    rx.el.span("Value", class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                    class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 relative",
                    data_column_header="value",
                    style={
                        "backgroundColor": "rgb(23, 23, 25)",
                        "width": f"{ListsState.column_width_value}px",
                        "minWidth": f"{ListsState.column_width_value}px",
                        "maxWidth": f"{ListsState.column_width_value}px",
                    },
                ),
                # Type column (last, no resize handle)
                rx.el.div(
                    rx.el.span("Type", class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                    class_name="px-4 py-3 flex-shrink-0",
                    style={
                        "backgroundColor": "rgb(23, 23, 25)",
                        "width": f"{ListsState.column_width_type}px",
                        "minWidth": f"{ListsState.column_width_type}px",
                        "maxWidth": f"{ListsState.column_width_type}px",
                    },
                ),
                class_name="flex border-b border-gray-700 group relative",
                style={"backgroundColor": "rgb(23, 23, 25)"},
            ),
            # Resize handles positioned absolutely to span full table height
            rx.el.div(
                # Resize handle for Name column
                rx.el.div(
                    class_name="resize-handle-object absolute top-0 bottom-0 cursor-col-resize hover:bg-green-500 transition-colors",
                    style={
                        "left": f"{ListsState.column_width_name - 2}px",
                        "width": "4px",
                        "zIndex": 50,
                        "pointerEvents": "auto",
                        "backgroundColor": "rgba(34, 197, 94, 0.1)",
                    },
                    data_column_key="name",
                ),
                # Resize handle for Description column
                rx.el.div(
                    class_name="resize-handle-object absolute top-0 bottom-0 cursor-col-resize hover:bg-green-500 transition-colors",
                    style={
                        "left": f"{ListsState.column_width_name + ListsState.column_width_description - 2}px",
                        "width": "4px",
                        "zIndex": 50,
                        "pointerEvents": "auto",
                        "backgroundColor": "rgba(34, 197, 94, 0.1)",
                    },
                    data_column_key="description",
                ),
                # Resize handle for Unit column
                rx.el.div(
                    class_name="resize-handle-object absolute top-0 bottom-0 cursor-col-resize hover:bg-green-500 transition-colors",
                    style={
                        "left": f"{ListsState.column_width_name + ListsState.column_width_description + ListsState.column_width_unit - 2}px",
                        "width": "4px",
                        "zIndex": 50,
                        "pointerEvents": "auto",
                        "backgroundColor": "rgba(34, 197, 94, 0.1)",
                    },
                    data_column_key="unit",
                ),
                # Resize handle for Site column
                rx.el.div(
                    class_name="resize-handle-object absolute top-0 bottom-0 cursor-col-resize hover:bg-green-500 transition-colors",
                    style={
                        "left": f"{ListsState.column_width_name + ListsState.column_width_description + ListsState.column_width_unit + ListsState.column_width_site_name - 2}px",
                        "width": "4px",
                        "zIndex": 50,
                        "pointerEvents": "auto",
                        "backgroundColor": "rgba(34, 197, 94, 0.1)",
                    },
                    data_column_key="site_name",
                ),
                # Resize handle for Value column
                rx.el.div(
                    class_name="resize-handle-object absolute top-0 bottom-0 cursor-col-resize hover:bg-green-500 transition-colors",
                    style={
                        "left": f"{ListsState.column_width_name + ListsState.column_width_description + ListsState.column_width_unit + ListsState.column_width_site_name + ListsState.column_width_value - 2}px",
                        "width": "4px",
                        "zIndex": 50,
                        "pointerEvents": "auto",
                        "backgroundColor": "rgba(34, 197, 94, 0.1)",
                    },
                    data_column_key="value",
                ),
                class_name="absolute inset-0",
                style={"zIndex": 50, "pointerEvents": "none"},
            ),
            # Table rows
            rx.el.div(
                rx.foreach(
                    items,
                    lambda item: rx.el.div(
                        # Name column
                        rx.el.div(
                            rx.el.span(
                                item["name"],
                                class_name="text-white text-sm",
                                style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
                            ),
                            class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 flex items-center",
                            data_column="name",
                            style={
                                "backgroundColor": "rgb(23, 23, 25)",
                                "width": f"{ListsState.column_width_name}px",
                                "minWidth": f"{ListsState.column_width_name}px",
                                "maxWidth": f"{ListsState.column_width_name}px",
                                "overflow": "hidden",
                            },
                        ),
                        # Description column
                        rx.el.div(
                            rx.el.span(
                                item["description"],
                                class_name="text-gray-300 text-sm",
                                style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
                            ),
                            class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 flex items-center",
                            data_column="description",
                            style={
                                "backgroundColor": "rgb(23, 23, 25)",
                                "width": f"{ListsState.column_width_description}px",
                                "minWidth": f"{ListsState.column_width_description}px",
                                "maxWidth": f"{ListsState.column_width_description}px",
                                "overflow": "hidden",
                            },
                        ),
                        # Unit column
                        rx.el.div(
                            rx.el.span(
                                item["unit"],
                                class_name="text-gray-300 text-sm",
                                style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
                            ),
                            class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 flex items-center",
                            data_column="unit",
                            style={
                                "backgroundColor": "rgb(23, 23, 25)",
                                "width": f"{ListsState.column_width_unit}px",
                                "minWidth": f"{ListsState.column_width_unit}px",
                                "maxWidth": f"{ListsState.column_width_unit}px",
                                "overflow": "hidden",
                            },
                        ),
                        # Site column
                        rx.el.div(
                            rx.el.span(
                                item["site_name"],
                                class_name="text-gray-300 text-sm",
                                style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
                            ),
                            class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 flex items-center",
                            data_column="site_name",
                            style={
                                "backgroundColor": "rgb(23, 23, 25)",
                                "width": f"{ListsState.column_width_site_name}px",
                                "minWidth": f"{ListsState.column_width_site_name}px",
                                "maxWidth": f"{ListsState.column_width_site_name}px",
                                "overflow": "hidden",
                            },
                        ),
                        # Value column
                        rx.el.div(
                            rx.el.span(
                                rx.cond(
                                    item["value"] != 0,
                                    item["value"],
                                    "0.00",
                                ),
                                class_name="text-gray-300 text-sm font-mono",
                                style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
                            ),
                            class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 flex items-center",
                            data_column="value",
                            style={
                                "backgroundColor": "rgb(23, 23, 25)",
                                "width": f"{ListsState.column_width_value}px",
                                "minWidth": f"{ListsState.column_width_value}px",
                                "maxWidth": f"{ListsState.column_width_value}px",
                                "overflow": "hidden",
                            },
                        ),
                        # Type column
                        rx.el.div(
                            rx.el.span(
                                item["type"],
                                class_name=rx.cond(
                                    item["type"] == "actual",
                                    "px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-400",
                                    rx.cond(
                                        item["type"] == "forecast",
                                        "px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-400",
                                        "px-2 py-0.5 rounded text-xs font-medium bg-yellow-500/20 text-yellow-400",
                                    ),
                                ),
                            ),
                            class_name="px-4 py-3 flex-shrink-0 flex items-center",
                            data_column="type",
                            style={
                                "backgroundColor": "rgb(23, 23, 25)",
                                "width": f"{ListsState.column_width_type}px",
                                "minWidth": f"{ListsState.column_width_type}px",
                                "maxWidth": f"{ListsState.column_width_type}px",
                                "overflow": "hidden",
                            },
                        ),
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


def configurable_list_view() -> rx.Component:
    """A list view with configurable columns, similar to Attio."""
    return rx.cond(
        ListsState.selected_menu_item != "",
        # Show menu item "coming soon" view
        rx.el.div(
            rx.el.span(
                f"{ListsState.selected_menu_item} view coming soon",
                class_name="text-gray-400 text-sm",
            ),
            class_name="flex items-center justify-center py-12",
        ),
        rx.cond(
            ListsState.selected_object_type != "",
            # Show object type view
            rx.cond(
                ListsState.is_loading,
                # Show loading spinner
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                class_name="w-8 h-8 border-4 border-gray-700 border-t-white rounded-full animate-spin",
                            ),
                            rx.el.span(
                                "Loading...",
                                class_name="text-gray-400 text-sm ml-3",
                            ),
                            class_name="flex items-center",
                        ),
                        class_name="flex items-center justify-center",
                    ),
                    class_name="flex items-center justify-center py-12 min-h-[400px]",
                ),
                rx.cond(
                    ListsState.selected_object_type == "TimeSeries",
                    object_list_view("TimeSeries", ListsState.all_time_series_items),
                    rx.el.div(
                        rx.el.span(
                            f"{ListsState.selected_object_type} view coming soon",
                            class_name="text-gray-400 text-sm",
                        ),
                        class_name="flex items-center justify-center py-12",
                    ),
                ),
            ),
            rx.cond(
                ListsState.selected_list,
                rx.el.div(
            # List header with name and emoji
            rx.el.div(
                rx.el.div(
                    # Emoji button with picker
                    rx.el.div(
                        rx.el.button(
                            rx.el.span(
                                rx.cond(
                                    ListsState.selected_list["emoji"] != "",
                                    ListsState.selected_list["emoji"],
                                    "📋",
                                ),
                                class_name="text-2xl",
                            ),
                            on_click=ListsState.toggle_emoji_picker,
                            class_name="w-10 h-10 flex items-center justify-center hover:bg-gray-800 rounded-md transition-colors",
                        ),
                        # Emoji picker (positioned relative to button)
                        emoji_picker(),
                        class_name="relative mr-3",
                    ),
                    # List name and type
                    rx.el.div(
                        rx.el.h2(
                            ListsState.selected_list["name"],
                            class_name="text-white font-bold text-xl",
                        ),
                        rx.el.span(
                            f"{ListsState.selected_list['object_type']} list",
                            class_name="text-gray-400 text-sm ml-2",
                        ),
                        class_name="flex items-center",
                    ),
                    class_name="flex items-center relative",
                ),
                class_name="mb-6",
            ),
            # Check view type and render accordingly
            rx.cond(
                ListsState.selected_list_view_type == "time_series_cards",
                # Time Series Card Layout with column toggle
                rx.el.div(
                    # Column toggle button
                    rx.el.div(
                        rx.el.button(
                            rx.el.div(
                                rx.cond(
                                    ListsState.timeseries_card_columns == 1,
                                    rx.icon(
                                        "layout-list",
                                        class_name="h-4 w-4 text-white",
                                    ),
                                    rx.icon(
                                        "layout-grid",
                                        class_name="h-4 w-4 text-white",
                                    ),
                                ),
                                rx.el.span(
                                    rx.cond(
                                        ListsState.timeseries_card_columns == 1,
                                        "1 Column",
                                        "2 Columns",
                                    ),
                                    class_name="text-sm text-gray-300 ml-2",
                                ),
                                class_name="flex items-center",
                            ),
                            on_click=ListsState.toggle_timeseries_card_columns,
                            class_name="px-3 py-2 bg-gray-800/50 hover:bg-gray-800/70 rounded-md border border-gray-700 transition-colors",
                        ),
                        class_name="mb-4",
                    ),
                    # Cards grid
                    timeseries_card_grid_view(ListsState.esett_card_data),
                    class_name="",
                ),
                # Default table view
                rx.el.div(
            # Search, Sort, Filter header
            list_header(),
            # Hidden input for column resize updates
            rx.el.input(
                type="hidden",
                id="column-resize-input",
                on_change=ListsState.set_column_width,
            ),
            # Table view with configurable columns - Attio style
            rx.el.div(
                # JavaScript for column resizing - using onload to ensure it runs
                rx.el.script(
                    """
                    window.initColumnResize = function() {
                        console.log('Initializing column resize, found handles:', document.querySelectorAll('.resize-handle').length);
                        document.querySelectorAll('.resize-handle').forEach(function(handle) {
                            // Remove any existing listeners by cloning
                            const newHandle = handle.cloneNode(true);
                            handle.parentNode.replaceChild(newHandle, handle);
                            
                            console.log('Attaching handler to handle:', newHandle.getAttribute('data-column-key'));
                            
                            newHandle.addEventListener('mousedown', function(e) {
                                console.log('Mouse down on resize handle:', newHandle.getAttribute('data-column-key'));
                                e.preventDefault();
                                e.stopPropagation();
                                
                                const columnKey = newHandle.getAttribute('data-column-key');
                                const tableContainer = newHandle.closest('[data-table-container]');
                                if (!tableContainer) {
                                    console.error('Table container not found');
                                    return;
                                }
                                
                                // Find all cells in this column
                                const headerCells = tableContainer.querySelectorAll('[data-column-header="' + columnKey + '"]');
                                const dataCells = tableContainer.querySelectorAll('[data-column="' + columnKey + '"]');
                                
                                if (headerCells.length === 0) {
                                    console.error('Header cells not found for', columnKey);
                                    return;
                                }
                                
                                const firstHeaderCell = headerCells[0];
                                const startX = e.clientX;
                                const startWidth = parseInt(window.getComputedStyle(firstHeaderCell).width, 10);
                                
                                const handleRect = newHandle.getBoundingClientRect();
                                const containerRect = tableContainer.getBoundingClientRect();
                                const startHandleLeft = handleRect.left - containerRect.left;
                                
                                function onMouseMove(e) {
                                    const diff = e.clientX - startX;
                                    const newWidth = Math.max(50, startWidth + diff);
                                    
                                    // Update all header cells
                                    headerCells.forEach(function(cell) {
                                        cell.style.width = newWidth + 'px';
                                        cell.style.minWidth = newWidth + 'px';
                                        cell.style.maxWidth = newWidth + 'px';
                                    });
                                    
                                    // Update all data cells
                                    dataCells.forEach(function(cell) {
                                        cell.style.width = newWidth + 'px';
                                        cell.style.minWidth = newWidth + 'px';
                                        cell.style.maxWidth = newWidth + 'px';
                                    });
                                    
                                    // Update resize handle position
                                    const newHandleLeft = startHandleLeft + diff;
                                    newHandle.style.left = (newHandleLeft - 2) + 'px';
                                    
                                    // Update subsequent handles
                                    const allHandles = Array.from(tableContainer.querySelectorAll('.resize-handle'));
                                    const currentIndex = allHandles.indexOf(newHandle);
                                    const allHeaders = Array.from(tableContainer.querySelectorAll('[data-column-header]'));
                                    
                                    let cumulativeWidth = 0;
                                    allHeaders.forEach(function(headerCell) {
                                        const key = headerCell.getAttribute('data-column-header');
                                        let width;
                                        
                                        if (key === columnKey) {
                                            width = newWidth;
                                        } else {
                                            width = parseInt(window.getComputedStyle(headerCell).width, 10);
                                        }
                                        
                                        cumulativeWidth += width;
                                        
                                        const handleForColumn = allHandles.find(function(h) {
                                            return h.getAttribute('data-column-key') === key;
                                        });
                                        
                                        if (handleForColumn && allHandles.indexOf(handleForColumn) > currentIndex) {
                                            handleForColumn.style.left = (cumulativeWidth - 2) + 'px';
                                        }
                                    });
                                }
                                
                                function onMouseUp(e) {
                                    const diff = e.clientX - startX;
                                    const newWidth = Math.max(50, startWidth + diff);
                                    
                                    // Update state via hidden input
                                    const input = document.getElementById('column-resize-input');
                                    if (input) {
                                        input.value = columnKey + ':' + newWidth;
                                        const event = new Event('change', { bubbles: true });
                                        input.dispatchEvent(event);
                                    }
                                    
                                    document.removeEventListener('mousemove', onMouseMove);
                                    document.removeEventListener('mouseup', onMouseUp);
                                    document.body.style.cursor = '';
                                    document.body.style.userSelect = '';
                                }
                                
                                document.body.style.cursor = 'col-resize';
                                document.body.style.userSelect = 'none';
                                document.addEventListener('mousemove', onMouseMove);
                                document.addEventListener('mouseup', onMouseUp);
                            });
                        });
                    };
                    
                    // Initialize immediately and on load
                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', function() {
                            setTimeout(window.initColumnResize, 100);
                        });
                    } else {
                        setTimeout(window.initColumnResize, 100);
                    }
                    
                    // Re-initialize on mutations
                    const observer = new MutationObserver(function() {
                        setTimeout(window.initColumnResize, 150);
                    });
                    observer.observe(document.body, { childList: true, subtree: true });
                    """
                ),
                # Table header row
                rx.el.div(
                        # First column with "+" button in top-right
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("Name", class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                                rx.el.button(
                                    rx.icon("plus", class_name="h-3.5 w-3.5 text-gray-400 hover:text-white"),
                                    on_click=ListsState.toggle_add_item_modal,
                                    class_name="ml-auto opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-700/50 rounded",
                                ),
                                class_name="flex items-center justify-between",
                            ),
                            class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 group",
                            data_column_header="name",
                            style={
                                "backgroundColor": "rgb(23, 23, 25)",
                                "width": f"{ListsState.column_width_name}px",
                                "minWidth": f"{ListsState.column_width_name}px",
                                "maxWidth": f"{ListsState.column_width_name}px",
                            },
                        ),
                        # Description column
                        rx.el.div(
                            rx.el.span("Description", class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                            class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 relative",
                            data_column_header="description",
                            style={
                                "backgroundColor": "rgb(23, 23, 25)",
                                "width": f"{ListsState.column_width_description}px",
                                "minWidth": f"{ListsState.column_width_description}px",
                                "maxWidth": f"{ListsState.column_width_description}px",
                            },
                        ),
                        # Unit column
                        rx.el.div(
                            rx.el.span("Unit", class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                            class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 relative",
                            data_column_header="unit",
                            style={
                                "backgroundColor": "rgb(23, 23, 25)",
                                "width": f"{ListsState.column_width_unit}px",
                                "minWidth": f"{ListsState.column_width_unit}px",
                                "maxWidth": f"{ListsState.column_width_unit}px",
                            },
                        ),
                        # Site column
                        rx.el.div(
                            rx.el.span("Site", class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                            class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 relative",
                            data_column_header="site_name",
                            style={
                                "backgroundColor": "rgb(23, 23, 25)",
                                "width": f"{ListsState.column_width_site_name}px",
                                "minWidth": f"{ListsState.column_width_site_name}px",
                                "maxWidth": f"{ListsState.column_width_site_name}px",
                            },
                        ),
                        # Value column
                        rx.el.div(
                            rx.el.span("Value", class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                            class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0",
                            data_column_header="value",
                            style={
                                "backgroundColor": "rgb(23, 23, 25)",
                                "width": f"{ListsState.column_width_value}px",
                                "minWidth": f"{ListsState.column_width_value}px",
                                "maxWidth": f"{ListsState.column_width_value}px",
                            },
                        ),
                        # Type column (last, no resize handle)
                        rx.el.div(
                            rx.el.span("Type", class_name="text-gray-400 text-xs font-semibold uppercase tracking-wide"),
                            class_name="px-4 py-3 flex-shrink-0",
                            style={
                                "backgroundColor": "rgb(23, 23, 25)",
                                "width": f"{ListsState.column_width_type}px",
                                "minWidth": f"{ListsState.column_width_type}px",
                                "maxWidth": f"{ListsState.column_width_type}px",
                            },
                        ),
                        class_name="flex border-b border-gray-700 group relative",
                        style={"backgroundColor": "rgb(23, 23, 25)"},
                    ),
                # Resize handles positioned absolutely to span full table height
                rx.el.div(
                    # Resize handle for Name column
                    rx.el.div(
                        class_name="resize-handle absolute top-0 bottom-0 cursor-col-resize hover:bg-green-500 transition-colors",
                        style={
                            "left": f"{ListsState.column_width_name - 2}px",
                            "width": "4px",
                            "zIndex": 50,
                            "pointerEvents": "auto",
                            "backgroundColor": "rgba(34, 197, 94, 0.1)",
                        },
                        data_column_key="name",
                    ),
                    # Resize handle for Description column
                    rx.el.div(
                        class_name="resize-handle absolute top-0 bottom-0 cursor-col-resize hover:bg-green-500 transition-colors",
                        style={
                            "left": f"{ListsState.column_width_name + ListsState.column_width_description - 2}px",
                            "width": "4px",
                            "zIndex": 50,
                            "pointerEvents": "auto",
                            "backgroundColor": "rgba(34, 197, 94, 0.1)",
                        },
                        data_column_key="description",
                    ),
                    # Resize handle for Unit column
                    rx.el.div(
                        class_name="resize-handle absolute top-0 bottom-0 cursor-col-resize hover:bg-green-500 transition-colors",
                        style={
                            "left": f"{ListsState.column_width_name + ListsState.column_width_description + ListsState.column_width_unit - 2}px",
                            "width": "4px",
                            "zIndex": 50,
                            "pointerEvents": "auto",
                            "backgroundColor": "rgba(34, 197, 94, 0.1)",
                        },
                        data_column_key="unit",
                    ),
                    # Resize handle for Site column
                    rx.el.div(
                        class_name="resize-handle absolute top-0 bottom-0 cursor-col-resize hover:bg-green-500 transition-colors",
                        style={
                            "left": f"{ListsState.column_width_name + ListsState.column_width_description + ListsState.column_width_unit + ListsState.column_width_site_name - 2}px",
                            "width": "4px",
                            "zIndex": 50,
                            "pointerEvents": "auto",
                            "backgroundColor": "rgba(34, 197, 94, 0.1)",
                        },
                        data_column_key="site_name",
                    ),
                    # Resize handle for Value column
                    rx.el.div(
                        class_name="resize-handle absolute top-0 bottom-0 cursor-col-resize hover:bg-green-500 transition-colors",
                        style={
                            "left": f"{ListsState.column_width_name + ListsState.column_width_description + ListsState.column_width_unit + ListsState.column_width_site_name + ListsState.column_width_value - 2}px",
                            "width": "4px",
                            "zIndex": 50,
                            "pointerEvents": "auto",
                            "backgroundColor": "rgba(34, 197, 94, 0.1)",
                        },
                        data_column_key="value",
                    ),
                    class_name="absolute inset-0",
                    style={"zIndex": 50, "pointerEvents": "none"},
                ),
                # Table rows
                rx.el.div(
                    rx.foreach(
                        ListsState.selected_list_items,
                        lambda item: rx.el.div(
                            # First column
                            rx.el.div(
                                rx.el.span(
                                    item["name"],
                                    class_name="text-white text-sm",
                                    style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
                                ),
                                class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 flex items-center",
                                data_column="name",
                                style={
                                    "backgroundColor": "rgb(23, 23, 25)",
                                    "width": f"{ListsState.column_width_name}px",
                                    "minWidth": f"{ListsState.column_width_name}px",
                                    "maxWidth": f"{ListsState.column_width_name}px",
                                    "overflow": "hidden",
                                },
                            ),
                            # Description column
                            rx.el.div(
                                rx.el.span(
                                    item["description"],
                                    class_name="text-gray-300 text-sm",
                                    style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
                                ),
                                class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 flex items-center",
                                data_column="description",
                                style={
                                    "backgroundColor": "rgb(23, 23, 25)",
                                    "width": f"{ListsState.column_width_description}px",
                                    "minWidth": f"{ListsState.column_width_description}px",
                                    "maxWidth": f"{ListsState.column_width_description}px",
                                    "overflow": "hidden",
                                },
                            ),
                            # Unit column
                            rx.el.div(
                                rx.el.span(
                                    item["unit"],
                                    class_name="text-gray-300 text-sm",
                                    style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
                                ),
                                class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 flex items-center",
                                data_column="unit",
                                style={
                                    "backgroundColor": "rgb(23, 23, 25)",
                                    "width": f"{ListsState.column_width_unit}px",
                                    "minWidth": f"{ListsState.column_width_unit}px",
                                    "maxWidth": f"{ListsState.column_width_unit}px",
                                    "overflow": "hidden",
                                },
                            ),
                            # Site column
                            rx.el.div(
                                rx.el.span(
                                    item["site_name"],
                                    class_name="text-gray-300 text-sm",
                                    style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
                                ),
                                class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 flex items-center",
                                data_column="site_name",
                                style={
                                    "backgroundColor": "rgb(23, 23, 25)",
                                    "width": f"{ListsState.column_width_site_name}px",
                                    "minWidth": f"{ListsState.column_width_site_name}px",
                                    "maxWidth": f"{ListsState.column_width_site_name}px",
                                    "overflow": "hidden",
                                },
                            ),
                            # Value column
                            rx.el.div(
                                rx.el.span(
                                    rx.cond(
                                        item["value"] != 0,
                                        item["value"],
                                        "0.00",
                                    ),
                                    class_name="text-gray-300 text-sm font-mono",
                                    style={"overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
                                ),
                                class_name="px-4 py-3 border-r border-gray-700 flex-shrink-0 flex items-center",
                                data_column="value",
                                style={
                                    "backgroundColor": "rgb(23, 23, 25)",
                                    "width": f"{ListsState.column_width_value}px",
                                    "minWidth": f"{ListsState.column_width_value}px",
                                    "maxWidth": f"{ListsState.column_width_value}px",
                                    "overflow": "hidden",
                                },
                            ),
                            # Type column
                            rx.el.div(
                                rx.el.span(
                                    item["type"],
                                    class_name=rx.cond(
                                        item["type"] == "actual",
                                        "px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-400",
                                        rx.cond(
                                            item["type"] == "forecast",
                                            "px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-400",
                                            "px-2 py-0.5 rounded text-xs font-medium bg-yellow-500/20 text-yellow-400",
                                        ),
                                    ),
                                ),
                                class_name="px-4 py-3 flex-shrink-0 flex items-center",
                                data_column="type",
                                style={
                                    "backgroundColor": "rgb(23, 23, 25)",
                                    "width": f"{ListsState.column_width_type}px",
                                    "minWidth": f"{ListsState.column_width_type}px",
                                    "maxWidth": f"{ListsState.column_width_type}px",
                                    "overflow": "hidden",
                                },
                            ),
                            class_name="flex border-b border-gray-700/50 hover:opacity-90 transition-opacity",
                            style={"backgroundColor": "rgb(23, 23, 25)"},
                        ),
                    ),
                ),
                class_name="border border-gray-700 rounded-lg overflow-hidden relative",
                style={"backgroundColor": "rgb(23, 23, 25)"},  # Component background
                data_table_container="true",
            ),
            class_name="w-full",
        ),
                ),
            ),
                rx.el.div(
                    rx.el.span(
                        "No list or object selected. Select a list or object to get started.",
                        class_name="text-gray-400 text-sm",
                    ),
                    class_name="flex items-center justify-center py-12",
                ),
            ),
        ),
    )

