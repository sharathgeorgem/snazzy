# 🛤️ Railway Booking Assistant (OpenAI Agents)

This project allows users to query train availability using natural language. The assistant extracts travel details, optionally performs web search, and returns structured JSON.

---

## 🧠 Features

- Parses natural language queries like:
  - `"Find trains from Delhi to Mumbai on Friday"`
  - `"Sleeper class trains between Chennai and Bangalore"`
- Extracts travel parameters: `source`, `destination`, `date`, and `class`
- Uses OpenAI Agents (via `WebSearchTool`) or local stub logic
- Understands class names like `"first ac"`, `"chair car"`, and maps them to:
  - `"1A"`, `"2A"`, `"3A"`, `"SL"`, `"CC"`, `"2S"`

---

## 📁 Project Structure

| File                                     | Description                                      |
|------------------------------------------|--------------------------------------------------|
| `railway_agent_openai.py`                | Agent using real-time web search                 |
| `railway_agent_openai_without_websearch.py` | Agent using stubbed/fallback data            |
| `agent_core.py`                          | Core logic to extract and normalize input        |
| `test_railway_agent.py`                  | ✅ Pytest suite to validate all major flows      |

---

## ▶️ Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set OpenAI key
echo "OPENAI_API_KEY=sk-..." > .env

# For real-time agent
python railway_agent_openai.py

# For stub/offline fallback
python railway_agent_openai_without_websearch.py
```

## TESTING

```bash
# Run all tests
pytest test_railway_agent.py -v

# Run a specific test
pytest test_railway_agent.py::test_class_extraction

# Run manually (fallback)
python test_railway_agent.py
```

