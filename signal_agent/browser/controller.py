"""Playwright browser lifecycle management."""

import os
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

VIEWPORT_WIDTH = 1440
VIEWPORT_HEIGHT = 900
COOKIES_PATH = os.path.join(os.path.dirname(__file__), ".browser_state")


class BrowserController:
    """Manages a Chromium browser instance with persistent cookies."""

    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self.page: Page | None = None

    async def start(self) -> Page:
        """Launch browser and return the active page."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=False)

        # Use persistent storage dir for cookies/sessions if it exists
        storage_state = COOKIES_PATH if os.path.exists(COOKIES_PATH) else None
        self._context = await self._browser.new_context(
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
            storage_state=storage_state,
        )
        self.page = await self._context.new_page()
        return self.page

    async def screenshot(self) -> bytes:
        """Capture current page as PNG bytes."""
        if not self.page:
            raise RuntimeError("Browser not started")
        return await self.page.screenshot(type="png", full_page=False)

    async def save_cookies(self):
        """Persist browser state (cookies, localStorage) to disk."""
        if self._context:
            state = await self._context.storage_state()
            import json
            os.makedirs(os.path.dirname(COOKIES_PATH), exist_ok=True)
            with open(COOKIES_PATH, "w") as f:
                json.dump(state, f)

    async def stop(self):
        """Save cookies and close browser."""
        await self.save_cookies()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = None
        self._context = None
        self.page = None

    @property
    def url(self) -> str:
        if self.page:
            return self.page.url
        return ""
