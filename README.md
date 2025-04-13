# 🚆 Railway Booking Assistant (OpenAI Agent)

This project is a smart natural language interface for checking train availability in India. It uses the OpenAI Agents SDK to extract travel parameters from plain English queries and returns structured JSON output.

---

## 🧠 Features

- Understands queries like:  
  `"Find sleeper trains from Chennai to Bangalore tomorrow"`
- Extracts: `source`, `destination`, `date`, `class`
- Uses **Playwright** to scrape real-time train availability (via Goibibo)
- Validated output with Pydantic models
- Fully testable with `pytest`

---

## 🚀 How to Use

### 🔧 Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/sharathgeorgem/snazzy.git
   cd snazzy
   ```

2. Create a `.env` file:
   ```
   OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXX
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Playwright browser dependencies:
   ```bash
   playwright install
   ```

5. Run the assistant:
   ```bash
   python railway_agent_openai.py
   ```

---

## 🧪 Run Tests

```bash
pytest test_railway_agent.py -v
```

All tests must pass for the agent to be considered production-ready.

---

## 🛤 Future Plans

- ⏳ Add IRCTC fallback - Possibly when life in Jail seems not too bad.
- ⏳ Add voice/WhatsApp interface - Cuz Baby got back!

---

Made with 💙 by [Sharath George M](https://github.com/sharathgeorgem)  
Powered by OpenAI's Agents SDK + Playwright 🚀