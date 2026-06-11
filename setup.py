from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
import venv


ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
REQUIREMENTS = [
    "Flask>=3.0.0",
    "python-dotenv>=1.0.1",
    "psycopg[binary]>=3.2.0",
]
APP_HOST = "127.0.0.1"
APP_PORT = 5000


def run(command: list[str]) -> None:
    subprocess.check_call(command, cwd=ROOT)


def ensure_venv() -> None:
    if VENV_DIR.exists():
        return
    print("Criando ambiente virtual em .venv...")
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(VENV_DIR)


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def install_dependencies() -> None:
    python_exe = venv_python()
    print("Atualizando pip e instalando dependências...")
    run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(python_exe), "-m", "pip", "install", *REQUIREMENTS])


def write_requirements_file() -> None:
    requirements_path = ROOT / "requirements.txt"
    current = "\n".join(REQUIREMENTS) + "\n"
    requirements_path.write_text(current, encoding="utf-8")


def launch_app() -> int:
    python_exe = venv_python()
    print()
    print("Iniciando o projeto Flask...")
    print(f"Abra no navegador: http://{APP_HOST}:{APP_PORT}")

    def open_browser() -> None:
        time.sleep(1.5)
        webbrowser.open(f"http://{APP_HOST}:{APP_PORT}")

    threading.Thread(target=open_browser, daemon=True).start()
    return subprocess.call([str(python_exe), "-m", "app.main"], cwd=ROOT)


def main() -> int:
    print("Iniciando bootstrap do projeto...")
    ensure_venv()
    write_requirements_file()
    install_dependencies()
    server_exit_code = launch_app()
    print()
    print(f"Projeto finalizado com código de saída: {server_exit_code}")
    print(f"Ambiente virtual criado em: {VENV_DIR}")
    print("Para ativar no Windows: .venv\\Scripts\\Activate.ps1")
    return server_exit_code


if __name__ == "__main__":
    raise SystemExit(main())
