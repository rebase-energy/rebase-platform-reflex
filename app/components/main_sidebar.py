"""Main sidebar component with menu items and collapsible sections."""
import reflex as rx
from app.states.workspace import WorkspaceState
from app.states.entities import EntitiesState
from app.states.collections import CollectionsState

# Default workspace slug - matches WorkspaceState.workspace_slug default
DEFAULT_WORKSPACE_SLUG = "rebase-energy"


def rebase_icon() -> rx.Component:
    """Rebase logo icon."""
    return rx.el.img(
        src=rx.cond(
            WorkspaceState.workspace_logo_data_url != "",
            WorkspaceState.workspace_logo_data_url,
            "/logo.png",
        ),
        alt="rebase-energy",
        class_name="w-6 h-6 mr-2 flex-shrink-0",
    )


def menu_item(
    title: str,
    icon_name: str,
    on_click_handler: callable = None,
) -> rx.Component:
    """A simple menu item with icon and title."""
    content = rx.el.div(
        rx.icon(icon_name, class_name="h-4 w-4 text-gray-400 mr-2"),
        rx.el.span(
            title,
            class_name="text-gray-300 text-sm font-medium flex-1 text-left",
        ),
        class_name="flex items-center",
    )
    
    if on_click_handler is not None:
        return rx.el.button(
            content,
            on_click=on_click_handler,
            class_name="w-full flex items-center px-3 py-2 hover:bg-gray-800/30 rounded-md text-left transition-colors",
        )
    else:
        return rx.el.button(
            content,
            class_name="w-full flex items-center px-3 py-2 hover:bg-gray-800/30 rounded-md text-left transition-colors",
        )


def collapsible_section(
    title: str,
    icon_name: str,
    is_expanded: bool,
    toggle_handler: callable,
    add_handler: callable,
    children: rx.Component,
    options_handler: callable = None,
) -> rx.Component:
    """A collapsible section with header, icon, options button, and add button."""
    # Build the options button conditionally
    options_button = rx.el.button(
        rx.icon("settings", class_name="h-3.5 w-3.5 text-gray-400 hover:text-white"),
        on_click=options_handler,
        class_name="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-gray-700/50 rounded mr-1",
    ) if options_handler is not None else rx.el.button(
        rx.icon("settings", class_name="h-3.5 w-3.5 text-gray-400 hover:text-white"),
        class_name="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-gray-700/50 rounded mr-1",
    )
    
    return rx.el.div(
        # Section header
        rx.el.div(
            rx.el.div(
                rx.el.button(
                    rx.cond(
                        is_expanded,
                        rx.icon("chevron-down", class_name="h-4 w-4 text-gray-400 mr-2 transition-transform"),
                        rx.icon("chevron-right", class_name="h-4 w-4 text-gray-400 mr-2 transition-transform"),
                    ),
                    rx.icon(icon_name, class_name="h-4 w-4 text-gray-400 mr-2"),
                    rx.el.span(
                        title,
                        class_name="text-gray-300 text-sm font-medium flex-1 text-left",
                    ),
                    on_click=toggle_handler,
                    class_name="flex items-center flex-1",
                ),
                options_button,
                rx.el.button(
                    rx.icon("plus", class_name="h-3.5 w-3.5 text-gray-400 hover:text-white"),
                    on_click=add_handler,
                    class_name="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-gray-700/50 rounded",
                ),
                class_name="flex items-center group hover:bg-gray-800/30 rounded-md px-3 py-2 transition-colors",
            ),
            class_name="mb-1",
        ),
        # Section content (only shown when expanded)
        rx.cond(
            is_expanded,
            rx.el.div(
                children,
                class_name="ml-6 space-y-0.5",
            ),
        ),
        class_name="mb-2",
    )


def main_sidebar() -> rx.Component:
    """Main sidebar with menu items and collapsible sections: Favorites, Entities, and Collections."""
    return rx.el.aside(
        rx.el.div(
            # Workspace selector with toggle button
            rx.cond(
                WorkspaceState.sidebar_collapsed == False,
                rx.el.div(
                    rx.el.div(
                        # Workspace selector button
                        rx.el.button(
                            rx.el.div(
                                rebase_icon(),
                                rx.el.span(
                                    "rebase-energy",
                                    class_name="text-white text-sm font-medium",
                                ),
                                rx.icon("chevron-down", class_name="h-4 w-4 text-gray-400 ml-2"),
                                rx.el.button(
                                    rx.icon("panel-left", class_name="h-4 w-4 text-gray-400"),
                                    on_click=WorkspaceState.toggle_sidebar,
                                    class_name="ml-auto p-1 hover:bg-gray-800/30 rounded transition-colors",
                                ),
                                class_name="flex items-center w-full",
                            ),
                            on_click=WorkspaceState.toggle_workspace_dropdown,
                            class_name="w-full px-3 py-2 hover:bg-gray-800/30 rounded-md text-left",
                            id="workspace-selector-button",
                        ),
                        # Dropdown menu
                        rx.cond(
                            WorkspaceState.workspace_dropdown_open,
                            rx.el.div(
                                rx.el.script(
                                    """
                                    (function() {
                                        const button = document.getElementById('workspace-selector-button');
                                        const dropdown = document.getElementById('workspace-dropdown');
                                        if (button && dropdown) {
                                            const rect = button.getBoundingClientRect();
                                            dropdown.style.position = 'fixed';
                                            dropdown.style.top = (rect.bottom + 4) + 'px';
                                            dropdown.style.left = (rect.left - 8) + 'px';
                                        }
                                    })();
                                    """,
                                ),
                                rx.el.button(
                                    rx.el.div(
                                        rx.icon("plus", class_name="h-4 w-4 text-gray-400 mr-2"),
                                        rx.el.span(
                                            "New workspace",
                                            class_name="text-gray-300 text-sm",
                                        ),
                                        class_name="flex items-center",
                                    ),
                                    on_click=WorkspaceState.close_workspace_dropdown,
                                    class_name="w-full flex items-center px-3 py-2 hover:bg-gray-800/50 rounded-md text-left transition-colors",
                                ),
                                rx.el.button(
                                    rx.el.div(
                                        rx.icon("settings", class_name="h-4 w-4 text-gray-400 mr-2"),
                                        rx.el.span(
                                            "Settings",
                                            class_name="text-gray-300 text-sm",
                                        ),
                                        class_name="flex items-center",
                                    ),
                                    on_click=WorkspaceState.navigate_to_settings,
                                    class_name="w-full flex items-center px-3 py-2 hover:bg-gray-800/50 rounded-md text-left transition-colors",
                                ),
                                rx.el.button(
                                    rx.el.div(
                                        rx.icon("user-plus", class_name="h-4 w-4 text-gray-400 mr-2"),
                                        rx.el.span(
                                            "Invite team members",
                                            class_name="text-gray-300 text-sm",
                                        ),
                                        class_name="flex items-center",
                                    ),
                                    on_click=WorkspaceState.close_workspace_dropdown,
                                    class_name="w-full flex items-center px-3 py-2 hover:bg-gray-800/50 rounded-md text-left transition-colors",
                                ),
                                rx.el.button(
                                    rx.el.div(
                                        rx.icon("layout-grid", class_name="h-4 w-4 text-gray-400 mr-2"),
                                        rx.el.span(
                                            "Integrations",
                                            class_name="text-gray-300 text-sm",
                                        ),
                                        class_name="flex items-center",
                                    ),
                                    on_click=WorkspaceState.close_workspace_dropdown,
                                    class_name="w-full flex items-center px-3 py-2 hover:bg-gray-800/50 rounded-md text-left transition-colors",
                                ),
                                class_name="w-64 bg-gray-900 border border-gray-800 rounded-lg shadow-lg p-1",
                                style={
                                    "backgroundColor": "rgb(23, 23, 25)",
                                    "zIndex": 9999,
                                },
                                id="workspace-dropdown",
                            ),
                        ),
                        class_name="relative",
                    ),
                    class_name="p-3 border-b border-gray-800",
                ),
                # Collapsed state - sidebar is completely hidden, no content here
                rx.fragment(),
            ),
            # Quick Actions - only when expanded
            rx.cond(
                WorkspaceState.sidebar_collapsed == False,
                rx.el.div(
                    # Quick Actions
                    rx.el.div(
                        rx.el.div(
                            rx.icon("search", class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400"),
                            rx.el.input(
                                placeholder="Quick actions",
                                class_name="w-full border border-gray-700/50 pl-9 pr-3 py-2 rounded-md text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500",
                                style={"backgroundColor": "rgb(23, 23, 25)"},
                            ),
                            class_name="relative mb-4",
                        ),
                        class_name="p-3",
                    ),
                    class_name="",
                ),
            ),
            # Sections container
            rx.cond(
                WorkspaceState.sidebar_collapsed == False,
                rx.el.div(
                # Top menu items - only show if visible in settings
                rx.el.div(
                    rx.foreach(
                        WorkspaceState.visible_menu_items,
                        lambda item: rx.link(
                            rx.el.div(
                                rx.icon(item[1], class_name="h-4 w-4 text-gray-400 mr-2"),
                                rx.el.span(
                                    item[0],
                                    class_name="text-gray-300 text-sm font-medium flex-1 text-left",
                                ),
                                class_name="flex items-center",
                            ),
                            href=f"/{DEFAULT_WORKSPACE_SLUG}/{item[0].lower()}",
                            class_name="w-full flex items-center px-3 py-2 hover:bg-gray-800/30 rounded-md text-left transition-colors",
                        ),
                    ),
                    class_name="px-2 mb-4 space-y-0.5",
                ),
                # Favorites section
                collapsible_section(
                    title="Favorites",
                    icon_name="star",
                    is_expanded=WorkspaceState.favorites_expanded,
                    toggle_handler=WorkspaceState.toggle_favorites,
                    add_handler=CollectionsState.toggle_create_collection_modal,
                    children=rx.el.div(
                        rx.el.span(
                            "No favorites yet",
                            class_name="text-gray-500 text-xs px-3 py-1",
                        ),
                    ),
                ),
                # Entities section
                collapsible_section(
                    title="Entities",
                    icon_name="database",
                    is_expanded=WorkspaceState.objects_expanded,
                    toggle_handler=WorkspaceState.toggle_objects,
                    add_handler=CollectionsState.toggle_create_collection_modal,
                    children=rx.el.div(
                        rx.link(
                            rx.icon("building", class_name="h-4 w-4 text-gray-400 mr-2"),
                            rx.el.span(
                                "TimeSeries",
                                class_name="px-2 py-0.5 rounded text-xs font-mono bg-gray-700/50 text-gray-300",
                            ),
                            href=f"/{DEFAULT_WORKSPACE_SLUG}/entities/timeseries",
                            class_name="w-full flex items-center px-3 py-2 hover:bg-gray-800/30 rounded-md text-left transition-colors",
                        ),
                        rx.link(
                            rx.icon("zap", class_name="h-4 w-4 text-gray-400 mr-2"),
                            rx.el.span(
                                "Sites",
                                class_name="px-2 py-0.5 rounded text-xs font-mono bg-gray-700/50 text-gray-300",
                            ),
                            href=f"/{DEFAULT_WORKSPACE_SLUG}/entities/sites",
                            class_name="w-full flex items-center px-3 py-2 hover:bg-gray-800/30 rounded-md text-left transition-colors",
                        ),
                        rx.link(
                            rx.icon("package", class_name="h-4 w-4 text-gray-400 mr-2"),
                            rx.el.span(
                                "Assets",
                                class_name="px-2 py-0.5 rounded text-xs font-mono bg-gray-700/50 text-gray-300",
                            ),
                            href=f"/{DEFAULT_WORKSPACE_SLUG}/entities/assets",
                            class_name="w-full flex items-center px-3 py-2 hover:bg-gray-800/30 rounded-md text-left transition-colors",
                        ),
                        class_name="flex flex-col gap-2",
                    ),
                ),
                # Collections section
                collapsible_section(
                    title="Collections",
                    icon_name="list",
                    is_expanded=WorkspaceState.collections_expanded,
                    toggle_handler=WorkspaceState.toggle_collections,
                    add_handler=CollectionsState.toggle_create_collection_modal,
                    children=rx.el.div(
                        rx.foreach(
                            CollectionsState.collections,
                            lambda lst: rx.link(
                                rx.el.div(
                                    rx.icon(
                                        "rocket",
                                        class_name="h-4 w-4 text-gray-400 mr-2",
                                    ),
                                    rx.el.span(
                                        lst["name"],
                                        class_name="text-gray-300 text-sm",
                                    ),
                                    class_name="flex items-center",
                                ),
                                href=f"/{DEFAULT_WORKSPACE_SLUG}/collections/{lst['id']}",
                                class_name="w-full flex items-center px-3 py-2 hover:bg-gray-800/30 rounded-md text-left transition-colors",
                            ),
                        ),
                    ),
                ),
                class_name="px-2 pb-4",
            ),
            ),
            class_name="h-full overflow-y-auto",
        ),
        class_name="h-screen border-r border-gray-800 flex flex-col transition-all duration-300",
        style={
            "backgroundColor": "rgb(16, 16, 18)",
            "width": WorkspaceState.get_sidebar_width_px,
            "minWidth": WorkspaceState.get_sidebar_width_px,
            "maxWidth": WorkspaceState.get_sidebar_width_px,
        },
    )

