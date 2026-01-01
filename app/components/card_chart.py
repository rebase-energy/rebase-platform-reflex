import reflex as rx
from app.states.state import Site, DashboardState


def legend_item(color: str, text: str, site_name: str, series_name: str, is_visible: bool) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            rx.el.div(
                class_name=f"w-2.5 h-2.5 rounded-full {color}",
                style={"opacity": "1" if is_visible else "0.3"},
            ),
            rx.el.span(
                text,
                class_name="text-xs text-gray-400",
                style={"opacity": "1" if is_visible else "0.3"},
            ),
            class_name="flex items-center space-x-2 cursor-pointer hover:opacity-80",
        ),
        on_click=DashboardState.toggle_chart_series(site_name, series_name),
    )


def card_chart(site: Site) -> rx.Component:
    site_name = site["name"]
    # Get visibility state reactively
    visibility_dict = DashboardState.chart_legend_visibility.get(site_name, {})
    capacity_visible = visibility_dict.get("Capacity", True) if isinstance(visibility_dict, dict) else True
    actual_visible = visibility_dict.get("Actual", True) if isinstance(visibility_dict, dict) else True
    forecast_visible = visibility_dict.get("Forecast", True) if isinstance(visibility_dict, dict) else True
    
    return rx.el.div(
        rx.el.div(
            rx.el.p("kW", class_name="text-xs text-gray-400"),
            rx.el.div(
                rx.cond(
                    site["type"] != "Load",
                    legend_item("bg-gray-500", "Capacity", site_name, "Capacity", capacity_visible),
                    rx.fragment(),
                ),
                legend_item("bg-yellow-400", "Actual", site_name, "Actual", actual_visible),
                legend_item("bg-green-500", "Forecast", site_name, "Forecast", forecast_visible),
                class_name="flex items-center space-x-4",
            ),
            class_name="flex justify-between items-center mb-2 px-4 pt-2",
        ),
        rx.recharts.composed_chart(
            rx.recharts.cartesian_grid(stroke="#374151", vertical=False),
            rx.recharts.x_axis(
                data_key="time",
                tick_line=False,
                axis_line=False,
                stroke="#9ca3af",
                font_size=12,
                tick_margin=10,
            ),
            rx.recharts.y_axis(
                domain=["dataMin", "dataMax"],
                allow_decimals=False,
                tick_line=False,
                axis_line=False,
                stroke="#9ca3af",
                font_size=12,
                tick_margin=10,
                width=50,
            ),
            rx.recharts.tooltip(
                cursor=False,
                content_style={
                    "background_color": "#111827",
                    "border": "1px solid #374151",
                },
            ),
            rx.recharts.reference_line(
                x=rx.Var.create("data[24].time"),
                stroke="#dc2626",
                stroke_dasharray="3 3",
                stroke_width=1,
                label=False,
                is_animation_active=False,
            ),
            rx.cond(
                capacity_visible,
                rx.recharts.line(
                    data_key="capacity",
                    type_="monotone",
                    stroke="#6b7280",
                    stroke_width=2,
                    stroke_dasharray="5 5",
                    dot=False,
                ),
                rx.fragment(),
            ),
            rx.cond(
                actual_visible,
                rx.recharts.line(
                    data_key="actual",
                    type_="monotone",
                    stroke="#f59e0b",
                    stroke_width=2,
                    dot=False,
                ),
                rx.fragment(),
            ),
            rx.cond(
                forecast_visible,
                rx.recharts.line(
                    data_key="forecast",
                    type_="monotone",
                    stroke="#22c55e",
                    stroke_width=2,
                    dot=False,
                ),
                rx.fragment(),
            ),
            data=site["data"],
            height=200,
            margin={"top": 10, "right": 20, "left": 0, "bottom": 0},
            style={"backgroundColor": "rgb(17,18,20)"},
        ),
        class_name="pb-4",
    )