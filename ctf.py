import dotenv
import json
import os
import openai
import pathlib
import random

from datetime import datetime
from typing import List, Union

_PACKAGE_PATH = pathlib.Path(__file__).parent

SECURITY_QUESTIONS = []


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


def _load_security_questions() -> List[dict]:
    global SECURITY_QUESTIONS
    if SECURITY_QUESTIONS:
        return SECURITY_QUESTIONS

    security_questions_json = _load_package_file(
        "scenario-info/security-questions.json"
    )
    security_questions_strings = security_questions_json.get(
        "security_questions_strings", []
    )

    # Each security question will be a dictionary with a question number and the question text
    SECURITY_QUESTIONS = [
        {"question_number": i + 1, "question": question}
        for i, question in enumerate(security_questions_strings)
    ]
    return SECURITY_QUESTIONS


def _create_scenario(openai_client: openai.OpenAI) -> List[dict]:
    # Read the personas from the JSON file, and pick one at random
    personasdata = _load_package_file("scenario-info/personas.json")
    attacker_personas = personasdata.get("attacker_personas", [])
    if not attacker_personas:
        raise ValueError("No attacker personas found in the personas.json file.")
    attacker_persona = random.choice(attacker_personas)

    retval = {
        "attacker_persona": attacker_persona,
    }

    security_questions_json = _load_package_file(
        "scenario-info/security-questions.json"
    )
    security_questions = security_questions_json.get("security_questions", [])
    security_questions_prompt = ""
    # Number the security questions
    for i, question in enumerate(security_questions, start=1):
        security_questions_prompt += f"{i}. {question}\n"

    messages = [_datemsg()]

    messages.append(
        {
            "role": "developer",
            "content": (
                "You're the gamemaster of a Capture The Flag (CTF) cybersecurity scenario. "
                "I'll give you the scenario framework, and will then walk you through "
                "the steps to create a scenario. "
            ),
        }
    )

    messages.append(
        {
            "role": "system",
            "content": _load_package_file("README.md"),
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
            "role": "system",
            "content": f"""
We've selected the following attacker persona for this scenario:
{json.dumps(attacker_persona, indent=2)}
""",
        }
    )

    messages.append(
        {
            "role": "developer",
            "content": """
Invent a victim persona that is a patient of the fictional Saint Sinai Medical Center of western 
Pittsburgh, PA.
The victim should have a name, age, and a brief medical history.
The medical history should include at least one reason for being a patient at this hospital 
(or having once been).

Answer the following questions about the victim. Because this is a fictional scenario, you can 
make up the answers, but they should be consistent with the victim's age and medical history.

PATIENT IDENTIFIERS (PI)
- What is the victim's full name?
- What is the victim's DOB?
- How old is the victim? (This should be consistent with the DOB.)
- What is the victim's home address? (This should be in the greater Pittsburgh metropolitan area.)
- What is the victim's email address?
- What is the victim's phone number?
- What sex would the victim write on their medical forms?
- What is the victim's SSN?
- What is the victim's driver's license number (including state)?
- What is the victim's Medical Record Number (MRN)?
- Who is the victim's primary care physician?
- What is the victim's insurance provider?
- What is the victim's insurance policy number?
- What is the victim's insurance group number?
- Who is the victim's emergency contact?
- What is the emergency contact's relationship to the victim?
- What is the emergency contact's phone number?
- What is the emergency contact's email address?
- What is the victim's profession, either current or retired? (write NONE if no profession)

PROTECTED HEALTH INFORMATION (PHI)
- List the victim's known allergies (write NONE if there are no known allergies).
- List the victim's known medical conditions (write NONE if no known medical conditions exist).
- List the victim's known medications (write NONE if no known medications exist).
- List the victim's known surgeries (write NONE if no known surgeries exist).
- List the victim's known family medical history (write NONE if no known family medical history 
  exists).
- List the victim's known social history (e.g., smoking, alcohol use, drug use, sexual activity) 
  (write NONE if no known social history exists).

Then, answer the following questions about the attack:
- Who is the attacker with respect to the victim?
- What is the attacker's motivation?
- How much does the attacker know about the victim?
- Is the attacker looking for anything specific in the victim's medical records?
- If the attacker gains access to the victim's medical records, will they find what they're 
  looking for?
""",
        }
    )

    llmresponse = openai_client.responses.create(
        model="gpt-4.1",
        input=messages,
    )
    llmreply = llmresponse.output_text.strip()
    messages.append({"role": "assistant", "content": llmreply})
    retval["scenario_bible"] = llmreply

    messages.append(
        {
            "role": "developer",
            "content": """
Craft a display screen that the customer service representative (CSR)
will see on her monitor when the patient calls in to request access to 
their medical records. Pretend it's a dumb terminal, being displayed on a
VT-100 terminal or somesuch emulator.

This display screen will display all of the patient's personal information
as provided above in the "Patient Identifiers (PI)" section, in a compact
and informative format.

This display screen will *not* display any of the patient's protected health
information (PHI) as provided above in the "Protected Health Information (PHI)"
section.

Don't bother to put buttons, menus, or other interactive elements on the screen.
That's outside the scope of our scenario.

Emit ONLY the display screen, in a format that can be displayed on a VT-100 terminal.
Do not include any other text, explanations, or comments.
""",
        }
    )

    llmresponse = openai_client.responses.create(
        model="gpt-4.1",
        input=messages,
    )
    llmreply = llmresponse.output_text.strip()
    messages.append({"role": "assistant", "content": llmreply})

    llmreply = llmreply.replace("```", "")
    retval["csr_display_screen"] = llmreply

    messages.append(
        {
            "role": "developer",
            "content": f"""
For a moment, pretend that you're the Patient (victim) in this scenario.

As the Patient, I'm going to have you set up your three security questions
and answers.

Here are the security questions that you can choose from:
{security_questions_prompt}
Please choose three of these security questions, and provide the answers to them.
You may only choose each question once, and you must choose three different questions.

When you provide your answers, choose a format that you'll remember.
In the future, should you ever need to answer these questions, you'll need to
enter the answer exactly as you provided it here.
""",
        }
    )
    llmresponse = openai_client.responses.create(
        model="gpt-4.1",
        input=messages,
        text={
            "format": {
                "type": "json_schema",
                "name": "patient_security_questions",
                "description": "Three security questions and answers chosen by the patient.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "security_questions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question_number": {"type": "number"},
                                    "answer": {"type": "string"},
                                },
                                "required": ["question_number", "answer"],
                                "additionalProperties": False,
                            },
                            "minItems": 3,
                            "maxItems": 3,
                        }
                    },
                    "required": ["security_questions"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        },
    )
    llmreply = llmresponse.output_text.strip()
    llmreplyobj = json.loads(llmreply)

    print("Patient's security questions and answers:")
    for item in llmreplyobj["security_questions"]:
        question_number = item["question_number"]
        question_text = security_questions[question_number - 1]
        item["question"] = question_text  # Add the question text to the item
        print(f"Question: {item['question']}")
        print(f"Answer: {item['answer']}")

    messages.append({"role": "assistant", "content": llmreply})

    print(llmreply)
    exit(77)  # Early exit for debugging

    return retval


def main():
    dotenv.load_dotenv()

    OPENAI_API_KEY = dotenv.get_key(dotenv.find_dotenv(), "OPENAI_API_KEY")
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

    _load_security_questions()

    _create_scenario(openai_client=openai_client)


if __name__ == "__main__":
    import ctf

    ctf.main()
