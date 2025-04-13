from typing import Dict, Any
from datetime import datetime, timedelta
from agents import Agent, WebSearchTool, function_tool
import re
import dateparser

# Valid train class codes and phrases
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
def extract_travel_info(query: str) -> Dict[str, Any]:
    source = ""
    destination = ""
    travel_class = "3A"
    travel_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    query_lower = query.lower()

    from_match = re.search(r'from\s+([a-zA-Z\s]+?)\s+to', query, re.IGNORECASE)
    to_match = re.search(r'to\s+([a-zA-Z\s]+?)(?:\s+in|\s+on|\s+for|$)', query, re.IGNORECASE)
    between_match = re.search(r'between\s+([a-zA-Z\s]+?)\s+and\s+([a-zA-Z\s]+)', query, re.IGNORECASE)
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

    # Phrase to class mapping
    for phrase, code in PHRASE_TO_CLASS.items():
        if phrase in query_lower:
            travel_class = code
            break

    # Direct code match if not matched via phrase
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

def create_railway_agent() -> Agent:
    return Agent(
        name="Railway Booking Assistant",
        instructions="""
You are a railway assistant. First, extract travel parameters using the `extract_travel_info` tool.

Then, use the WebSearchTool to search Goibibo, IRCTC, or other travel sources to find real-time train availability between the source and destination on the given date and class.

Look for train names, numbers, departure/arrival times, duration, seat availability, and fare.

⚠️ IMPORTANT:
- Always use the extracted parameters exactly as provided (especially the class).
- Allowed class codes: "1A", "2A", "3A", "SL", "CC", "2S"
- You MUST return a valid JSON object only. Strictly follow this format:

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

If there are no trains available or the route does not exist, you must still return the following valid JSON format using the input parameters:

{
  "source": "<source>",
  "destination": "<destination>",
  "date": "<date>",
  "class": "<class>",
  "trains": []
}

⚠️ Do not include explanations, descriptions, tables, or markdown output.
Only return valid JSON. No apologies, no background info, no plain text.
""",
        tools=[extract_travel_info, WebSearchTool()]
    )