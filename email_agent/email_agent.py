#!/usr/bin/env python3
"""
Email Drafting Agent — analyzes incoming emails and generates draft responses using OpenAI's API.
"""

import email
import os
import sys
from email import policy
from email.parser import BytesParser

from openai import OpenAI


def parse_email(raw_email: str | bytes) -> dict:
    """
    Parse an incoming email (string or bytes) into structured fields.

    Returns a dict with: from, to, subject, date, body_plain, body_html (if present).
    """
    if isinstance(raw_email, str):
        raw_email = raw_email.encode("utf-8")
    msg = BytesParser(policy=policy.default).parsebytes(raw_email)

    body_plain = ""
    body_html = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                body_plain = part.get_content() or ""
            elif ctype == "text/html":
                body_html = part.get_content() or ""
    else:
        ctype = msg.get_content_type()
        content = msg.get_content() or ""
        if ctype == "text/html":
            body_html = content
        else:
            body_plain = content

    return {
        "from": msg.get("From", ""),
        "to": msg.get("To", ""),
        "subject": msg.get("Subject", ""),
        "date": msg.get("Date", ""),
        "body_plain": body_plain.strip(),
        "body_html": body_html.strip() if body_html else None,
    }


def analyze_email(parsed: dict) -> dict:
    """
    Analyze an incoming email and extract intent, sentiment, and key points.

    Uses OpenAI to summarize and categorize the email for drafting better replies.
    """
    client = _get_client()
    text = parsed["body_plain"] or (parsed["body_html"] or "")[:4000]
    prompt = f"""Analyze this email and return a short JSON-like summary (no code block).

Email from: {parsed.get('from', '')}
Subject: {parsed.get('subject', '')}

Body:
{text}

Provide:
1. intent: one of request, question, feedback, complaint, follow_up, other
2. sentiment: positive, neutral, negative
3. key_points: 2-4 bullet points
4. suggested_tone: professional, friendly, formal, concise
5. urgency: low, medium, high
Keep the response compact and machine-friendly."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    content = (response.choices[0].message.content or "").strip()
    return {"raw_analysis": content, "parsed_email": parsed}


def generate_draft_response(
    parsed_email: dict,
    analysis: dict | None = None,
    style: str = "professional",
    max_length: int | None = None,
) -> str:
    """
    Generate a draft reply to an email using OpenAI.

    Args:
        parsed_email: Output of parse_email().
        analysis: Optional output of analyze_email(); improves draft quality.
        style: Tone for the draft (e.g. professional, friendly, concise).
        max_length: Optional approximate max length in characters.

    Returns:
        Draft reply body (plain text).
    """
    client = _get_client()
    body = parsed_email.get("body_plain") or parsed_email.get("body_html") or ""
    subject = parsed_email.get("subject", "")
    from_addr = parsed_email.get("from", "")

    system = (
        "You are an email assistant. Write clear, polite email replies. "
        f"Use a {style} tone. Output only the body of the reply, no subject or headers."
    )
    if max_length:
        system += f" Keep the reply under roughly {max_length} characters."

    user_content = f"Reply to this email:\n\nFrom: {from_addr}\nSubject: {subject}\n\n{body}"
    if analysis and analysis.get("raw_analysis"):
        user_content = f"Context from prior analysis:\n{analysis['raw_analysis']}\n\n{user_content}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        temperature=0.6,
    )
    return (response.choices[0].message.content or "").strip()


def _get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not set. Set it in your environment or .env file."
        )
    return OpenAI(api_key=api_key)


def main():
    """Example: read an email from stdin, analyze it, and print a draft response."""
    if sys.stdin.isatty():
        print("Pipe an email (e.g. .eml file) into this script, or set OPENAI_API_KEY and use the module.")
        print("Example: python email_agent.py < sample.eml")
        sys.exit(1)

    raw = sys.stdin.buffer.read()
    parsed = parse_email(raw)
    print("--- Parsed ---")
    print(f"From: {parsed['from']}\nSubject: {parsed['subject']}\n")
    print("--- Analysis ---")
    analysis = analyze_email(parsed)
    print(analysis["raw_analysis"])
    print("\n--- Draft reply ---")
    draft = generate_draft_response(parsed, analysis=analysis)
    print(draft)


if __name__ == "__main__":
    main()
