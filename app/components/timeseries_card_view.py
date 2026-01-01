import reflex as rx
from app.components.timeseries_card import timeseries_card, TimeSeriesCardData


def timeseries_card_view(
    items: list[TimeSeriesCardData],
    columns: int = 2,
    on_column_toggle: callable = None,
    show_column_toggle: bool = True,
) -> rx.Component:
    """
    Reusable time series card grid view component.
    
    Args:
        items: List of time series card data to display
        columns: Number of columns (1 or 2)
        on_column_toggle: Handler for column toggle button
        show_column_toggle: Whether to show the column toggle button
    
    Returns:
        Grid view with time series cards
    """
    return rx.el.div(
        # Column toggle button (if enabled)
        rx.cond(
            show_column_toggle,
            rx.el.div(
                rx.el.button(
                    rx.el.div(
                        rx.cond(
                            columns == 1,
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
                                columns == 1,
                                "1 Column",
                                "2 Columns",
                            ),
                            class_name="text-sm text-gray-300 ml-2",
                        ),
                        class_name="flex items-center",
                    ),
                    on_click=on_column_toggle if on_column_toggle else lambda: None,
                    class_name="px-3 py-2 bg-gray-800/50 hover:bg-gray-800/70 rounded-md border border-gray-700 transition-colors",
                ),
                class_name="mb-4",
            ),
        ),
        # Cards grid
        rx.el.div(
            rx.foreach(
                items,
                lambda card: timeseries_card(card),
            ),
            class_name=rx.cond(
                columns == 1,
                "grid grid-cols-1 gap-6",
                "grid grid-cols-2 gap-6",
            ),
        ),
        class_name="w-full",
    )

