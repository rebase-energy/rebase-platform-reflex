import os
import subprocess

import modal

APP_NAME = "reflex-platform"
APP_PORT = 8000

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("curl", "unzip")
    # Install bun for faster frontend builds
    .run_commands("curl -fsSL https://bun.sh/install | bash")
    .env({"PATH": "/root/.bun/bin:$PATH", "BUN_INSTALL": "/root/.bun"})
    .pip_install(
        "reflex==0.8.24.post1",
        "supabase==2.10.0",
        "python-dotenv>=1.0.0",
        "reflex-echarts>=0.1.0",
    )
    # Copy source files, excluding generated directories (dockerignore syntax)
    .add_local_dir(
        ".",
        remote_path="/root/app",
        copy=True,
        ignore=[".web", ".venv", "__pycache__", ".git", "node_modules", ".states"],
    )
    # Build frontend at image build time
    .run_commands("cd /root/app && reflex init")
)

app = modal.App(APP_NAME)


def _run_reflex() -> None:
    # Reflex uses a single port for frontend + backend when deployed on Modal.
    env = os.environ.copy()
    env.setdefault("REFLEX_ENV", "prod")
    subprocess.Popen(
        [
            "reflex",
            "run",
            "--env",
            "prod",
            "--single-port",
            "--backend-host",
            "0.0.0.0",
            "--frontend-port",
            str(APP_PORT),
            "--backend-port",
            str(APP_PORT),
        ],
        cwd="/root/app",
        env=env,
    )


@app.function(
    image=image,
)
@modal.web_server(port=APP_PORT, startup_timeout=300)
def serve() -> None:
    _run_reflex()
