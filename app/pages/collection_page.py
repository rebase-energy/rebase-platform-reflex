import reflex as rx
from app.components.collections_sidebar import collections_sidebar
from app.components.collection_view import collection_view
from app.components.create_collection_modal import create_collection_modal
from app.components.add_item_modal import add_item_modal
from app.states.collections import CollectionsState


def collection_page() -> rx.Component:
    """Collection page for a specific collection."""
    return rx.el.div(
        # Script to load collection from route parameter on page load
        rx.el.script(
            r"""
            (function() {
                // Extract collection_id from URL
                const path = window.location.pathname;
                const match = path.match(/\/collections\/([^\/]+)/);
                if (match && match[1]) {
                    const collectionId = match[1];
                    // Load the collection using Reflex event system
                    if (window.reflex && window.reflex.call_event) {
                        window.reflex.call_event(
                            'CollectionsState.load_collection_page',
                            [collectionId]
                        );
                    }
                } else {
                    // Fallback: use a placeholder collection_id for now
                    // In the future, this will be provided by the database
                    const placeholderId = 'default-timeseries';
                    if (window.reflex && window.reflex.call_event) {
                        window.reflex.call_event(
                            'CollectionsState.load_collection_page',
                            [placeholderId]
                        );
                    }
                }
            })();
            """,
        ),
        collections_sidebar(),
        rx.el.div(
            rx.el.div(
                collection_view(),
                class_name="p-6 pt-6",
            ),
            class_name="flex-1 h-screen overflow-y-auto",
            style={"backgroundColor": "rgb(23, 23, 25)"},
        ),
        create_collection_modal(),
        add_item_modal(),
        class_name="flex font-['Inter']",
        style={"backgroundColor": "rgb(16, 16, 18)"},
    )

