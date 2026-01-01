"""Standalone demo page for the time series card view component.

This demo showcases the timeseries_card_view component with sample data.
All rendering is done using components from timeseries_card_view.py and timeseries_card.py.
"""
import reflex as rx
from app.components.timeseries_card_view import timeseries_card_view
from app.components.timeseries_card import TimeSeriesCardData, TimeSeriesDataPoint
import random
from datetime import datetime, timedelta


def generate_sample_timeseries_data(name: str, capacity_mw: float) -> TimeSeriesCardData:
    """Generate sample time series data for demo purposes."""
    data_points: list[TimeSeriesDataPoint] = []
    now = datetime.now()
    start_time = now - timedelta(days=1)
    end_time = now + timedelta(days=4)
    current_time = start_time
    
    while current_time <= end_time:
        hour = current_time.hour
        base = capacity_mw * 0.6
        variation = capacity_mw * 0.3 * (0.5 + (hour % 12) / 12)
        actual = base + variation + (capacity_mw * 0.1 * random.uniform(-1, 1))
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
        "id": name.lower().replace(" ", "-").replace("ä", "a").replace("ö", "o"),
        "name": name,
        "capacity_mw": capacity_mw,
        "data": data_points,
        "view_tabs": ["Default view", "Iceloss", "Iceloss pct", "Iceloss weather"],
    }


# Sample data for the demo - wind farms with different capacities
SAMPLE_CARDS: list[TimeSeriesCardData] = [
    generate_sample_timeseries_data("Blackfjället", 90.2),
    generate_sample_timeseries_data("Ranasjo", 150.0),
    generate_sample_timeseries_data("Storberget", 75.5),
    generate_sample_timeseries_data("Vindpark Nord", 200.0),
]


class TimeSeriesDemoState(rx.State):
    """State for time series demo - only data and event handlers, no component code."""
    
    # Sample card data
    cards: list[dict] = SAMPLE_CARDS
    
    # Column layout (1 or 2 columns)
    columns: int = 2
    
    def toggle_columns(self):
        """Toggle between 1 and 2 column layout."""
        self.columns = 1 if self.columns == 2 else 2
    
    def add_card(self):
        """Add a new sample card."""
        new_name = f"Wind Farm {len(self.cards) + 1}"
        new_capacity = random.uniform(50, 200)
        new_card = generate_sample_timeseries_data(new_name, new_capacity)
        self.cards = self.cards + [new_card]


def demo_timeseries_view_page() -> rx.Component:
    """Demo page showing the time series card view component."""
    
    return rx.el.div(
        # Header
        rx.el.div(
            rx.el.h1(
                "Time Series Card View Demo",
                class_name="text-white text-2xl font-bold mb-2",
            ),
            rx.el.p(
                "Interactive time series charts with legend toggling and responsive grid layout.",
                class_name="text-gray-400 text-sm mb-4",
            ),
            rx.el.div(
                rx.link(
                    rx.el.span("← Back to app", class_name="text-green-400 hover:text-green-300 text-sm"),
                    href="/rebase-energy",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-2"),
                    "Add Card",
                    on_click=TimeSeriesDemoState.add_card,
                    class_name="ml-4 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm rounded-md flex items-center transition-colors",
                ),
                class_name="flex items-center",
            ),
            class_name="mb-6",
        ),
        # Time series card view component from timeseries_card_view.py
        timeseries_card_view(
            items=TimeSeriesDemoState.cards,
            columns=TimeSeriesDemoState.columns,
            on_column_toggle=TimeSeriesDemoState.toggle_columns,
            show_column_toggle=True,
        ),
        # Feature list
        rx.el.div(
            rx.el.h3("Features:", class_name="text-white text-lg font-semibold mb-2 mt-8"),
            rx.el.ul(
                rx.el.li("✓ Interactive ECharts with tooltips", class_name="text-gray-300 text-sm mb-1"),
                rx.el.li("✓ Toggle legend items (click Actual/Forecast to show/hide)", class_name="text-gray-300 text-sm mb-1"),
                rx.el.li("✓ 1 or 2 column layout toggle", class_name="text-gray-300 text-sm mb-1"),
                rx.el.li("✓ Red 'now' reference line", class_name="text-gray-300 text-sm mb-1"),
                rx.el.li("✓ Dynamically add new cards", class_name="text-gray-300 text-sm mb-1"),
                class_name="space-y-1",
            ),
            class_name="mt-8 p-4 bg-gray-800/50 rounded-lg border border-gray-700",
        ),
        class_name="p-8 min-h-screen font-['Inter']",
        style={"backgroundColor": "rgb(23, 23, 25)"},
    )

