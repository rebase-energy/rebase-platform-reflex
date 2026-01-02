import reflex as rx

config = rx.Config(
    app_name="app",
    plugins=[
        rx.plugins.TailwindV3Plugin(),
        rx.plugins.SitemapPlugin(),
    ],
    # Use single port mode for Fly.io deployment
    # Disable SSR to prevent database dependency issues during build
    ssr=False,
)
