import modal

app = modal.App("reflex-all-in-one")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("reflex", "fastapi", "uvicorn", "supabase", "python-dotenv", "reflex-echarts")
    .add_local_dir(".", remote_path="/root/app", copy=True)  # copy=True allows run_commands after
    # Build/export at image build time so the container starts fast.
    .run_commands(
        "cd /root/app && reflex init && API_URL=/api reflex export --no-zip"
    )
)

@app.function(image=image)
@modal.asgi_app()
def asgi():
    # NOTE: The exact export output paths can vary by Reflex version/project layout.
    # After `reflex export --no-zip`, inspect the folders created and adjust paths/imports below.
    import os
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles

    os.chdir("/root/app")

    api = FastAPI()

    # 1) Serve exported frontend (adjust path to your export output)
    # Commonly you'll get something like `frontend/` or a web build directory.
    api.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

    # 2) Mount exported backend ASGI app (adjust import to match exported backend entrypoint)
    # Often exported backend contains a `main.py` with `app = FastAPI()` or similar.
    from backend.main import app as reflex_backend_app  # <-- adjust if needed
    api.mount("/api", reflex_backend_app)

    return api
