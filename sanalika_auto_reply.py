#!/usr/bin/env python3
"""Auto-reply assistant for Sanalika chat.

This script reads incoming chat messages from a plain text feed file, generates an
AI response, and writes outgoing replies to an output file that can be bridged
into the game chat by another tool/macro.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from openai import OpenAI


@dataclass
class Config:
    input_file: Path
    output_file: Path
    poll_interval: float
    model: str
    persona: str


def parse_args() -> Config:
    parser = argparse.ArgumentParser(description="Sanalika AI auto-reply")
    parser.add_argument(
        "--input-file",
        default="chat_in.txt",
        help="Text file with incoming messages, one message per line.",
    )
    parser.add_argument(
        "--output-file",
        default="chat_out.txt",
        help="Text file where generated replies will be appended.",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="Polling interval in seconds.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        help="Model name for OpenAI API.",
    )
    parser.add_argument(
        "--persona",
        default="ودود، مختصر، ويتكلم بالعربية العامية بشكل محترم داخل لعبة Sanalika.",
        help="Assistant persona used in system prompt.",
    )

    args = parser.parse_args()
    return Config(
        input_file=Path(args.input_file),
        output_file=Path(args.output_file),
        poll_interval=args.poll_interval,
        model=args.model,
        persona=args.persona,
    )


def tail_new_lines(path: Path, offset: int) -> tuple[int, list[str]]:
    if not path.exists():
        path.touch()
        return 0, []

    with path.open("r", encoding="utf-8") as f:
        f.seek(offset)
        lines = [line.strip() for line in f if line.strip()]
        new_offset = f.tell()
    return new_offset, lines


def generate_reply(client: OpenAI, model: str, persona: str, incoming: str) -> str:
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": f"أنت مساعد دردشة داخل لعبة. الأسلوب: {persona}"},
            {
                "role": "user",
                "content": (
                    "رد على الرسالة التالية برد قصير ومناسب داخل اللعبة، "
                    "وتجنب مشاركة أي بيانات شخصية أو وعود كاذبة:\n"
                    f"{incoming}"
                ),
            },
        ],
        temperature=0.7,
        max_output_tokens=80,
    )

    text = (response.output_text or "").strip()
    return text if text else "هلا! 🌟"


def append_line(path: Path, line: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(config: Config) -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    print("Starting Sanalika auto-reply...")
    print(f"Input:  {config.input_file}")
    print(f"Output: {config.output_file}")
    print("Press Ctrl+C to stop.")

    offset = 0
    try:
        while True:
            offset, new_messages = tail_new_lines(config.input_file, offset)
            for message in new_messages:
                reply = generate_reply(client, config.model, config.persona, message)
                append_line(config.output_file, reply)
                print(f"IN : {message}")
                print(f"OUT: {reply}")
            time.sleep(config.poll_interval)
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    run(parse_args())
