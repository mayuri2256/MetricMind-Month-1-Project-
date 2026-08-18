# MetricMind — Month 1 Project

MetricMind is a GitHub-ready prototype of a governed conversational BI engine. It converts a small set of natural-language business questions into **approved semantic metrics** instead of allowing arbitrary SQL generation.

## Month 1 scope

- Synthetic corporate sales dataset
- Governed semantic metric definitions
- Deterministic natural-language intent parser
- Query compiler that produces a semantic query payload
- Revenue, cost, profit, and margin analysis
- Root-cause breakdown for margin movement
- Query governance and audit logging
- Streamlit dashboard with charts and transparent API payloads
- Automated tests

## Architecture

```text
User question
     |
     v
Intent parser  --->  Governance validator  --->  Semantic query engine
     |                         |                         |
     +-------------------------+-------------------------+
                               |
                         Audit log + UI
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_data.py
streamlit run app.py
```

Open the local URL shown by Streamlit. Example questions:

- `Show Q3 2025 revenue`
- `Show European sales by country`
- `Why did European margins drop last quarter?`
- `Compare revenue by region in Q4 2025`

## Run tests

```bash
pytest -q
```

## Project structure

```text
metricmind-month1/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── sales.csv
├── semantic_layer/
│   └── metrics.yml
├── src/
│   ├── __init__.py
│   ├── semantic_engine.py
│   └── audit.py
├── scripts/
│   └── generate_data.py
└── tests/
    └── test_metricmind.py
```

## Important design decision

This Month 1 implementation intentionally uses a deterministic parser and local semantic engine. It is safe to demo without an external LLM key. In Month 2, the parser can be replaced with LangChain or an LLM function-calling layer while keeping the governed semantic API unchanged.

## GitHub upload

```bash
git init
git add .
git commit -m "Add MetricMind Month 1 governed conversational BI prototype"
git branch -M main
git remote add origin https://github.com/<your-username>/metricmind-month1.git
git push -u origin main
```
