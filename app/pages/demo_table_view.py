"""Standalone demo page for the table view component.

This demo showcases the data_table component with sample data.
All rendering is done using reusable cell renderers from table_view.py.
"""
import reflex as rx
from app.components.table_view import (
    data_table,
    TableColumn,
    # Reusable cell renderers
    text_cell,
    badge_cell,
    status_cell,
    value_cell,
)


# Sample data for the demo
SAMPLE_DATA = [
    {
        "name": "Blackfjället Power",
        "description": "Wind power production at Blackfjället site",
        "unit": "MW",
        "site": "Blackfjället",
        "value": "87.5",
        "status": "Active",
    },
    {
        "name": "Ranasjo Energy",
        "description": "Solar production at Ranasjo facility",
        "unit": "MW",
        "site": "Ranasjo",
        "value": "142.3",
        "status": "Active",
    },
    {
        "name": "Hydro Station 1",
        "description": "Hydroelectric power generation",
        "unit": "MW",
        "site": "Northern Region",
        "value": "225.8",
        "status": "Maintenance",
    },
    {
        "name": "Battery Storage A",
        "description": "Energy storage system",
        "unit": "MWh",
        "site": "Central Hub",
        "value": "98.2",
        "status": "Active",
    },
    {
        "name": "Solar Farm Beta",
        "description": "Large-scale solar installation",
        "unit": "MW",
        "site": "Southern Plains",
        "value": "156.7",
        "status": "Active",
    },
]


class TableDemoState(rx.State):
    """State for table demo - only data and event handlers, no component code."""
    
    # Sample data
    sample_items: list[dict] = SAMPLE_DATA
    
    # Column widths (editable via resize)
    col_width_name: int = 200
    col_width_description: int = 300
    col_width_unit: int = 100
    col_width_site: int = 150
    col_width_value: int = 120
    col_width_status: int = 120
    
    def handle_column_resize(self, value: str):
        """Handle column width changes."""
        if not value or ":" not in value:
            return
        
        column_key, new_width = value.split(":")
        new_width = int(new_width)
        
        width_map = {
            "name": "col_width_name",
            "description": "col_width_description",
            "unit": "col_width_unit",
            "site": "col_width_site",
            "value": "col_width_value",
            "status": "col_width_status",
        }
        
        if column_key in width_map:
            setattr(self, width_map[column_key], new_width)
    
    def add_item(self):
        """Add a new item to the table."""
        new_item = {
            "name": f"New Item {len(self.sample_items) + 1}",
            "description": "Newly added item",
            "unit": "MW",
            "site": "Demo Site",
            "value": "50.0",
            "status": "Active",
        }
        self.sample_items = self.sample_items + [new_item]


def demo_table_view_page() -> rx.Component:
    """Demo page showing the table component using only reusable renderers."""
    
    # Column definitions using reusable cell renderers from table_view.py
    columns: list[TableColumn] = [
        {"key": "name", "label": "Name", "width": TableDemoState.col_width_name, "render": text_cell("name", bold=True, color="white")},
        {"key": "description", "label": "Description", "width": TableDemoState.col_width_description, "render": text_cell("description")},
        {"key": "unit", "label": "Unit", "width": TableDemoState.col_width_unit, "render": badge_cell("unit")},
        {"key": "site", "label": "Site", "width": TableDemoState.col_width_site, "render": text_cell("site")},
        {"key": "value", "label": "Value", "width": TableDemoState.col_width_value, "render": value_cell("value")},
        {"key": "status", "label": "Status", "width": TableDemoState.col_width_status, "render": status_cell("status")},
    ]
    
    return rx.el.div(
        # Header
        rx.el.div(
            rx.el.h1(
                "Table View Component Demo",
                class_name="text-white text-2xl font-bold mb-2",
            ),
            rx.el.p(
                "Interactive table with resizable columns. Drag the green handles to resize columns.",
                class_name="text-gray-400 text-sm mb-4",
            ),
            rx.link(
                rx.el.span("← Back to app", class_name="text-green-400 hover:text-green-300 text-sm"),
                href="/rebase-energy",
            ),
            class_name="mb-6",
        ),
        # Table component from table_view.py
        data_table(
            items=TableDemoState.sample_items,
            columns=columns,
            on_column_width_change=TableDemoState.handle_column_resize,
            on_add_item=TableDemoState.add_item,
            resize_input_id="demo-column-resize",
            resize_handle_class="demo-resize-handle",
        ),
        # Feature list
        rx.el.div(
            rx.el.h3("Features:", class_name="text-white text-lg font-semibold mb-2 mt-8"),
            rx.el.ul(
                rx.el.li("✓ Resizable columns (drag the green handles)", class_name="text-gray-300 text-sm mb-1"),
                rx.el.li("✓ Reusable cell renderers (text_cell, badge_cell, status_cell, value_cell)", class_name="text-gray-300 text-sm mb-1"),
                rx.el.li("✓ Add items button (+ icon on hover over 'Name' column header)", class_name="text-gray-300 text-sm mb-1"),
                rx.el.li("✓ Hover effects on rows", class_name="text-gray-300 text-sm mb-1"),
                class_name="space-y-1",
            ),
            class_name="mt-8 p-4 bg-gray-800/50 rounded-lg border border-gray-700",
        ),
        class_name="p-8 min-h-screen font-['Inter']",
        style={"backgroundColor": "rgb(23, 23, 25)"},
    )
