from pathlib import Path
import os

PROFILES_DIR = Path(__file__).resolve().parent / "profiles"


def ensure_profile_dir(client_id: int) -> str:
    profile_dir = PROFILES_DIR / str(client_id)
    profile_dir.mkdir(parents=True, exist_ok=True)
    return str(profile_dir)


def open_profile_browser(profile_dir: str):
    """
    Abre o navegador com um perfil persistente do cliente.
    O login do TikTok deve ser feito manualmente uma vez pelo usuário.
    """
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Playwright não está instalado. Rode: pip install -r requirements.txt") from exc

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            profile_dir,
            headless=False,
            viewport={"width": 1400, "height": 900},
        )
        page = browser.new_page()
        page.goto("https://www.tiktok.com")
        print("Faça login no TikTok e pressione ENTER no terminal para fechar o navegador.")
        input()
        browser.close()

    return profile_dir
