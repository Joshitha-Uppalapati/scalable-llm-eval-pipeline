# NOTE:
# This file represents an early exploration before the pipeline
# structure stabilized. It is kept here for reference.


import os
import time
from typing import Dict, Optional

import openai


MAX_RETRIES = 3
REQUEST_TIMEOUT = 30


def infer(prompt: str) -> Dict[str, Optional[int | str]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    openai.api_key = api_key

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            start = time.time()
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                timeout=REQUEST_TIMEOUT,
            )
            latency_ms = int((time.time() - start) * 1000)

            choice = resp.choices[0].message.content
            usage = resp.usage or {}

            return {
                "output": choice,
                "model": resp.model,
                "latency_ms": latency_ms,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
            }
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(1)

    raise RuntimeError(f"LLM call failed after {MAX_RETRIES} retries: {last_error}")
