import asyncio
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, Any, List
from pydantic import BaseModel, Field, ValidationError
from agents import Agent, Runner, function_tool

# Load OpenAI key
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# -------------------------------
# Pydantic Output Schema
# -------------------------------
class TrainInfo(BaseModel):
    train_number: str
    train_name: str
    departure: str
    arrival: str
    duration: str
    availability: str
    fare: int

class TrainAvailability(BaseModel):
    source: str
    destination: str
    date: str
    class_type: str = Field(..., alias="class")
    trains: List[TrainInfo]

# -------------------------------
# Tool: Extract info and simulate train data
# -------------------------------
@function_tool
def extract_travel_info(query: str) -> Dict[str, Any]:
    import re
    import dateparser

    source = ""
    destination = ""
    travel_class = "3A"
    travel_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Improved regex to handle many formats
    from_match = re.search(r'from\s+([a-zA-Z\s]+?)\s+to', query, re.IGNORECASE)
    to_match = re.search(r'to\s+([a-zA-Z\s]+?)(?:\s+in|\s+on|\s+for|$)', query, re.IGNORECASE)
    class_match = re.search(r'(1A|2A|3A|SL|2S|sleeper)', query.lower())
    date_match = re.search(r'on\s+([a-zA-Z0-9,\s]+)', query.lower())
    # Fallback for "between X and Y" phrasing
    between_match = re.search(r'between\s+([a-zA-Z\s]+?)\s+and\s+([a-zA-Z\s]+)', query, re.IGNORECASE)
    
    if between_match:
        source = between_match.group(1).strip().title()
        destination = between_match.group(2).strip().title()
    if from_match:
        source = from_match.group(1).strip().title()
    if to_match:
        destination = to_match.group(1).strip().title()
    if class_match:
        match = class_match.group(1).upper()
        travel_class = "SL" if match == "SLEEPER" else match
    if date_match:
        parsed = dateparser.parse(date_match.group(1))
        if parsed:
            travel_date = parsed.strftime("%Y-%m-%d")

    trains = []
    if source == "Delhi" and destination == "Mumbai":
        trains = [
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
    elif source == "Chennai" and destination == "Bangalore":
        trains = [
            {
                "train_number": "12607",
                "train_name": "Lalbagh Express",
                "departure": "15:30",
                "arrival": "21:00",
                "duration": "5h 30m",
                "availability": "Available 23",
                "fare": 310
            }
        ]

    return {
        "source": source,
        "destination": destination,
        "date": travel_date,
        "class": travel_class,
        "trains": trains
    }

# -------------------------------
# Main Agent Logic
# -------------------------------
async def railway_agent(user_query: str) -> Dict[str, Any]:
    agent = Agent(
        name="Railway Booking Assistant",
        instructions="""
Your ONLY job is to extract travel details (source, destination, date, and class) from the user's query using the `extract_travel_info` tool.

Return a valid JSON using this structure:
{
  "source": "<city>",
  "destination": "<city>",
  "date": "<YYYY-MM-DD>",
  "class": "<1A|2A|3A|SL|2S>",
  "trains": [<train objects>]
}

Do NOT explain. Do NOT add extra words. Do NOT narrate. JUST return valid JSON.
""",
        tools=[extract_travel_info]
    )

    result = await Runner.run(agent, user_query)

    output = result.final_output

    # 🔍 Clean up LLM output (strip markdown code blocks like ```json ... ```)
    if isinstance(output, str):
        output = output.strip()
        if output.startswith("```json"):
            output = output.replace("```json", "").replace("```", "").strip()
        elif output.startswith("```"):
            output = output.replace("```", "").strip()

        try:
            output = json.loads(output)
        except json.JSONDecodeError:
            print("🔴 Agent returned plain text:\n", output)
            return {
                "source": "",
                "destination": "",
                "date": "",
                "class": "3A",
                "trains": [],
                "error": "Agent did not return valid JSON."
            }

    # ✅ Validate structured data
    try:
        validated = TrainAvailability.parse_obj(output)
    except ValidationError as ve:
        print("❌ Validation error:", ve)
        return {
            "source": output.get("source", ""),
            "destination": output.get("destination", ""),
            "date": output.get("date", ""),
            "class": output.get("class", "3A"),
            "trains": [],
            "error": "Response was invalid or incomplete"
        }

    return validated.dict(by_alias=True)

# -------------------------------
# Manual CLI for Debugging
# -------------------------------
async def main():
    print("🚆 Railway Booking Assistant 🚆")
    while True:
        query = input("\nAsk me about trains (or type 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            break
        response = await railway_agent(query)
        print(json.dumps(response, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
