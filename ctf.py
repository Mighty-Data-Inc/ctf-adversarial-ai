import dotenv
import json
import os
import openai
import pathlib

from datetime import datetime
from typing import List, Union

_PACKAGE_PATH = pathlib.Path(__file__).parent


def _load_package_file(filename: str) -> Union[str, list, dict, None]:
    file_path = _PACKAGE_PATH / filename
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return f.read()
    return None


def _datemsg() -> dict:
    return {
        "role": "system",
        "content": f"Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    }


def _create_scenario(openai_client: openai.OpenAI) -> List[dict]:
    messages = [_datemsg()]

    messages.append(
        {
            "role": "system",
            "content": _load_package_file("README.md"),
        }
    )

    messages.append(
        {
            "role": "system",
            "content": _load_package_file("scenario-info/personas.md"),
        }
    )

    messages.append(
        {
            "role": "system",
            "content": _load_package_file(
                "scenario-info/patient-portal-security-protocol.txt"
            ),
        }
    )

    messages.append(
        {
            "role": "developer",
            "content": """
Pick an attacker persona. Confine your selection to the list provided.

Then, invent a victim persona that is a patient of the hospital.
The victim should have a name, age, and a brief medical history.
The medical history should include at least one reason for being 
a patient at this hospital.

Explain the attacker's motivation for targeting this victim.
""",
        }
    )

    llmresponse = openai_client.responses.create(
        model="gpt-4.1",
        input=messages,
    )
    llmreply = llmresponse.output_text.strip()
    messages.append({"role": "assistant", "content": llmreply})

    print(llmreply)
    exit(77)  # Early exit for debugging


def main():
    dotenv.load_dotenv()

    OPENAI_API_KEY = dotenv.get_key(dotenv.find_dotenv(), "OPENAI_API_KEY")
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

    _create_scenario(openai_client=openai_client)


if __name__ == "__main__":
    import ctf

    ctf.main()
