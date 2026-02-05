"""
Utility functions for browser automation.
Reusable across different automation scripts.
"""

from playwright.sync_api import Page
import time


def create_status_overlay(page: Page) -> None:
    """Create an on-screen status overlay for visual feedback."""
    page.evaluate("""
        const box = document.createElement('div');
        box.id = 'rpa-status';
        box.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 15px 20px;
            background: rgba(0, 0, 0, 0.9);
            color: #00ff00;
            z-index: 99999;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            border-radius: 8px;
            border: 2px solid #00ff00;
            box-shadow: 0 0 15px rgba(0,255,0,0.3);
            min-width: 300px;
        `;
        box.innerText = 'RPA Automation Starting...';
        document.body.appendChild(box);
    """)


def update_status(page: Page, msg: str, step: str = "") -> None:
    """Update the on-screen status overlay and print to console."""
    safe_msg = str(msg).replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
    if step:
        safe_msg = f"{step}\\n{safe_msg}"
    try:
        page.evaluate(f"document.getElementById('rpa-status').innerText = '{safe_msg}';")
    except:
        pass
    print(f"  {msg}")


def get_viewport_center(page: Page) -> tuple:
    """Get the center coordinates of the viewport."""
    viewport = page.viewport_size or {"width": 1920, "height": 1080}
    return viewport['width'] // 2, viewport['height'] // 2


def click_chart(page: Page, x: int = 500, y: int = 400) -> None:
    """Click on the chart to ensure focus."""
    page.mouse.click(x, y)
    time.sleep(0.5)


def safe_click(page: Page, selector: str, timeout: int = 3000) -> bool:
    """Safely click an element, return False if not found."""
    try:
        page.click(selector, timeout=timeout)
        return True
    except:
        return False


def wait_and_type(page: Page, text: str, delay: int = 100) -> None:
    """Type text with a delay between keystrokes."""
    page.keyboard.type(text, delay=delay)
