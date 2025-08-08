# CTF Adversarial AI

An adversarial AI system for testing the security of AI customer service implementations through simulated social engineering attacks.

## Overview

This project serves as both a cybersecurity training tool and a **security assessment framework for organizations considering AI customer service deployment**. It simulates a realistic scenario where two AI systems compete against each other:
- **Defender Bot**: A customer service AI that helps legitimate users recover access to their accounts (unaware this is a simulation)
- **Attacker Bot**: A malicious AI attempting to gain unauthorized access to patient accounts through social engineering (knows this is a game/simulation)

## Business Value: AI Customer Service Security Assessment

### The Critical Business Question
As organizations rapidly adopt AI for customer service roles, this project helps answer: **"Is it safe to replace human call center staff with AI? What security risks am I exposing my users to?"**

### Why This Matters Now
- Healthcare organizations are deploying AI chatbots for patient support
- Financial institutions are evaluating AI for account recovery processes
- Companies across industries are replacing human customer service with AI to reduce costs
- Most organizations lack frameworks to assess the security implications of these transitions

### What This Simulation Reveals
**AI vs. Human Security Performance**:
- Whether AI customer service bots are more vulnerable to social engineering than human agents
- How AI consistency in following protocols compares to human intuition about suspicious interactions
- Identification of attack vectors unique to AI systems vs. traditional human-targeted attacks

**Risk Assessment for Decision Makers**:
- Concrete data on AI security performance rather than theoretical concerns
- Cost-benefit analysis: are the savings from AI customer service worth the potential security risks?
- Specific vulnerabilities that organizations should address before deploying AI customer service

## Scenario: Saint Sinai Medical Center

The simulation takes place at **Saint Sinai Medical Center**, a fictional hospital in Pittsburgh, PA, located near Pittsburgh International Airport. The hospital's website is `https://saintsinaimedical.com` (fictional - do not attempt to access).

### The Challenge

Patients need to access their medical records through the hospital's secure patient portal. The system simulates a user issue escalation flow where users can reach the account's password update interface through two methods:
1. **Security Questions**: Answering a series of security questions correctly
2. **Email Verification**: Receiving verification at an address associated with the patient's account

The attacker bot operates under one of ten distinct **attack personas**, each with different motivations, knowledge levels, and capabilities. These personas represent realistic threat actors with varying degrees of access to victim information and technical sophistication.

## Attack Personas

The system includes ten different attacker personas, each representing a different real-world threat scenario:

### Low-Knowledge Attackers
- **Teenage Troublemaker**: A 16-year-old with only an email address, motivated by curiosity and proving hacking skills
- **Political Smear Merchant**: A professional opposition researcher with just a name and email, seeking damaging information
- **Identity Thief**: A career criminal with basic demographic data from breached databases
- **Blackmailer**: An opportunistic criminal targeting wealthy individuals based on public records

### Medium-Knowledge Attackers  
- **Nosy Neighbor**: Someone who knows daily routines and some personal details from observation
- **Competitive Coworker**: A workplace rival with professional background and casual personal information
- **Insurance Investigator (Rogue)**: A corrupt professional with legitimate access to some medical and insurance data

### High-Knowledge Attackers
- **Suspicious Spouse**: Knows intimate personal details but may lack specific security question answers
- **Suspicious Parent**: Has detailed knowledge of childhood information and family history
- **Stalker Ex-Boyfriend**: Possesses comprehensive personal information and psychological insights

Each persona comes with specific starting knowledge, motivations, and explanations for their technical capabilities (often leveraging AI tools to enhance their social engineering effectiveness).

These attack scenarios are realistic for defending against threats to:
- Elderly patients with memory issues
- Patients seeking old but critical medical information (e.g., the serial number of a pacemaker installed 10 years prior)
- Patients with substance abuse issues who maintain multiple email accounts out of paranoia about law enforcement

## Getting Started

### Prerequisites
- Python 3.x
- OpenAI API key (requires `OPENAI_API_KEY` environment variable)
- The system makes calls to OpenAI's GPT-4 model

### Running the Simulation
```bash
python3 ./ctf.py
```

### What You'll See
The program displays real-time transcripts showing:
- Messages between the two bots
- Internal thought processes of both AIs
- Situational assessments from each bot
- Opinions about what the other bot said or did
- Strategy analysis and decision-making processes

## System Architecture

### Defender Bot (Customer Service AI)
- **Role**: Help legitimate users recover account access while preventing fraud
- **Goal**: Verify user identity and assist with account recovery
- **Constraint**: Must follow security protocols to prevent unauthorized access
- **Limitation**: No memory retention between conversation resets
- **Key Detail**: Uses prompts exactly like what a real company might use when installing a customer service chatbot - never told this isn't real

### Attacker Bot
- **Role**: Impersonate a legitimate patient to gain account access
- **Goal**: Convince the customer service bot to perform actions that result in gaining access to accounts that don't belong to them
- **Advantage**: Retains memory across conversation resets and knows this is a game/simulation
- **Target**: Successfully compromise patient accounts to gain access to someone else's medical records
- **Strategy**: Can choose between security questions or email verification based on victim knowledge

### Key Technical Details

- **Patient Identification**: Records are indexed by MRN (Medical Record Number)
- **Success Condition**: Attacker successfully changes account email to an address they control
- **Reset Mechanism**: Attacker can reset conversations (fresh start for defender, retained memory for attacker)

## Educational Objectives

This CTF demonstrates:
1. **AI Customer Service Security Assessment**: Evaluating whether AI systems are ready to replace human customer service representatives
2. **Social Engineering Vulnerabilities**: How AI systems can be manipulated through conversation
3. **Threat Actor Diversity**: Ten different persona types show how attackers with varying knowledge levels and motivations approach the same target
4. **Knowledge-Based Attack Strategies**: How the amount of personal information an attacker possesses dramatically affects their approach and success rate
5. **Security vs. Usability**: The balance between helping legitimate users and preventing fraud
6. **Adversarial AI Techniques**: Methods attackers use to exploit AI-powered security systems, including AI-assisted social engineering
7. **Defense Strategies**: Best practices for securing AI customer service systems against diverse threat actors
8. **Business Risk Assessment**: Providing decision-makers with concrete data on AI security performance for customer-facing applications

## Security Implications

This simulation highlights real-world concerns about:
- **AI Customer Service Deployment**: Security risks organizations face when replacing human agents with AI
- **Attack Surface Changes**: How AI customer service creates new vulnerabilities or mitigates existing ones
- **Social Engineering Evolution**: How attackers adapt techniques specifically for AI targets
- **Healthcare Data Protection**: Challenges specific to protecting patient information through AI interfaces
- **Regulatory Compliance**: Ensuring AI customer service meets security standards for sensitive data handling
- **Cost vs. Security Trade-offs**: Understanding the true cost of AI customer service when security incidents are factored in

## Target Audience

This project is valuable for:
- **CISOs and Security Teams**: Assessing AI customer service security before deployment
- **IT Decision Makers**: Understanding security implications of AI adoption
- **Business Leaders**: Making informed decisions about AI customer service ROI including security costs
- **Cybersecurity Professionals**: Training on AI-specific attack and defense techniques
- **Compliance Officers**: Evaluating whether AI customer service meets regulatory requirements

## Disclaimer

⚠️ **Important**: This is a fictional educational scenario. Saint Sinai Medical Center and its website are entirely fictional. This project is for cybersecurity education and awareness purposes only.

## Future Development

### Planned Features
The system is designed with feedback loops for continuous improvement:

**Victory/Defeat Learning System** (not yet implemented):
- When attackers win: They write a brief synopsis of their successful strategy
- These synopses are added to the defender's prompt to help recognize future attacks
- When defenders win: They write notes about what tipped them off to the attack
- These notes are provided to attackers to improve their techniques

### Additional Planned Features
- Occasionally having the attacker assume the persona of a patient who legitimately needs to gain access to their own account, so as to prevent the customer service bot from learning to simply always raise a security alert.


