import reflex as rx


def sidebar_icon(icon_name: str, is_active: bool = False) -> rx.Component:
    return rx.el.div(
        rx.icon(
            icon_name,
            class_name=rx.cond(
                is_active, "text-white", "text-gray-400 group-hover:text-white"
            ),
        ),
        class_name=rx.cond(
            is_active,
            "p-3 rounded-lg bg-gray-700",
            "p-3 rounded-lg group hover:bg-gray-800 cursor-pointer",
        ),
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                sidebar_icon("bar-chart-horizontal", is_active=True),
                sidebar_icon("database"),
                sidebar_icon("bolt"),
                sidebar_icon("layout-grid"),
                sidebar_icon("circle-dot"),
                sidebar_icon("flag_triangle_right"),
                class_name="flex flex-col items-center space-y-2",
            ),
            class_name="p-2",
        ),
        class_name="h-screen bg-gray-900 border-r border-gray-800",
    )