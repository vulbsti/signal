"""Playwright browser lifecycle management using Microsoft Edge."""

import os
from playwright.async_api import async_playwright, BrowserContext, Page

VIEWPORT_WIDTH = 1440
VIEWPORT_HEIGHT = 900

# Edge user data directory — uses the real Edge profile with existing logins
_EDGE_USER_DATA = os.path.expanduser("~/.config/microsoft-edge")
# Separate persistent dir for Playwright to avoid locking Edge's profile
_PERSISTENT_DIR = os.path.join(os.path.dirname(__file__), ".edge_profile")


class BrowserController:
    """Manages a Microsoft Edge browser instance with the user's real profile."""

    def __init__(self):
        self._playwright = None
        self._context: BrowserContext | None = None
        self.page: Page | None = None

    async def start(self) -> Page:
        """Launch Edge and return the active page."""
        self._playwright = await async_playwright().start()

        os.makedirs(_PERSISTENT_DIR, exist_ok=True)

        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=_PERSISTENT_DIR,
            channel="msedge",
            headless=False,
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
            args=["--disable-blink-features=AutomationControlled"],
        )

        # Use existing page or open a new one
        if self._context.pages:
            self.page = self._context.pages[0]
        else:
            self.page = await self._context.new_page()

        return self.page

    async def screenshot(self) -> bytes:
        """Capture current page as PNG bytes."""
        if not self.page:
            raise RuntimeError("Browser not started")
        return await self.page.screenshot(type="png", full_page=False)

    async def stop(self):
        """Close browser context."""
        if self._context:
            await self._context.close()
        if self._playwright:
            await self._playwright.stop()
        self._context = None
        self.page = None

    @property
    def url(self) -> str:
        if self.page:
            return self.page.url
        return ""
