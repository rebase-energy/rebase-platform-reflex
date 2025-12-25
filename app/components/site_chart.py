import reflex as rx
from app.states.state import Site


def legend_item(color: str, text: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name=f"w-2.5 h-2.5 rounded-full {color}"),
        rx.el.span(text, class_name="text-xs text-gray-400"),
        class_name="flex items-center space-x-2",
    )


def site_chart(site: Site) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p("kW", class_name="text-xs text-gray-400"),
            rx.el.div(
                rx.cond(
                    site["type"] != "Load",
                    legend_item("bg-gray-500", "Capacity"),
                    rx.fragment(),
                ),
                legend_item("bg-yellow-400", "Actual"),
                legend_item("bg-green-500", "Forecast"),
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
                stroke="#ef4444",
                stroke_dasharray="3 3",
            ),
            rx.recharts.area(
                data_key="actual",
                type_="monotone",
                stroke="#f59e0b",
                fill="#f59e0b",
                fill_opacity=0.2,
                stroke_width=2,
                dot=False,
            ),
            rx.recharts.area(
                data_key="forecast",
                type_="monotone",
                stroke="#22c55e",
                fill="#22c55e",
                fill_opacity=0.2,
                stroke_width=2,
                dot=False,
            ),
            rx.recharts.line(
                data_key="capacity",
                type_="monotone",
                stroke="#6b7280",
                stroke_width=2,
                stroke_dasharray="5 5",
                dot=False,
            ),
            data=site["data"],
            height=200,
            margin={"top": 10, "right": 20, "left": 0, "bottom": 0},
        ),
        class_name="pb-4",
    )