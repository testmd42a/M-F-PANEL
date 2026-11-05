
import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

EMAIL = os.environ.get("KATABUMP_EMAIL")
PASSWORD = os.environ.get("KATABUMP_PASSWORD")
SERVER_ID = os.environ.get("SERVER_ID")

def main():
    if not all([EMAIL, PASSWORD, SERVER_ID]):
        print("ERROR: Missing required GitHub Secrets.")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()

        try:
            print("Opening Katabump login page...")
            page.goto(
                "https://control.katabump.com/auth/login",
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.locator(
                'input[name="username"], input[name="email"], '
                'input[type="email"], input[type="text"]'
            ).first.fill(EMAIL, timeout=20000)

            page.locator(
                'input[name="password"], input[type="password"]'
            ).first.fill(PASSWORD)

            page.locator(
                'button[type="submit"], input[type="submit"]'
            ).first.click()

            page.wait_for_timeout(5000)

            if "/auth/login" in page.url:
                raise RuntimeError("Login may have failed.")

            print("Login redirect detected.")

            server_url = (
                f"https://control.katabump.com/server/{SERVER_ID}"
            )

            page.goto(
                server_url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            renew_btn = page.get_by_role(
                "button", name="Renew", exact=True
            ).or_(
                page.get_by_role("link", name="Renew", exact=True)
            ).first

            try:
                renew_btn.wait_for(state="visible", timeout=15000)
            except PlaywrightTimeout:
                print("Renew button not found.")
                print("Renewal status is unverified.")
                sys.exit(1)

            if not renew_btn.is_enabled():
                print("Renew button is currently disabled.")
                return

            renew_btn.click()
            print("Renew button clicked.")
            print("Server renewal still requires verification.")

        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    main()
