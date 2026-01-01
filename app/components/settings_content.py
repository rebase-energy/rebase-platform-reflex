import reflex as rx
from app.states.workspace import WorkspaceState
from app.states.collections import CollectionsState
from app.states.entities import EntitiesState


def settings_general_content() -> rx.Component:
    """General settings content."""
    return rx.fragment(
        rx.el.h1(
            "General",
            class_name="text-2xl font-semibold text-white mb-2 mt-0",
        ),
        rx.el.p(
            "Change the settings for your current workspace",
            class_name="text-gray-400 text-sm mb-6",
        ),
        # Workspace logo section
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.span(
                            "R",
                            class_name="text-white text-2xl font-bold",
                        ),
                        class_name="w-16 h-16 bg-green-500 rounded-lg flex items-center justify-center",
                    ),
                    rx.el.div(
                        rx.el.h3(
                            "Workspace logo",
                            class_name="text-white font-medium mb-1",
                        ),
                        rx.el.p(
                            "We only support PNGs, JPEGs and GIFs under 10MB",
                            class_name="text-gray-400 text-sm",
                        ),
                        class_name="ml-4",
                    ),
                    class_name="flex items-center mb-4",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("camera", class_name="h-4 w-4 mr-2"),
                        "Upload new logo",
                        class_name="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors",
                    ),
                    rx.el.button(
                        rx.icon("trash-2", class_name="h-4 w-4 text-red-400"),
                        class_name="ml-2 p-2 hover:bg-gray-800 rounded-md transition-colors",
                    ),
                    class_name="flex items-center",
                ),
                class_name="mb-8",
            ),
            # Name and Slug fields
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Name",
                        class_name="block text-sm font-medium text-gray-300 mb-2",
                    ),
                    rx.el.input(
                        value=WorkspaceState.workspace_name,
                        on_change=WorkspaceState.set_workspace_name,
                        class_name="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-md text-white text-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Slug",
                        class_name="block text-sm font-medium text-gray-300 mb-2",
                    ),
                    rx.el.input(
                        value=WorkspaceState.workspace_slug,
                        disabled=True,
                        class_name="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-md text-gray-500 text-sm cursor-not-allowed",
                    ),
                    rx.el.p(
                        "Slug is automatically generated from the workspace name",
                        class_name="text-gray-500 text-xs mt-1",
                    ),
                    class_name="mb-4",
                ),
                class_name="mb-8",
            ),
            # Export Workspace data section
            rx.el.div(
                rx.el.h3(
                    "Export Workspace data",
                    class_name="text-white font-medium mb-2",
                ),
                rx.el.p(
                    "Exports are in CSV format and can be downloaded within 7 days",
                    class_name="text-gray-400 text-sm mb-4",
                ),
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th("Type", class_name="text-left text-sm font-medium text-gray-400 px-4 py-2"),
                                rx.el.th("Date", class_name="text-left text-sm font-medium text-gray-400 px-4 py-2"),
                                class_name="border-b border-gray-800",
                            ),
                        ),
                        rx.el.tbody(
                            rx.el.tr(
                                rx.el.td(
                                    rx.el.span(
                                        "No exports yet",
                                        class_name="text-gray-500 text-sm",
                                    ),
                                    colspan=2,
                                    class_name="px-4 py-8 text-center",
                                ),
                            ),
                        ),
                        class_name="w-full",
                    ),
                    rx.el.button(
                        rx.icon("download", class_name="h-4 w-4 mr-2"),
                        "Start new export",
                        class_name="flex items-center px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-md text-sm font-medium transition-colors mt-4",
                    ),
                    class_name="flex flex-col",
                ),
            ),
            class_name="p-6 space-y-6",
        ),
    )


def settings_appearance_content() -> rx.Component:
    """Appearance settings content."""
    from app.states.workspace import WorkspaceState
    
    # Predefined accent colors
    accent_colors = [
        ("#3b82f6", "Blue"),
        ("#14b8a6", "Teal"),
        ("#f97316", "Orange"),
        ("#ef4444", "Red"),
        ("#ec4899", "Pink"),
        ("#a855f7", "Purple"),
        ("#10b981", "Green"),
    ]
    
    # Menu items with icons
    menu_items = [
        ("Projects", "folder"),
        ("Workflows", "git-branch"),
        ("Dashboards", "layout-dashboard"),
        ("Notebooks", "book"),
        ("Models", "brain"),
        ("Datasets", "database"),
        ("Notifications", "bell"),
        ("Reports", "bar-chart"),
    ]
    
    return rx.fragment(
        rx.el.h1(
            "Appearance",
            class_name="text-2xl font-semibold text-white mb-2 mt-0",
        ),
        rx.el.p(
            "Customize the look and feel of your platform",
            class_name="text-gray-400 text-sm mb-6",
        ),
        rx.el.div(
            # Theme section
            rx.el.div(
            rx.el.h3(
                "Theme",
                class_name="text-white font-medium mb-1",
            ),
            rx.el.p(
                "Select a theme to personalize your platform's appearance",
                class_name="text-gray-400 text-sm mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    # Light theme
                    rx.el.button(
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.div(
                                            class_name="w-full h-1/2 bg-white rounded border border-gray-200",
                                        ),
                                        class_name="w-full h-full bg-gray-50 rounded-md p-2",
                                    ),
                                ),
                                class_name="w-full h-20 bg-white border border-gray-200 rounded-md mb-2",
                            ),
                            rx.icon("sun", class_name="h-4 w-4 text-gray-400 mx-auto mb-1"),
                            rx.el.span("Light", class_name="text-gray-300 text-sm"),
                            class_name="flex flex-col items-center",
                        ),
                        on_click=WorkspaceState.set_theme("Light"),
                        class_name=rx.cond(
                            WorkspaceState.theme == "Light",
                            "flex flex-col items-center p-4 border-2 border-purple-500 rounded-lg bg-gray-800/50",
                            "flex flex-col items-center p-4 border border-gray-700 rounded-lg hover:border-gray-600 bg-gray-800/30",
                        ),
                    ),
                    # Dark theme
                    rx.el.button(
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.div(
                                            class_name="w-full h-1/2 bg-gray-700 rounded border border-gray-600",
                                        ),
                                        class_name="w-full h-full bg-gray-800 rounded-md p-2",
                                    ),
                                ),
                                class_name="w-full h-20 bg-gray-900 border border-gray-700 rounded-md mb-2",
                            ),
                            rx.icon("moon", class_name="h-4 w-4 text-gray-400 mx-auto mb-1"),
                            rx.el.span("Dark", class_name="text-gray-300 text-sm"),
                            class_name="flex flex-col items-center",
                        ),
                        on_click=WorkspaceState.set_theme("Dark"),
                        class_name=rx.cond(
                            WorkspaceState.theme == "Dark",
                            "flex flex-col items-center p-4 border-2 border-purple-500 rounded-lg bg-gray-800/50",
                            "flex flex-col items-center p-4 border border-gray-700 rounded-lg hover:border-gray-600 bg-gray-800/30",
                        ),
                    ),
                    # System theme
                    rx.el.button(
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.div(
                                            class_name="w-full h-1/2 bg-gray-700 rounded border border-gray-600",
                                        ),
                                        class_name="w-full h-full bg-gray-800 rounded-md p-2",
                                    ),
                                ),
                                class_name="w-full h-20 bg-gradient-to-r from-white to-gray-900 border border-gray-700 rounded-md mb-2",
                            ),
                            rx.icon("monitor", class_name="h-4 w-4 text-gray-400 mx-auto mb-1"),
                            rx.el.span("System", class_name="text-gray-300 text-sm"),
                            class_name="flex flex-col items-center",
                        ),
                        on_click=WorkspaceState.set_theme("System"),
                        class_name=rx.cond(
                            WorkspaceState.theme == "System",
                            "flex flex-col items-center p-4 border-2 border-purple-500 rounded-lg bg-gray-800/50",
                            "flex flex-col items-center p-4 border border-gray-700 rounded-lg hover:border-gray-600 bg-gray-800/30",
                        ),
                    ),
                    class_name="grid grid-cols-3 gap-4",
                ),
                class_name="mb-8",
            ),
            class_name="mb-8",
        ),
        # Accent color section
        rx.el.div(
            rx.el.h3(
                "Accent color",
                class_name="text-white font-medium mb-1",
            ),
            rx.el.p(
                "Choose the main color that defines the overall tone",
                class_name="text-gray-400 text-sm mb-4",
            ),
            rx.el.div(
                # Color swatches
                rx.el.div(
                    rx.foreach(
                        accent_colors,
                        lambda color: rx.el.button(
                            rx.el.div(
                                class_name="w-10 h-10 rounded-full",
                                style={"backgroundColor": color[0]},
                            ),
                            on_click=WorkspaceState.set_accent_color(color[0]),
                            class_name=rx.cond(
                                WorkspaceState.accent_color == color[0],
                                "p-1 border-2 border-white rounded-full",
                                "p-1 border-2 border-transparent rounded-full hover:border-gray-600",
                            ),
                        ),
                    ),
                    class_name="flex gap-3 mb-4",
                ),
                # Custom hex input
                rx.el.div(
                    rx.el.label(
                        "Custom color",
                        class_name="block text-sm font-medium text-gray-300 mb-2",
                    ),
                    rx.el.div(
                        rx.el.div(
                            class_name="w-10 h-10 rounded border border-gray-700",
                            style={"backgroundColor": WorkspaceState.accent_color},
                        ),
                        rx.el.input(
                            type="text",
                            placeholder="#000000",
                            value=WorkspaceState.custom_accent_color,
                            on_change=WorkspaceState.set_custom_accent_color,
                            class_name="flex-1 px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-md text-white text-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500",
                        ),
                        class_name="flex items-center gap-3",
                    ),
                    class_name="max-w-xs",
                ),
                class_name="mb-8",
            ),
            class_name="mb-8",
        ),
        # Menu items visibility section
        rx.el.div(
            rx.el.h3(
                "Menu items",
                class_name="text-white font-medium mb-1",
            ),
            rx.el.p(
                "Toggle menu items to show or hide them in the main workspace",
                class_name="text-gray-400 text-sm mb-4",
            ),
            rx.el.div(
                rx.foreach(
                    WorkspaceState.menu_items_with_visibility,
                    lambda item: rx.el.div(
                        rx.el.div(
                            rx.icon(item[1], class_name="h-4 w-4 text-gray-400 mr-2"),
                            rx.el.span(
                                item[0],
                                class_name="text-gray-300 text-sm flex-1",
                            ),
                            rx.el.button(
                                rx.cond(
                                    item[2],
                                    rx.el.div(
                                        rx.el.div(
                                            class_name="w-4 h-4 bg-white rounded-full absolute right-1 top-1",
                                        ),
                                        class_name="w-11 h-6 bg-green-500 rounded-full relative",
                                    ),
                                    rx.el.div(
                                        rx.el.div(
                                            class_name="w-4 h-4 bg-white rounded-full absolute left-1 top-1",
                                        ),
                                        class_name="w-11 h-6 bg-gray-700 rounded-full relative",
                                    ),
                                ),
                                on_click=WorkspaceState.toggle_menu_item_visibility(item[0]),
                                class_name="flex-shrink-0",
                            ),
                            class_name="flex items-center justify-between px-3 py-2 hover:bg-gray-800/30 rounded-md",
                        ),
                        class_name="mb-1",
                    ),
                ),
                class_name="space-y-0.5",
            ),
            class_name="mb-8",
        ),
        class_name="space-y-8",
        ),
    )


def settings_entities_content() -> rx.Component:
    """Entities settings content."""
    return rx.fragment(
        rx.el.h1(
            "Entities",
            class_name="text-2xl font-semibold text-white mb-2 mt-0",
        ),
        rx.el.p(
            "Manage entity types and configurations",
            class_name="text-gray-400 text-sm mb-6",
        ),
        rx.el.div(
            rx.el.p(
                "Entities settings coming soon...",
                class_name="text-gray-400",
            ),
            class_name="p-6",
        ),
    )


def collection_row(collection: dict) -> rx.Component:
    """Render a single collection row in the settings table."""
    return rx.el.tr(
        # Star icon and Collection name
        rx.el.td(
            rx.el.div(
                rx.el.button(
                    rx.icon(
                        "star",
                        class_name=rx.cond(
                            collection.get("is_favorite", False),
                            "h-4 w-4 text-yellow-400 fill-yellow-400",
                            "h-4 w-4 text-gray-500 hover:text-yellow-400",
                        ),
                    ),
                    on_click=CollectionsState.toggle_collection_favorite(collection["id"]),
                    class_name="mr-2 hover:opacity-80 transition-opacity",
                ),
                rx.el.span(
                    collection["name"],
                    class_name="text-white text-sm",
                ),
                class_name="flex items-center",
            ),
            class_name="px-4 py-3",
        ),
        # Entity type
        rx.el.td(
            rx.el.span(
                collection.get("object_type", "TimeSeries"),
                class_name="px-2 py-0.5 rounded text-xs font-mono bg-gray-700/50 text-gray-300",
            ),
            class_name="px-4 py-3",
        ),
        # Created by
        rx.el.td(
            rx.el.span(
                collection.get("created_by", "You"),
                class_name="text-gray-300 text-sm",
            ),
            class_name="px-4 py-3",
        ),
        # Entries count - access from EntitiesState
        rx.el.td(
            rx.el.span(
                EntitiesState.collection_entry_counts_dict.get(collection["id"], 0),
                class_name="text-gray-300 text-sm",
            ),
            class_name="px-4 py-3",
        ),
        # Default radio button
        rx.el.td(
            rx.el.input(
                type="radio",
                name="default_collection",
                checked=collection.get("is_default", False),
                on_change=CollectionsState.set_default_collection(collection["id"]),
                class_name="custom-radio-button",
            ),
            class_name="px-4 py-3 text-center",
        ),
        # Actions (three dots)
        rx.el.td(
            rx.el.button(
                rx.icon("menu", class_name="h-4 w-4 text-gray-400 hover:text-white"),
                class_name="hover:opacity-80 transition-opacity",
            ),
            class_name="px-4 py-3 text-center",
        ),
        class_name="border-b border-gray-800 hover:bg-gray-800/30 transition-colors",
    )


def settings_collections_content() -> rx.Component:
    """Collections settings content."""
    return rx.fragment(
        rx.el.style(
            """
            .custom-radio-button {
                appearance: none;
                -webkit-appearance: none;
                -moz-appearance: none;
                width: 16px;
                height: 16px;
                border: 2px solid rgb(55, 65, 81);
                border-radius: 50%;
                background-color: rgb(16, 16, 18);
                position: relative;
                cursor: pointer;
                pointer-events: auto;
                z-index: 1;
            }
            .custom-radio-button:checked {
                background-color: rgb(16, 16, 18);
            }
            .custom-radio-button:checked::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: var(--accent-color, #10b981);
                pointer-events: none;
            }
            """,
        ),
        rx.el.h1(
            "Collections",
            class_name="text-2xl font-semibold text-white mb-2 mt-0",
        ),
        rx.el.p(
            "Modify and add Collections in your workspace",
            class_name="text-gray-400 text-sm mb-6",
        ),
        # Search bar and New collection button
        rx.el.div(
            rx.el.input(
                placeholder="Search collections",
                value=CollectionsState.settings_collections_search_query,
                on_change=CollectionsState.set_settings_collections_search_query,
                class_name="w-full px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-md text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500",
            ),
            rx.el.button(
                "+ New collection",
                on_click=CollectionsState.toggle_create_collection_modal,
                class_name="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm font-medium transition-colors whitespace-nowrap",
            ),
            class_name="flex items-center gap-3 mb-6",
        ),
        # Collections table
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Collection", class_name="text-left text-sm font-medium text-gray-400 px-4 py-2"),
                        rx.el.th("Entity", class_name="text-left text-sm font-medium text-gray-400 px-4 py-2"),
                        rx.el.th("Created by", class_name="text-left text-sm font-medium text-gray-400 px-4 py-2"),
                        rx.el.th("Entries", class_name="text-left text-sm font-medium text-gray-400 px-4 py-2"),
                        rx.el.th(
                            rx.el.div(
                                rx.el.span("Default", class_name="mr-1.5"),
                                rx.el.button(
                                    rx.icon(
                                        "circle_help",
                                        class_name="h-3.5 w-3.5 text-gray-500 hover:text-gray-400",
                                    ),
                                    title="The default collection will be showed when logging in.",
                                    class_name="cursor-help inline-flex items-center bg-transparent border-none p-0 hover:opacity-80",
                                    type="button",
                                ),
                                class_name="flex items-center",
                            ),
                            class_name="text-left text-sm font-medium text-gray-400 px-4 py-2",
                        ),
                        rx.el.th("", class_name="text-left text-sm font-medium text-gray-400 px-4 py-2 w-12"),
                        class_name="border-b border-gray-800",
                    ),
                ),
                rx.el.tbody(
                    rx.foreach(
                        CollectionsState.filtered_collections_for_settings,
                        collection_row,
                    ),
                ),
                class_name="w-full",
            ),
            class_name="bg-gray-800/30 rounded-lg overflow-hidden",
        ),
    )


def settings_content(selected_section: str = "General") -> rx.Component:
    """Main settings content area that shows the selected section."""
    return rx.cond(
        selected_section == "General",
        settings_general_content(),
        rx.cond(
            selected_section == "Appearance",
            settings_appearance_content(),
            rx.cond(
                selected_section == "Entities",
                settings_entities_content(),
                settings_collections_content(),
            ),
        ),
    )

