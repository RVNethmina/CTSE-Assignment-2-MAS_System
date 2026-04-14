# Project Rescue Report

Generated at: **2026-04-14 18:13:03**

## Executive Summary
This report analyzes the provided project against the assignment brief and identifies the most important gaps before submission.

## Submission Readiness Score
**15/100**

## Current Blockers
- Agent count is below the required 3 to 4 distinct agents.
- Automated testing evidence is missing.
- Logging or tracing evidence is missing.
- Final output/report generation evidence is missing.

## Brief Summary
Build a local system that helps a volunteer organization process incoming help requests.

## Extracted Assignment Requirements
- The system should operate as a multi-agent workflow rather than a single assistant.
- Use 4 distinct agents with clearly separated responsibilities.
- At least 1 custom Python tool must interact with files or structured local data.

## Technical Constraints
- Run fully on a local machine.
- Use Python for the implementation.
- Do not depend on paid APIs.
- Use structured shared state between agents.
- Include logging or tracing so the execution flow can be inspected.

## Agent Design Snapshot
### IntakeAndScopeAgent
- **Owner:** Student 1
- **Role:** Intake and Scope Agent
- **Persona:** A careful project intake coordinator that validates evidence before analysis begins.
- **Objective:** Validate input paths, identify basic project characteristics, and initialize workflow state.
- **Constraints:** Do not invent missing files or assume project structure without evidence.
- **Owned Tool:** project_input_validator
- **System Prompt:** You are the Intake and Scope Agent. Validate the provided brief and project path, summarize what was received, and prepare clean initial state for downstream agents. Never invent files, folders, or evidence.

### BriefAndRubricAnalystAgent
- **Owner:** Student 2
- **Role:** Brief and Rubric Analyst Agent
- **Persona:** A rubric-focused academic analyst that extracts only supported requirements.
- **Objective:** Read the assignment brief and extract deliverables, constraints, and grading signals.
- **Constraints:** Do not hallucinate requirements that are not explicitly or strongly supported by the brief.
- **Owned Tool:** brief_parser
- **System Prompt:** You are the Brief and Rubric Analyst Agent. Extract concrete requirements, submission components, constraints, and grading signals from the assignment brief. Return only supported findings.

### RepositoryAndEvidenceAuditorAgent
- **Owner:** Student 3
- **Role:** Repository and Evidence Auditor Agent
- **Persona:** A strict repository auditor that works only from real file-system evidence.
- **Objective:** Inspect the repository structure and summarize what has actually been built.
- **Constraints:** Do not treat assumptions as evidence. Only report what the repository shows.
- **Owned Tool:** repo_audit
- **System Prompt:** You are the Repository and Evidence Auditor Agent. Inspect the provided project folder, count important implementation evidence, and identify missing or weak areas based only on actual repository contents.

### RiskAndDeliveryStrategistAgent
- **Owner:** Student 4
- **Role:** Risk and Delivery Strategist Agent
- **Persona:** A practical delivery strategist focused on submission readiness and risk reduction.
- **Objective:** Turn audit findings into blockers, priorities, action plans, and final report outputs.
- **Constraints:** Prioritize the highest-mark-impact issues first and avoid vague recommendations.
- **Owned Tool:** rescue_plan_writer
- **System Prompt:** You are the Risk and Delivery Strategist Agent. Compare requirements against evidence, identify critical blockers, prioritize next steps, assign ownership, and produce a clear submission rescue plan.

## Contribution Matrix
| Student | Agent | Owned Tool | Main Focus |
|---|---|---|---|
| Student 1 | Intake and Scope Agent | project_input_validator | Validate input paths, identify basic project characteristics, and initialize workflow state. |
| Student 2 | Brief and Rubric Analyst Agent | brief_parser | Read the assignment brief and extract deliverables, constraints, and grading signals. |
| Student 3 | Repository and Evidence Auditor Agent | repo_audit | Inspect the repository structure and summarize what has actually been built. |
| Student 4 | Risk and Delivery Strategist Agent | rescue_plan_writer | Turn audit findings into blockers, priorities, action plans, and final report outputs. |

## Repository Summary
Project contains 6 files and 5 directories. Detected artifacts: configuration, documentation, source_code. Agent files: 2, Tool files: 1, Test files: 0, Logging evidence: no, Output writer evidence: no.

## Compliance Snapshot
| Check | Status |
|---|---|
| 3 to 4 agent modules present | No |
| At least 1 custom tool present | Yes |
| Test files present | No |
| Logging/tracing evidence present | No |
| Output/report writing evidence present | No |

## Present Evidence
- configuration
- documentation
- source_code

## Missing or Weak Areas
- tests
- insufficient_agents
- missing_logging
- missing_output_writer

## Key Risks
- Testing evidence is missing, which can reduce marks for evaluation quality.
- Only 2 agent file(s) were detected, which may fail the 3 to 4 agent requirement.
- Logging or tracing evidence is missing, which weakens observability marks.
- No test files were detected in the repository.

## Prioritized Action Plan
- **High** — Create automated tests for each agent and one integration test for the full workflow.
- **High** — Implement at least 3 to 4 distinct agent modules with clear responsibilities.
- **High** — Implement structured logging or tracing and show it clearly in the demo.
- **High** — Add per-agent tests and one workflow integration test.
- **Medium** — Cross-check the implemented system against all extracted assignment requirements.
- **Medium** — Verify the project runs fully locally and does not depend on paid APIs.

## Suggested Team Ownership
- Student 1: Build the missing agent modules so the system reaches the required 3 to 4 distinct agents.
- Student 2: Create per-agent tests and one integration test for the full workflow.
- Student 3: Implement structured logging or tracing and make it clearly visible in the demo.
- Student 4: Implement final output/report generation and polish the rescue report for submission.

## Demo Checklist
- Run the full workflow locally using Ollama.
- Show all 4 agents executing in sequence.
- Demonstrate tool usage clearly.
- Show logs or tracing output.
- Open the generated rescue report file.
- Keep the demo under 5 minutes.

## Technical Report Outline
- Introduction and problem domain
- Why a multi-agent system is needed
- System architecture and workflow diagram
- Agent roles and responsibilities
- Custom tools and their usage
- State management design
- Observability and logging
- Testing and evaluation strategy
- Individual contributions
- Challenges and lessons learned

## Final Recommendation
The project is not submission-ready yet. Resolve the critical blockers first: missing agents, missing tests, missing observability, and missing final output generation.
