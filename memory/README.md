# Precedent Hindsight Memory Subsystem

This is the Hindsight Cloud-backed persistent memory layer for the Precedent AML alert decision-support system.

## Setup
1. Create a `.env` file based on `.env.example`.
2. Add your `HINDSIGHT_API_KEY`.
3. Set the bank to `precedent-aml` (or appropriate test bank).
4. Run `pip install -r requirements.txt`.

## Architecture
- **Retain**: Uses Hindsight Retain to store alert facts and human analyst decisions with overrides.
- **Recall**: Uses TEMPR retrieval to find precedents based on customer, typology, and transaction patterns.
- **Reflect**: Synthesizes knowledge over accumulated alerts for customer histories and typologies.
- **Mental Models**: Long-term summaries for typologies.
- **Directives**: Configured via `memory/directives.py` to ensure Hindsight reasons safely and accurately.

## Seed Data
To populate the system with demo history:
```bash
python -m memory.seed
```
This is idempotent and won't duplicate data.

## Interfaces for Teammates
### For Person 2 (Decision Engine)
- `memory.customer_memory.get_customer_history(customer_id)`
- `memory.precedent_memory.get_precedents(alert)`
- `memory.typology_memory.get_typology_knowledge(typology)`
- `memory.retain.retain_analyst_decision(alert, agent_recommendation, final_decision, analyst_reason)`
- `memory.evidence.get_memory_evidence(response_dict)`

### For Person 3 (UI)
- `memory.customer_memory.get_customer_history(customer_id)`
- `memory.timeline.get_customer_timeline(customer_id)`
- `memory.precedent_memory.get_precedents(alert)`
- `memory.consolidate.get_memory_stats()`
- `memory.evidence.get_memory_evidence(response_dict)`
- `memory.retain.retain_analyst_decision(...)`

## Tests
Run tests with:
```bash
PYTHONPATH=. pytest tests/
```

## Cost considerations
- Only retain when a decision is final.
- Use `recall` over `reflect` for fetching simple historical precedents.
- Refresh mental models periodically, not on every write.
