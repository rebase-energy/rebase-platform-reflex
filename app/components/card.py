import reflex as rx
from app.states.state import Site
from .card_chart import card_chart


def card_header(site: Site) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(site["name"], class_name="text-white font-bold text-lg"),
            rx.el.div(
                rx.el.span("Default view", class_name="text-gray-400 text-sm"),
                rx.foreach(
                    site["tags"],
                    lambda tag: rx.el.span(
                        tag,
                        class_name="text-gray-400 text-sm border border-gray-600 rounded px-1",
                    ),
                ),
                class_name="flex items-center space-x-2",
            ),
            class_name="flex flex-col",
        ),
        rx.el.div(
            rx.el.span(site["type"], class_name="text-sm font-medium text-gray-300"),
            rx.el.span(
                site["capacity"], class_name="text-sm font-medium text-gray-300"
            ),
            rx.el.div(
                rx.icon("circle-dot", class_name="h-4 w-4 text-gray-500"),
                class_name="p-1 rounded-full bg-gray-700",
            ),
            rx.icon("square_check", class_name="h-4 w-4 text-green-500"),
            rx.el.span(site["status"], class_name="text-sm text-gray-400"),
            rx.el.button(
                rx.icon("fold_vertical", class_name="h-4 w-4 text-gray-400"),
                class_name="hover:bg-gray-800 p-1 rounded-md",
            ),
            class_name="flex items-center space-x-3",
        ),
        class_name="flex items-start justify-between p-4",
    )


def card(site: Site) -> rx.Component:
    return rx.el.div(
        card_header(site),
        card_chart(site=site),
        class_name="bg-gray-800/50 rounded-lg border border-gray-700",
    )