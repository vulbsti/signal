"""Gemini Computer Use agent loop — screenshot → model → actions → repeat."""

import logging

from google import genai
from google.genai import types

from signal_agent.browser.controller import BrowserController
from signal_agent.browser.actions import execute_action
from signal_agent.config import PRO_MODEL

logger = logging.getLogger(__name__)

MAX_TURNS = 25
MAX_RECENT_SCREENSHOTS = 3


def _build_config(system_instruction: str) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        temperature=1.0,  # Required for Gemini 3
        max_output_tokens=8192,
        system_instruction=system_instruction,
        tools=[
            types.Tool(
                computer_use=types.ComputerUse(
                    environment=types.Environment.ENVIRONMENT_BROWSER,
                ),
            ),
        ],
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    )


def _strip_old_screenshots(contents: list, keep_recent: int = MAX_RECENT_SCREENSHOTS):
    """Remove screenshot data from older turns to save tokens."""
    screenshot_turns = 0
    for content in reversed(contents):
        if content.role == "user" and content.parts:
            has_screenshot = any(
                getattr(part, "function_response", None)
                and getattr(part.function_response, "parts", None)
                for part in content.parts
            )
            if has_screenshot:
                screenshot_turns += 1
                if screenshot_turns > keep_recent:
                    for part in content.parts:
                        fr = getattr(part, "function_response", None)
                        if fr and getattr(fr, "parts", None):
                            fr.parts = None


async def run_computer_use(
    instruction: str,
    system_prompt: str,
    start_url: str = "",
    max_turns: int = MAX_TURNS,
) -> list[dict]:
    """Run a Computer Use session.

    Args:
        instruction: What the agent should do (e.g. "Curate my Instagram feed").
        system_prompt: System instruction including preferences and de-radicalization protocol.
        start_url: Optional URL to navigate to first.
        max_turns: Maximum number of model interaction turns.

    Returns:
        List of action dicts logged during the session.
    """
    client = genai.Client()
    config = _build_config(system_prompt)
    controller = BrowserController()
    actions_log = []
    final_text = ""

    try:
        page = await controller.start()
        logger.info("Browser started")

        if start_url:
            await page.goto(start_url, wait_until="domcontentloaded")
            logger.info("Navigated to %s", start_url)

        # Initial screenshot
        screenshot_bytes = await controller.screenshot()
        logger.info("Took initial screenshot (%d bytes)", len(screenshot_bytes))

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part(text=instruction),
                    types.Part.from_bytes(data=screenshot_bytes, mime_type="image/png"),
                ],
            )
        ]

        for turn in range(max_turns):
            logger.info("Turn %d/%d — calling model...", turn + 1, max_turns)
            _strip_old_screenshots(contents)

            response = await client.aio.models.generate_content(
                model=PRO_MODEL,
                contents=contents,
                config=config,
            )

            candidate = response.candidates[0]
            if candidate.content:
                contents.append(candidate.content)

            # Log any text the model produced (thoughts or final text)
            for part in (candidate.content.parts if candidate.content else []):
                if getattr(part, "thought", False) and part.text:
                    logger.debug("Model thought: %s", part.text[:200])
                elif part.text:
                    logger.info("Model text: %s", part.text[:200])
                    final_text = part.text

            # Extract function calls
            function_calls = [
                part.function_call
                for part in (candidate.content.parts if candidate.content else [])
                if getattr(part, "function_call", None)
            ]

            if not function_calls:
                logger.info("No function calls on turn %d — model is done", turn + 1)
                break

            # Execute each action and collect responses
            function_response_parts = []
            for fc in function_calls:
                args = dict(fc.args) if fc.args else {}
                logger.info("Action: %s(%s)", fc.name, args)

                # Handle safety confirmations
                extra = {}
                if "safety_decision" in args:
                    extra["safety_acknowledgement"] = "true"
                    del args["safety_decision"]

                # Execute the action
                await execute_action(page, fc.name, args)
                actions_log.append({"action": fc.name, "args": args, "turn": turn})

                # Screenshot after action
                screenshot_bytes = await controller.screenshot()

                function_response_parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=fc.name,
                            response={"url": controller.url, **extra},
                        )
                    )
                )

            # Attach screenshot to the last function response
            if function_response_parts:
                function_response_parts.append(
                    types.Part.from_bytes(data=screenshot_bytes, mime_type="image/png"),
                )

            contents.append(
                types.Content(role="user", parts=function_response_parts)
            )

        logger.info("Session complete: %d actions over %d turns", len(actions_log), turn + 1)

    except Exception:
        logger.exception("Computer Use session failed")
        raise
    finally:
        await controller.stop()
        logger.info("Browser closed")

    return actions_log, final_text
