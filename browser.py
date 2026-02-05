"""
Browser management functions.
Handles browser launch and context creation.
"""

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from config import CONFIG


def launch_browser(playwright) -> Browser:
    """Launch a Chromium browser with configured settings."""
    try:
        browser = playwright.chromium.launch(
            headless=False,
            channel="chrome",
            args=CONFIG["browser_args"]
        )
    except:
        # Fallback if Chrome channel not available
        browser = playwright.chromium.launch(
            headless=False,
            args=CONFIG["browser_args"]
        )
    return browser


def create_context(browser: Browser) -> BrowserContext:
    """Create a browser context with no viewport restrictions."""
    return browser.new_context(viewport=None)


def create_page(context: BrowserContext) -> Page:
    """Create a new page in the context."""
    return context.new_page()


def setup_browser(playwright) -> tuple:
    """
    Complete browser setup.
    Returns: (browser, context, page)
    """
    browser = launch_browser(playwright)
    context = create_context(browser)
    page = create_page(context)
    return browser, context, page
