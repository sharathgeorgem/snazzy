import asyncio
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, Any, List
from pydantic import BaseModel, Field, ValidationError
from agent_core import create_railway_agent, extract_travel_info
from agents import Runner


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
# Main Agent Logic
# -------------------------------
async def railway_agent(user_query: str) -> Dict[str, Any]:
    agent = create_railway_agent()
    result = await Runner.run(agent, user_query)
    output = result.final_output

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
