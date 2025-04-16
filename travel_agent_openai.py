import asyncio
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, Any, List
from pydantic import ValidationError
from agent_core import create_agent
from agents import Runner
from models.models import FlightAvailability, TrainAvailability

# Load OpenAI key
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# -------------------------------
# Main Agent Logic
# -------------------------------
async def railway_agent(user_query: str) -> Dict[str, Any]:
    agent = create_agent()
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
                "error": "Agent did not return valid JSON.",
                "raw_output": output
            }

    # Determine if it's a train response or flight response based on known fields
    if isinstance(output, dict):
        if "trains" in output:
            try:
                validated = TrainAvailability.parse_obj(output)
                return validated.dict(by_alias=True)
            except ValidationError as ve:
                print("❌ Train validation error:", ve)
            return {"error": "Invalid train response", "raw_output": output}
        elif "flights" in output:
            try:
                validated = FlightAvailability.parse_obj(output)
                return validated.dict(by_alias=True)
            except ValidationError as ve:
                print("❌ Flight validation error:", ve)
            return {"error": "Invalid flight response", "raw_output": output}
        else:
            return {"error": "Unknown response format", "raw_output": output}
    else:
        return {"error": "Agent returned non-dict output", "raw_output": output}

# -------------------------------
# Manual CLI for Debugging
# -------------------------------
async def main():
    print("🧳 Travel Assistant 🧳")
    while True:
        query = input("\nAsk me about trains or flights (or type 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            break
        response = await railway_agent(query)
        print(json.dumps(response, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
