import os
import re
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def trim_transcript(text, max_chars=4000):
    return text[:max_chars]

def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {}

def llm_extract(transcript):

    prompt = f"""
Extract structured configuration from the following call transcript.

Rules:
- Return ONLY valid JSON
- No explanations
- No markdown
- No text outside JSON
- If a field is not explicitly mentioned return null
- Do NOT infer missing configuration
- Do NOT hallucinate

Fields:
business_hours:
    days
    start
    end
    timezone

services_supported

emergency_definition

emergency_routing_rules:
    transfer_required
    transfer_target
    timeout_seconds

non_emergency_routing_rules:
    collect_details
    followup_during_business_hours

call_transfer_rules:
    timeout_seconds
    retry_attempts

integration_constraints

Transcript:
{trim_transcript(transcript)}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    try:
        content = response.choices[0].message.content
        return extract_json(content)
    except Exception:
        return {}