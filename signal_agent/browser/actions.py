"""Execute Computer Use actions via Playwright, with coordinate denormalization."""

import asyncio
from playwright.async_api import Page

from signal_agent.browser.controller import VIEWPORT_WIDTH, VIEWPORT_HEIGHT

# The model uses a normalized 0-999 coordinate grid.
GRID_SIZE = 1000


def denormalize_x(x: int) -> int:
    return int(x / GRID_SIZE * VIEWPORT_WIDTH)


def denormalize_y(y: int) -> int:
    return int(y / GRID_SIZE * VIEWPORT_HEIGHT)


async def execute_action(page: Page, action_name: str, args: dict) -> None:
    """Execute a single Computer Use action on the Playwright page."""

    if action_name == "click_at":
        ax = denormalize_x(args["x"])
        ay = denormalize_y(args["y"])
        await page.mouse.click(ax, ay)

    elif action_name == "hover_at":
        ax = denormalize_x(args["x"])
        ay = denormalize_y(args["y"])
        await page.mouse.move(ax, ay)

    elif action_name == "type_text_at":
        ax = denormalize_x(args["x"])
        ay = denormalize_y(args["y"])
        await page.mouse.click(ax, ay)
        if args.get("clear_before_typing", True):
            await page.keyboard.press("Control+a")
            await page.keyboard.press("Delete")
        await page.keyboard.type(args["text"], delay=30)
        if args.get("press_enter", True):
            await page.keyboard.press("Enter")

    elif action_name == "scroll_document":
        direction = args.get("direction", "down")
        key = {
            "down": "PageDown",
            "up": "PageUp",
            "left": "Home",
            "right": "End",
        }.get(direction, "PageDown")
        await page.keyboard.press(key)

    elif action_name == "scroll_at":
        ax = denormalize_x(args["x"])
        ay = denormalize_y(args["y"])
        direction = args.get("direction", "down")
        magnitude = args.get("magnitude", 800)
        delta = int(magnitude / GRID_SIZE * VIEWPORT_HEIGHT)
        if direction == "up":
            delta = -delta
        elif direction in ("left", "right"):
            delta_x = int(magnitude / GRID_SIZE * VIEWPORT_WIDTH)
            if direction == "left":
                delta_x = -delta_x
            await page.mouse.move(ax, ay)
            await page.mouse.wheel(delta_x, 0)
            return
        await page.mouse.move(ax, ay)
        await page.mouse.wheel(0, delta)

    elif action_name == "navigate":
        await page.goto(args["url"], wait_until="domcontentloaded")

    elif action_name == "go_back":
        await page.go_back()

    elif action_name == "go_forward":
        await page.go_forward()

    elif action_name == "search":
        await page.goto("https://www.google.com", wait_until="domcontentloaded")

    elif action_name == "open_web_browser":
        pass  # Browser is already open

    elif action_name == "wait_5_seconds":
        await asyncio.sleep(5)

    elif action_name == "key_combination":
        keys = args.get("keys", "")
        await page.keyboard.press(keys)

    elif action_name == "drag_and_drop":
        sx = denormalize_x(args["x"])
        sy = denormalize_y(args["y"])
        dx = denormalize_x(args["destination_x"])
        dy = denormalize_y(args["destination_y"])
        await page.mouse.move(sx, sy)
        await page.mouse.down()
        await page.mouse.move(dx, dy, steps=10)
        await page.mouse.up()

    # Small delay after every action to let the page settle
    await asyncio.sleep(0.5)
