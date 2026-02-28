# Email Drafting Agent

A simple agent that analyzes incoming emails and generates draft replies using OpenAI's API.

## Features

- **Parse emails** — Extract from, to, subject, date, and body (plain text or HTML) from raw email content
- **Analyze emails** — Use OpenAI to detect intent, sentiment, key points, and suggested tone
- **Generate drafts** — Produce reply drafts with configurable style and optional length limit

## Requirements

- Python 3.10+
- OpenAI API key

## Setup

### 1. Create a virtual environment (recommended)

```bash
cd email_agent
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your OpenAI API key

Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys), then:

**Option A — Environment variable**

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**Option B — `.env` file (load with `python-dotenv` if you add it)**

Create a `.env` file in the `email_agent` directory:

```
OPENAI_API_KEY=sk-your-key-here
```

Do not commit `.env` or expose your API key in code.

## Usage

### As a module

```python
from email_agent.email_agent import parse_email, analyze_email, generate_draft_response

# Parse an email (string or bytes)
raw = open("inbox_message.eml", "rb").read()
parsed = parse_email(raw)

# Analyze it
analysis = analyze_email(parsed)

# Generate a draft reply
draft = generate_draft_response(
    parsed,
    analysis=analysis,
    style="professional",   # or "friendly", "concise", "formal"
    max_length=500,         # optional
)
print(draft)
```

### From the command line

Pipe a raw email (e.g. an `.eml` file) into the script. It will parse, analyze, and print a draft reply:

```bash
python email_agent.py < sample.eml
```

### Sample email for testing

Save this as `sample.eml` and run:

```bash
python email_agent.py < sample.eml
```

```
From: colleague@example.com
To: you@example.com
Subject: Meeting follow-up

Hi,

Could we schedule 30 minutes next week to go over the Q2 metrics? Also, do you have the updated dashboard link?

Thanks!
```

## API overview

| Function | Description |
|----------|-------------|
| `parse_email(raw_email)` | Parse raw email string/bytes into a dict (from, to, subject, date, body_plain, body_html). |
| `analyze_email(parsed)` | Call OpenAI to analyze intent, sentiment, key points, and suggested tone. Returns dict with `raw_analysis` and `parsed_email`. |
| `generate_draft_response(parsed_email, analysis=None, style="professional", max_length=None)` | Generate a draft reply body. Optionally pass `analysis` for better context. |

## License

Use as you like. Ensure you comply with [OpenAI's usage policies](https://openai.com/policies/usage-policies) when using the API.
