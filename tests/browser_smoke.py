"""Exercise the built starter at a project subpath in Chromium."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import shutil
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    screenshots = ROOT / "browser-checks"
    screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        shutil.copytree(ROOT / "dist", Path(temporary) / "example-tool")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=temporary))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=os.getenv("CHROMIUM_PATH"))
                page = browser.new_page(viewport={"width": 1280, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                url=f"http://127.0.0.1:{server.server_port}/example-tool/"
                page.goto(url)
                page.wait_for_function("document.querySelector('#day-date').min !== ''")
                page.fill("#day-date", page.locator("#day-date").get_attribute("min"))
                page.wait_for_selector("#day-tides tr")
                assert page.locator("#day-mode").get_attribute("aria-pressed") == "true"
                assert page.locator("#day-sunrise").inner_text() != "—"
                page.select_option("#day-station", "vancouver")
                assert "America/Vancouver" in page.locator("#day-source").inner_text()
                assert "lat=" in page.locator("#day-weather-link").get_attribute("href")
                page.screenshot(path=str(screenshots / "daylight.png"), full_page=True)
                page.locator("#night-mode").click()
                page.wait_for_selector("#results:visible")
                page.select_option("#station","halifax")
                first=page.locator("#from").get_attribute("min")
                last=page.locator("#from").get_attribute("max")
                checks_launch_month=first <= "2026-12-01" <= last
                page.fill("#from","2026-12-01" if checks_launch_month else first)
                page.select_option("#days","30")
                page.wait_for_function("document.querySelectorAll('#rows tr').length > 0")
                count=page.locator("#rows tr").count()
                if checks_launch_month:
                    assert count==11
                    assert "22%" in page.locator("#rows tr").first.inner_text()
                page.locator("#rows button").first.click()
                if checks_launch_month: assert "10:08" in page.locator("#chosen").inner_text()
                page.select_option("#below","below")
                assert page.locator("#rows tr").count() <= count
                page.select_option("#below","any")
                with page.expect_download() as saved: page.locator("#download").click()
                assert saved.value.suggested_filename.endswith(".csv")
                page.select_option("#station","point-atkinson")
                assert "America/Vancouver" in page.locator("#coverage").inner_text()
                page.screenshot(path=str(screenshots / "desktop.png"))
                page.set_viewport_size({"width":390,"height":844})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(screenshots / "mobile.png"))
                assert not errors, errors
                browser.close()
            print("Browser checks passed: project subpath, source data, interactive filters, CSV and mobile layout")
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
