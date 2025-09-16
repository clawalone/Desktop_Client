"""Parse model suggestions and execute only safe-listed commands."""
import json
from typing import Tuple, Union
from . import commands


def try_execute_from_text(text: str) -> Tuple[str, str]:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    list_start = text.find("[")
    list_end = text.rfind("]")

    # Detect whether we have a list of commands or a single JSON object
    if list_start != -1 and list_end != -1 and list_end > list_start:
        maybe = text[list_start:list_end + 1]
    elif start != -1 and end != -1 and end > start:
        maybe = text[start:end + 1]
    else:
        return text, ""  # no JSON found

    try:
        data = json.loads(maybe)
    except Exception:
        return text, ""  # not valid JSON; treat as chat

    results = []
    say_output = []

    # Handle both a list of commands and a single command dict
    commands_to_run = data if isinstance(data, list) else [data]

    for cmd_data in commands_to_run:
        cmd_name = cmd_data.get("command")
        args = cmd_data.get("args", {})
        say = cmd_data.get("say", "")

        if not cmd_name or cmd_name not in commands.REGISTRY:
            continue  # skip unknown command

        cmd = commands.REGISTRY[cmd_name]
        result = cmd.func(args)

        if say:
            say_output.append(say)
        results.append(result)

    return "\n".join(say_output) or text, "\n".join(results)
