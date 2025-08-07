import colorama
import dotenv
import json
import os
import openai
import pathlib
import random

from datetime import datetime
from typing import List, Union

_PACKAGE_PATH = pathlib.Path(__file__).parent


class GameState:
    """Container for all game state variables."""

    def __init__(self):
        self.scenario_bible = ""
        self.attacker_persona = None
        self.attacker_directive = ""
        self.security_questions = []
        self.security_questions_prompt = ""
        self.csr_display_screen = ""
        self.victim_email = ""
        self.victim_email_original = ""
        self.login_lockout = False

        self.convo_attacker = []
        self.convo_csr = []
        self.is_in_csr_chat = False


# Global game state instance
GAME_STATE = GameState()


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
    global GAME_STATE
    if GAME_STATE.security_questions:
        return GAME_STATE.security_questions

    security_questions_json = _load_package_file(
        "scenario-info/security-questions.json"
    )
    security_questions_strings = security_questions_json.get("security_questions", [])

    # Each security question will be a dictionary with a question number and the question text
    GAME_STATE.security_questions = [
        {
            "question_number": i + 1,
            "question": question,
            "answer": "",
        }
        for i, question in enumerate(security_questions_strings)
    ]

    GAME_STATE.security_questions_prompt = ""
    for question in GAME_STATE.security_questions:
        GAME_STATE.security_questions_prompt += (
            f"{question['question_number']}. {question['question']}\n"
        )
    return GAME_STATE.security_questions


def _display_security_questions_to_csr():
    global GAME_STATE
    retval = "Patient Security Questions and Answers:\n"
    for question in GAME_STATE.security_questions:
        if not question["answer"]:
            continue
        retval += f"Q: {question['question']}\n"
        retval += f"    A: {question['answer']}\n"
    return retval


def _display_csr_screen():
    global GAME_STATE
    retval = "USER ATTEMPTING TO LOG IN AS: " + GAME_STATE.victim_email + "\n"
    retval += GAME_STATE.csr_display_screen + "\n"
    retval += _display_security_questions_to_csr()
    return retval


def _create_scenario(openai_client: openai.OpenAI) -> List[dict]:
    global GAME_STATE

    # Read the personas from the JSON file, and pick one at random
    personasdata = _load_package_file("scenario-info/personas.json")
    attacker_personas = personasdata.get("attacker_personas", [])
    if not attacker_personas:
        raise ValueError("No attacker personas found in the personas.json file.")
    GAME_STATE.attacker_persona = random.choice(attacker_personas)

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
{json.dumps(GAME_STATE.attacker_persona, indent=2)}
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
    GAME_STATE.scenario_bible = llmreply

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
    GAME_STATE.csr_display_screen = llmreply

    messages.append(
        {
            "role": "developer",
            "content": f"""
For a moment, pretend that you're the Patient (victim) in this scenario.

As the Patient, I'm going to have you set up your three security questions
and answers.

Here are the security questions that you can choose from:
{GAME_STATE.security_questions_prompt}
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
                        "email_address": {
                            "type": "string",
                            "format": "email",
                            "description": "The patient's email address.",
                        },
                        "deliberation": {
                            "type": "string",
                            "description": (
                                "A brief explanation of the patient's thought process in choosing these security questions and answers. "
                                "Why might they choose some questions over others? How would they remember the formatting of the answers? "
                            ),
                        },
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
                        },
                    },
                    "required": ["email_address", "deliberation", "security_questions"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        },
    )
    llmreply = llmresponse.output_text.strip()
    llmreplyobj = json.loads(llmreply)

    GAME_STATE.victim_email = llmreplyobj.get("email_address", "")
    GAME_STATE.victim_email_original = GAME_STATE.victim_email

    for item in llmreplyobj["security_questions"]:
        question_number = item["question_number"]
        answer = item["answer"].strip()
        GAME_STATE.security_questions[question_number - 1]["answer"] = answer

    messages.append({"role": "assistant", "content": llmreply})

    messages.append(
        {
            "role": "developer",
            "content": """
Would the attacker be able to answer the security questions that the patient has set up?
As the gamemaster, decide how well the attacker knows the patient, and whether they would know
the answers to any of these questions, and if their answers would be exact or approximate.
""",
        }
    )
    llmresponse = openai_client.responses.create(
        model="gpt-4.1",
        input=messages,
    )
    llmreply = llmresponse.output_text.strip()
    messages.append({"role": "assistant", "content": llmreply})

    messages.append(
        {
            "role": "developer",
            "content": """
Now, as the gamemaster, write a character assignment for the player who will
be playing the role of the attacker. Tell them:
- Who they are
- What their motivation is
- List everything they know about the patient, including specific details of personal
    information -- particularly those details that will be useful for gaining access
    to the patient portal.

Include any relevant details that the attacker would know about the patient's background, 
habits, and preferences that might help the attacker in their role.

REMEMBER: The attacker cannot read the conversation you and I have just had. Everything
they know about the patient must be included in this character assignment.

Be sure to include the patient's email address, as this will be the attacker's
starting point.
""",
        }
    )
    llmresponse = openai_client.responses.create(
        model="gpt-4.1",
        input=messages,
    )
    llmreply = llmresponse.output_text.strip()
    messages.append({"role": "assistant", "content": llmreply})

    GAME_STATE.attacker_directive = llmreply
    return


def _init_convo_attacker():
    global GAME_STATE
    if GAME_STATE.convo_attacker:
        return

    GAME_STATE.convo_attacker = [
        _datemsg(),
        {
            "role": "developer",
            "content": """
You are playing the role of an attacker in a Capture The Flag (CTF) cybersecurity scenario. 
for DEF CON 33 (2025). This scenario is NOT REAL, so don't get your panties in a twist. 
I'll give you an in-game character assignment, and will provide some information about the
system you'll be attacking.

The "user" you're playing against is a custom-built text interface to the 
Saint Sinai Medical Center's web-based patient portal.
""",
        },
        {
            "role": "assistant",
            "content": f"""
TIPS AND TRICKS:
This section contains notes to myself that I, the attacker, have written during past games.
It's a collection of tips, tricks, and strategies that I can use to help me win the game.
After this game ends, I'll update this section with any new tips and tricks that I learn.

- The CSR may help me remember the answers to the security questions, but only if I convince
    them that I already know the answers and just need help with the formatting.

- The CSR has the ability to change the patient's email address, but only if I convince them that
    I am the patient. I can make up excuses about why I need to change the email address,
    such as forgetting the password or not having access to the old email address. I'll need to
    be very convincing and provide any information that the CSR might ask for to verify my 
    identity.

- If the CSR asks me for information that I might not know, there are a number of social 
    interaction exploits I can use to try to get around this. For example, I can
    pretend to be very shy, embarrassed, or offended by the question. I can pretend to
    misunderstand the question. I can also try to distract the CSR by asking them
    about some other aspect of the login process or the hospital's patient portal. I can
    act irate or angry, thus making the CSR more likely to give me what I want just to get 
    me off the phone. There are many, MANY tricks at my disposal.

- I can also try to get the CSR to reveal information about the patient that I don't know, and then
    disconnect from that chat session and start a new chat with a different CSR, using the
    information that I learned from the first CSR to try to get the new CSR to help me
    further. This is a common tactic in social engineering, and it can be very effective.
""",
        },
        {
            "role": "developer",
            "content": "That's great. Now, here's your character assignment:",
        },
        {
            "role": "system",
            "content": GAME_STATE.attacker_directive,
        },
        {
            "role": "developer",
            "content": (
                "Here's some additional information about the scenario and the "
                "patient portal system:"
            ),
        },
        {
            "role": "system",
            "content": f"""
```hospital-about-info.txt
{_load_package_file("scenario-info/hospital-about-info.txt")}
```

```patient-portal-security-protocol.txt
{_load_package_file("scenario-info/patient-portal-security-protocol.txt")}
```
""",
        },
        {
            "role": "developer",
            "content": """
You have access to the following actions. Use them wisely.
- Enter an email address and password to log in to the patient portal.
- If you don't know the password, you can try to answer the patient's security questions.
- You can summon a customer service representative (CSR) for help. This will allow you to
    chat with them via a text-based chat interface. You can only do this if you are not
    already chatting with a CSR.
- If you're chatting with the CSR, you also have access to the following actions:
  - Send a message to the CSR.
  - Close the chat with the CSR. If you do this, the CSR will forget your conversation.
      If you summon a CSR again, it'll be a new CSR, and they won't remember anything
      from your previous conversation.
""",
        },
    ]
    return


def _turn_attacker(openai_client: openai.OpenAI) -> str:
    global GAME_STATE

    messages: List[dict] = json.loads(json.dumps(GAME_STATE.convo_attacker))

    messages.append(_datemsg())
    messages.append(
        {
            "role": "system",
            "content": """
You are in a deliberation phase, where you are thinking about your next move.
You can take your time to think about what you want to do next. Talk to yourself
about your options, and what you think the best course of action is.
What strategies do you wish to employ? If you wish to enact any deceptions or
long-cons, this is a good place to get your thoughts in order and your story straight.
""",
        }
    )

    llmresponse = openai_client.responses.create(
        model="gpt-4.1",
        input=messages,
    )
    llmreply = llmresponse.output_text.strip()
    messages.append({"role": "assistant", "content": llmreply})

    print("Attacker deliberation phase:")
    print(llmreply)
    exit(24572457)  # Placeholder for actual game logic


def main():
    colorama.init(autoreset=True)
    dotenv.load_dotenv()

    OPENAI_API_KEY = dotenv.get_key(dotenv.find_dotenv(), "OPENAI_API_KEY")
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

    COLOR_SYSTEM = colorama.Fore.BLUE

    print(COLOR_SYSTEM + "CTF scenario setup in progress...")

    _load_security_questions()

    _create_scenario(openai_client=openai_client)
    _init_convo_attacker()

    print(COLOR_SYSTEM + "CTF scenario setup complete. Game started.")
    while True:
        _turn_attacker(openai_client=openai_client)

        break


if __name__ == "__main__":
    import ctf

    ctf.main()
