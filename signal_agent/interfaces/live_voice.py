"""Gemini Live API voice briefing — reads digest aloud."""

import asyncio
import wave
import os
import struct

from google import genai
from google.genai import types

AUDIO_MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"
SAMPLE_RATE = 24000  # Output audio is 24kHz PCM
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory_data")


async def generate_voice_briefing(
    digest_text: str,
    voice: str = "Kore",
    output_file: str = "",
) -> str:
    """Generate a voice briefing from digest text using Gemini Live API.

    Args:
        digest_text: The digest content to read aloud.
        voice: Voice name (Kore, Puck, Charon, Fenrir, Aoede, Leda, Orus, Zephyr).
        output_file: Path to save WAV file. If empty, saves to memory_data/briefing.wav.

    Returns:
        Path to the generated WAV file.
    """
    if not output_file:
        output_file = os.path.join(OUTPUT_DIR, "briefing.wav")

    client = genai.Client()

    config = {
        "response_modalities": ["AUDIO"],
        "system_instruction": (
            "You are a concise, professional news briefer. "
            "Read the following digest aloud clearly and naturally. "
            "Be brief — summarize each item in 1-2 sentences. "
            "Start with a quick overview of how many items and key topics."
        ),
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {
                    "voice_name": voice,
                }
            }
        },
    }

    audio_chunks = []

    async with client.aio.live.connect(model=AUDIO_MODEL, config=config) as session:
        await session.send_client_content(
            turns=types.Content(
                role="user",
                parts=[types.Part(text=f"Read this digest aloud:\n\n{digest_text}")],
            )
        )

        async for msg in session.receive():
            if msg.server_content and msg.server_content.model_turn:
                for part in msg.server_content.model_turn.parts:
                    if part.inline_data and part.inline_data.data:
                        audio_chunks.append(part.inline_data.data)
            if msg.server_content and msg.server_content.turn_complete:
                break

    # Combine and save as WAV
    pcm_data = b"".join(audio_chunks)
    _save_wav(output_file, pcm_data, SAMPLE_RATE)

    return output_file


def _save_wav(path: str, pcm_data: bytes, sample_rate: int):
    """Save raw PCM data as a WAV file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)


def play_audio(wav_path: str):
    """Play a WAV file using pyaudio if available, otherwise system player."""
    try:
        import pyaudio

        wf = wave.open(wav_path, "rb")
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
        )
        chunk = 1024
        data = wf.readframes(chunk)
        while data:
            stream.write(data)
            data = wf.readframes(chunk)
        stream.close()
        p.terminate()
        wf.close()
    except ImportError:
        # Fallback: use system audio player
        import subprocess

        subprocess.run(["xdg-open", wav_path], check=False)


async def briefing_from_digest(digest_text: str, voice: str = "Kore") -> str:
    """Generate and play a voice briefing. Returns path to WAV file."""
    path = await generate_voice_briefing(digest_text, voice=voice)
    play_audio(path)
    return path


if __name__ == "__main__":
    sample = (
        "Today's digest: 5 items from HN and Reddit.\n"
        "1. GPT-5.2 derives a new result in theoretical physics (Score: 92)\n"
        "2. Show HN: SQL-tap - Real-time SQL traffic viewer (Score: 85)\n"
        "3. Understanding the Go Compiler (Score: 78)\n"
    )
    asyncio.run(briefing_from_digest(sample))
