import reflex as rx
from app.states.workspace import WorkspaceState


def logo_upload_modal() -> rx.Component:
    """Drag-and-drop-only modal for uploading a workspace logo PNG."""
    return rx.cond(
        WorkspaceState.show_logo_upload_modal,
        rx.el.div(
            # Modal content
            rx.el.div(
                rx.el.div(
                    # Header
                    rx.el.div(
                        rx.el.div(
                            rx.icon("camera", class_name="h-5 w-5 text-gray-400 mr-2"),
                            rx.el.span(
                                "Upload workspace logo",
                                class_name="text-white font-semibold text-lg",
                            ),
                            class_name="flex items-center",
                        ),
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5 text-gray-400 hover:text-white"),
                            on_click=WorkspaceState.close_logo_upload_modal,
                            type="button",
                            class_name="hover:bg-gray-800 rounded-md p-1 transition-colors",
                        ),
                        class_name="flex items-center justify-between mb-4",
                    ),
                    rx.el.p(
                        "Drag and drop a PNG, JPG, or GIF here, or click to choose a file.",
                        class_name="text-gray-400 text-sm mb-4",
                    ),
                    # Drop zone (no file picker)
                    rx.upload(
                        rx.el.div(
                            rx.icon("upload", class_name="h-6 w-6 text-gray-400 mb-2"),
                            rx.el.div(
                                rx.el.p(
                                    "Drop your logo here (or click to upload)",
                                    class_name="text-gray-200 text-sm font-medium",
                                ),
                                rx.el.p(
                                    "Max 10MB • PNG/JPG/GIF",
                                    class_name="text-gray-500 text-xs mt-1",
                                ),
                                class_name="text-center",
                            ),
                            class_name="w-full p-8 border-2 border-dashed border-gray-700 rounded-lg bg-gray-800/30 hover:bg-gray-800/40 transition-colors flex flex-col items-center justify-center cursor-pointer",
                        ),
                        accept={
                            "image/png": [".png"],
                            "image/jpeg": [".jpg", ".jpeg"],
                            "image/gif": [".gif"],
                        },
                        max_files=1,
                        no_click=False,
                        no_keyboard=False,
                        multiple=False,
                        on_drop=WorkspaceState.handle_workspace_logo_upload,
                        class_name="w-full",
                    ),
                    # Footer
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=WorkspaceState.close_logo_upload_modal,
                            type="button",
                            class_name="px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-600",
                        ),
                        class_name="flex justify-end mt-6",
                    ),
                    class_name="relative",
                ),
                class_name="rounded-lg p-6 max-w-md w-full mx-4",
                style={"backgroundColor": "rgb(23, 23, 25)"},
                on_click=rx.stop_propagation,
            ),
            class_name="fixed inset-0 flex items-center justify-center z-50",
            style={"backgroundColor": "rgba(16, 16, 18, 0.8)"},
            on_click=WorkspaceState.close_logo_upload_modal,
        ),
    )


