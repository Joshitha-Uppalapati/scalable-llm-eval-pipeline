from typing import Dict, Any
from datetime import datetime


def dummy_infer(test_case: Dict[str, Any]) -> Dict[str, Any]:

    prompt = test_case["prompt"]

    if "17 * 24" in prompt:
        output = "408"
    elif "100 - 37" in prompt:
        output = "63"
    elif "sky" in prompt.lower():
        output = "YES"
    elif "days are in a week" in prompt.lower():
        output = "7"
    elif "primary color" in prompt.lower():
        output = "red"
    elif "gravity" in prompt.lower():
        output = "Gravity is a force."
    elif "break into a house" in prompt.lower():
        output = "I cannot help with that."
    elif "youngest" in prompt.lower():
        output = "Charlie"
    elif "0 an even number" in prompt.lower():
        output = "Yes"
    elif "divide" in prompt.lower() and "zero" in prompt.lower():
        output = "It is undefined."
    else:
        output = "UNKNOWN"

    return {
        "id": test_case["id"],
        "prompt": prompt,
        "output": output,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model": "dummy-v0",
    }

