import reflex as rx
from app.states.lists import ListsState
from app.components.lists_sidebar import lists_sidebar
from app.components.configurable_list_view import configurable_list_view
from app.components.create_list_modal import create_list_modal
from app.components.add_item_modal import add_item_modal


def sidebar_resize_handle() -> rx.Component:
    """Resize handle for the sidebar."""
    return rx.el.div(
        rx.el.input(
            type="hidden",
            id="sidebar-resize-input",
            on_change=ListsState.set_sidebar_width,
        ),
        rx.el.script(
            """
            window.initSidebarResize = function() {
                const handle = document.getElementById('sidebar-resize-handle');
                if (!handle) return;
                
                // Remove existing listeners by cloning
                const newHandle = handle.cloneNode(true);
                handle.parentNode.replaceChild(newHandle, handle);
                
                newHandle.addEventListener('mousedown', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const sidebar = document.querySelector('[data-sidebar]');
                    if (!sidebar) return;
                    
                    const startX = e.clientX;
                    const startWidth = parseInt(window.getComputedStyle(sidebar).width, 10);
                    
                    function onMouseMove(e) {
                        const diff = e.clientX - startX;
                        const newWidth = Math.max(200, Math.min(600, startWidth + diff));
                        
                        sidebar.style.width = newWidth + 'px';
                        sidebar.style.minWidth = newWidth + 'px';
                        sidebar.style.maxWidth = newWidth + 'px';
                    }
                    
                    function onMouseUp(e) {
                        const diff = e.clientX - startX;
                        const newWidth = Math.max(200, Math.min(600, startWidth + diff));
                        
                        const input = document.getElementById('sidebar-resize-input');
                        if (input) {
                            input.value = newWidth.toString();
                            const event = new Event('change', { bubbles: true });
                            input.dispatchEvent(event);
                        }
                        
                        document.removeEventListener('mousemove', onMouseMove);
                        document.removeEventListener('mouseup', onMouseUp);
                        document.body.style.cursor = '';
                        document.body.style.userSelect = '';
                    }
                    
                    document.body.style.cursor = 'col-resize';
                    document.body.style.userSelect = 'none';
                    document.addEventListener('mousemove', onMouseMove);
                    document.addEventListener('mouseup', onMouseUp);
                });
            };
            
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', function() {
                    setTimeout(window.initSidebarResize, 100);
                });
            } else {
                setTimeout(window.initSidebarResize, 100);
            }
            
            const observer = new MutationObserver(function() {
                setTimeout(window.initSidebarResize, 150);
            });
            observer.observe(document.body, { childList: true, subtree: true });
            """
        ),
        rx.el.div(
            id="sidebar-resize-handle",
            class_name="w-1 h-full cursor-col-resize hover:bg-green-500/50 transition-colors",
            style={
                "backgroundColor": "rgba(34, 197, 94, 0.1)",
            },
        ),
        class_name="relative",
        style={"zIndex": 10},
    )


def lists_page() -> rx.Component:
    """Main page for the modular list system."""
    return rx.el.div(
        rx.el.div(
            lists_sidebar(),
            data_sidebar="true",
        ),
        rx.cond(
            ListsState.sidebar_collapsed == False,
            sidebar_resize_handle(),
        ),
        rx.el.div(
            rx.el.main(
                rx.el.div(
                    configurable_list_view(),
                    class_name="p-6",
                ),
            ),
            class_name="flex-1 h-screen overflow-y-auto",
            style={"backgroundColor": "rgb(16, 16, 18)"},
        ),
        create_list_modal(),
        add_item_modal(),
        class_name="flex font-['Inter']",
        style={"backgroundColor": "rgb(16, 16, 18)"},
    )

