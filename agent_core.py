import json
from typing import Dict, Any
from datetime import datetime, timedelta
from agents import Agent, WebSearchTool, function_tool
import re
import dateparser
from models.models import FlightQueryRequest
from openai import OpenAI

VALID_CLASS_CODES = {"1A", "2A", "3A", "SL", "CC", "2S", "SLEEPER"}
PHRASE_TO_CLASS = {
    "first ac": "1A",
    "second ac": "2A",
    "third ac": "3A",
    "sleeper": "SL",
    "chair car": "CC",
    "second sitting": "2S"
}

@function_tool
def extract_train_travel_info_from_prompt(query: str) -> Dict[str, Any]:
    source = ""
    destination = ""
    travel_class = "3A"
    travel_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    query_lower = query.lower()

    from_match = re.search(r'from\s+([a-zA-Z\s]+?)\s+to', query_lower)
    to_match = re.search(r'to\s+([a-zA-Z\s]+?)(?:\s+in|\s+on|\s+for|$)', query_lower)
    between_match = re.search(r'between\s+([a-zA-Z\s]+?)\s+and\s+([a-zA-Z\s]+)', query_lower)
    class_match = re.search(r'(1A|2A|3A|SL|CC|2S|sleeper)', query_lower)
    date_match = re.search(r'on\s+([a-zA-Z0-9,\s]+)', query_lower)

    if between_match:
        source = between_match.group(1).strip().title()
        destination = between_match.group(2).strip().title()
    else:
        if from_match:
            source = from_match.group(1).strip().title()
        if to_match:
            destination = to_match.group(1).strip().title()

    for phrase, code in PHRASE_TO_CLASS.items():
        if phrase in query_lower:
            travel_class = code
            break

    if class_match:
        match = class_match.group(1).upper()
        if match in VALID_CLASS_CODES:
            travel_class = "SL" if match == "SLEEPER" else match

    if date_match:
        parsed = dateparser.parse(date_match.group(1))
        if parsed:
            travel_date = parsed.strftime("%Y-%m-%d")

    return {
        "source": source,
        "destination": destination,
        "date": travel_date,
        "class": travel_class
    }

@function_tool
def extract_flight_info_from_prompt(prompt: str) -> FlightQueryRequest:
    system_prompt = """
You are a flight data analyser.

🚨 YOUR ONLY TASK: Extract the following fields from the user query/prompt and return a JSON object in EXACTLY this format:
{
  "source": "<source>",
  "destination": "<destination>",
  "date": "<YYYY-MM-DD>",
  "cabin_class": "Economy|Business|First"
}

RULES:
- ❌ DO NOT write prose, explanations, links, or commentary.
- ❌ DO NOT include markdown, formatting, or headings.
- ✅ ONLY return raw JSON.
- ✅ If a field is missing, leave it as an empty string: "".
- ✅ Default cabin_class to "Economy" if missing.
- ✅ Default date to tomorrow (YYYY-MM-DD format) if missing.
- 🎯 Output MUST be valid JSON, with double quotes around all keys and values.
- ⚠️ DO NOT mix natural language with the JSON. Just the JSON output. Nothing else.

Examples:
Prompt: "I want to fly to Mumbai tomorrow in business class."
Response:
{
  "source": "",
  "destination": "Mumbai",
  "date": "2025-04-15",
  "cabin_class": "Business"
}

Prompt: "Flights from Chennai to Delhi"
Response:
{
  "source": "Chennai",
  "destination": "Delhi",
  "date": "2025-04-15",
  "cabin_class": "Economy"
}
"""

    response = OpenAI.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": f"Prompt: {prompt.strip()}"}
        ],
        temperature=0,
    )

    parsed = json.loads(response.choices[0].message.content)
    return FlightQueryRequest(**parsed)

def create_agent() -> Agent:
    return Agent(
        name="Transport Booking Assistant",
        instructions="""
You are a transport booking assistant specializing in Indian travel.

1. If the prompt includes terms related to trains (e.g., "train", "IRCTC", "railway"), use the `extract_train_travel_info` tool to extract details.
2. If the prompt includes terms related to flights (e.g., "fly", "flight", "airfare", "aeroplane"), use the `extract_flight_info` tool instead.

Then, use the WebSearchTool to fetch real-time availability from Goibibo for trains.
https://www.goibibo.com/trains/

Use web search to find flight availability from makemytrip.com for flights.

3. If the prompt includes both trains and flights, prioritize the train information.
4. Always return valid JSON with the following structure:
5. If no availability is found, you must still return a valid JSON object with empty `trains` or `flights` list, instead of plain text explanation.
e.g:{
  "source": "Delhi",
  "destination": "Leh",
  "date": "2025-04-17",
  "class": "3A",
  "trains": []
}


Expected JSON response from Websearchtool for trains:
{
  "source": "<city>",
  "destination": "<city>",
  "date": "<YYYY-MM-DD>",
  "class": "<1A|2A|3A|SL|CC|2S>",
  "trains": [
    {
      "train_number": "12951",
      "train_name": "Mumbai Rajdhani",
      "departure": "16:25",
      "arrival": "08:15",
      "duration": "15h 50m",
      "availability": "Available 42",
      "fare": 1985
    }
  ]
}

Expected JSON response for flights:
{
  "source": "<source>",
  "destination": "<destination>",
  "date": "<YYYY-MM-DD>",
  "cabin_class": "Economy|Business|First",
  "flights": [
    {
      "flight_number": "AI202",
      "departure": "2023-10-01T10:00:00",
      "arrival": "2023-10-01T12:30:00",
      "duration": "2h 30m",
      "availability": "Available 5",
      "fare": 5000
    }
  ]
}

Always return valid JSON only. No markdown, no plain text, no extra commentary.
""",
        tools=[
            extract_train_travel_info_from_prompt,
            extract_flight_info_from_prompt,
            WebSearchTool()
        ]
    )
