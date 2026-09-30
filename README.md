# PRECEDENT — AML Decision Intelligence

PRECEDENT is an AI-powered AML (Anti-Money Laundering) decision-support system that helps analysts investigate alerts using historical decisions, institutional memory, and AI-generated recommendations.

The system combines:
- **Hindsight memory** for retaining and recalling historical analyst decisions and customer/typology context
- **Groq LLM** for AI-assisted decision recommendations
- **Guardrails and precedent ranking** to keep recommendations grounded in available evidence
- **Streamlit** for the analyst-facing web application
- **HI-Small transaction data** for alert generation and evaluation

> **Important:** PRECEDENT is a decision-support tool. The human analyst makes the final decision.

## Key Features

### 1. AML Alert Command Center
Provides an overview of the active alert queue, risk levels, reviewed alerts, and system status.

### 2. Alert Investigation
Analysts can inspect alerts and use historical precedents and customer memory to support investigation.

### 3. AI Decision Support
The Decision Engine combines retrieved precedents and alert information to generate an AI recommendation with supporting reasoning.

### 4. Persistent Memory with Hindsight
Analyst decisions can be retained as historical precedents so future investigations can learn from previous cases.

### 5. Consistency Audit
Identifies potentially conflicting historical analyst decisions retrieved from the Hindsight memory bank.

### 6. Evaluation Dashboard
Displays measured metrics from the available dataset, alert generator, Hindsight memory, analyst decisions, and LLM evaluation.

## Architecture

```text
                         ┌─────────────────────┐
                         │    AML Alert        │
                         │  Transaction Data   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Alert Generator    │
                         │ Risk / Typology     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                  ┌─────────────────────────────────┐
                  │      Hindsight Memory           │
                  │  Customer History / Precedents  │
                  └───────────────┬─────────────────┘
                                  │
                                  ▼
                         ┌─────────────────────┐
                         │  Precedent Ranker   │
                         │ + Decision Engine   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Groq LLM        │
                         │ AI Recommendation   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Human Analyst     │
                         │ Accept / Override   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Retain New Decision │
                         │ in Hindsight Memory │
                         └─────────────────────┘
```

## Project Structure

```text
precedent/
├── agent/
│   ├── decision_engine.py
│   ├── evaluator.py
│   ├── explanation.py
│   ├── guardrails.py
│   ├── precedent_ranker.py
│   ├── prompts.py
│   ├── retry.py
│   └── schemas.py
│
├── data/
│   ├── alert_generator.py
│   ├── build_alert_dataset.py
│   ├── live_alerts.py
│   └── mock_data.py
│
├── integration/
│   └── precedent_service.py
│
├── memory/
│   ├── customer_memory.py
│   ├── precedent_memory.py
│   ├── typology_memory.py
│   ├── hindsight_client.py
│   ├── retain.py
│   ├── recall.py
│   ├── reflect.py
│   └── ...
│
├── ui/
│   ├── components/
│   └── styles/
│
├── views/
│   ├── alerts.py
│   ├── audit.py
│   ├── evaluation.py
│   └── memory.py
│
├── app.py
├── requirements.txt
├── .env.example
└── tests/
```

## Requirements

- Python 3.10+
- pip
- Internet connection for Hindsight and Groq APIs
- Hindsight API key
- Groq API key

## Installation

Clone the repository:

```bash
git clone https://github.com/anwar-jehan-begum/precedent.git
cd precedent
```

Create a virtual environment:

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file from the example:

### Windows

```powershell
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Then add your API keys:

```env
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_BANK_ID=precedent-aml
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io

GROQ_API_KEY=your_groq_api_key
```

Never commit `.env` or API keys to GitHub.

## Dataset

The application can use the **HI-Small transaction dataset** for real alert generation and evaluation.

Expected path:

```text
data/HI-Small/HI-Small_Trans.csv
```

The dataset is intentionally excluded from Git because it is large and is listed in `.gitignore`.

Without the dataset, the application can still run in demo mode, while dataset-dependent metrics remain unavailable.

## Run the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, typically:

```text
http://localhost:8501
```

## Seed Demo Memory

To populate the Hindsight memory bank with demo historical decisions:

```bash
python -m memory.seed
```

## Run Tests

Run the memory and integration tests:

```bash
PYTHONPATH=. pytest tests/
```

Run the root-level tests as well:

```bash
PYTHONPATH=. pytest
```

## Main Technology Stack

| Area | Technology |
|---|---|
| Web UI | Streamlit |
| AI / LLM | Groq |
| Persistent Memory | Hindsight |
| Data Processing | Python, Pandas |
| Visualization | Plotly |
| Validation | Pydantic |
| Testing | Pytest |
| Configuration | python-dotenv |

## Safety & Design Principles

PRECEDENT is designed around evidence-grounded decision support:

- Historical comparison fields are taken from recalled Hindsight precedents rather than copied from the current alert.
- The current alert is excluded from being used as its own historical precedent.
- Unknown or unsupported Hindsight records are filtered before being used as authoritative precedents.
- The system is designed to keep the analyst in control of the final decision.
- API secrets are loaded through environment variables and should never be committed.

## License

Add the project's license information here before publishing the repository publicly.
