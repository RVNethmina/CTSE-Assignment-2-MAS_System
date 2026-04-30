# Project Rescue MAS

Project Rescue MAS is a locally hosted multi-agent system that reviews a project against an assignment brief and produces a submission readiness report. It uses LangGraph for orchestration, Ollama-backed local models for agent reasoning, typed Python tools for filesystem interactions, and structured shared state for agent handoffs.

## Agents

- Intake and Scope Agent: validates the brief path and project path, detects the likely project stack, and initializes workflow state.
- Brief and Rubric Analyst Agent: parses PDF, Markdown, or text briefs and extracts supported requirements, constraints, and grading signals.
- Repository and Evidence Auditor Agent: scans the local project for implementation evidence, tests, tools, logging, and report output capability.
- Risk and Delivery Strategist Agent: compares requirements against repository evidence and writes the final rescue report.

## Tools

- `project_input_validator`: validates provided paths and detects the likely stack.
- `brief_parser`: extracts text from PDF, Markdown, or text assignment briefs.
- `repo_audit`: audits repository structure while ignoring generated, vendor, cache, and sample-data directories.
- `rescue_plan_writer`: writes Markdown and JSON rescue reports.

## Local Setup

```powershell
pip install -r requirements.txt
ollama pull llama3
```

Run the workflow:

```powershell
python -m app.main --brief "CTSE - Assignment 2.pdf" --project "." --model llama3
```

Generated reports are written to `outputs/rescue_report.md` and `outputs/rescue_report.json`.

## Testing

Run deterministic tests:

```powershell
pytest -m "not llm_judge"
```

Run the local LLM-as-a-judge evaluation when Ollama is running:

```powershell
pytest -m llm_judge
```
