---
id: 1
title: Update Todo Constitution
stage: constitution
date: 2025-12-28
surface: agent
model: Qwen
feature: none
branch: main
user: hasnainxdev
command: /sp.constitution
labels: [constitution, todo, spec-driven]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```
description: Create or update the project constitution from interactive or provided principle inputs, ensuring all dependent templates stay in sync.
handoffs: 
  - label: Build Specification
    agent: sp.specify
    prompt: Implement the feature specification based on the updated constitution. I want to build...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are updating the project constitution at `.specify/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

Follow this execution flow:

1. Load the existing constitution template at `.specify/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

2. Collect/derive values for placeholders:
   - If user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.

3. Draft the updated constitution content:
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

4. Consistency propagation checklist (convert prior checklist into active validations):
   - Read `.specify/templates/plan-template.md` and ensure any "Constitution Check" or rules align with updated principles.
   - Read `.specify/templates/spec-template.md` for scope/requirements alignment—update if constitution adds/removes mandatory sections or constraints.
   - Read `.specify/templates/tasks-template.md` and ensure task categorization reflects new or removed principle-driven task types (e.g., observability, versioning, testing discipline).
   - Read each command file in `.specify/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required.
   - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present). Update references to principles changed.

5. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file after update):
   - Version change: old → new
   - List of modified principles (old title → new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending) with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

6. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).

7. Write the completed constitution back to `.specify/memory/constitution.md` (overwrite).

8. Output a final summary to the user with:
   - New version and bump rationale.
   - Any files flagged for manual follow-up.
   - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

Do not create a new template; always operate on the existing `.specify/memory/constitution.md` file.

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - Route is automatically determined by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
     - `general` → `history/prompts/general/`

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.


/sp.constitution Requirements:
You are required to complete the 5-Phase "Evolution of Todo" Project using Claude Code and Spec-Kit Plus. The core deliverables are:

- Spec-Driven Implementation: You must implement all 5 Phases of the project (detailed below). You are strictly required to use Spec-Driven Development. You must write a Markdown Constitution and Spec for every feature of the phase, and use Claude Code to generate the implementation.
Constraint: You cannot write the code manually. You must refine the Spec until Claude Code generates the correct output.

- Integrated AI Chatbot: In Phases III, IV, and V, you must implement a conversational interface using OpenAI Chatkit, OpenAI Agents SDK, and Official MCP SDK. The bot must be able to manage the user's Todo list via natural language (e.g., "Reschedule my morning meetings to 2 PM").

- Cloud Native Deployment: In Phases IV and V, you must deploy the chatbot locally on Minikube, and on the cloud on DigitalOcean Kubernetes (DOKS). 

Todo App Feature Progression
Basic Level (Core Essentials)

These form the foundation—quick to build, essential for any MVP:
- Add Task – Create new todo items
- Delete Task – Remove tasks from the list
- Update Task – Modify existing task details
- View Task List – Display all tasks
- Mark as Complete – Toggle task completion status


 Intermediate Level (Organization & Usability)
Add these to make the app feel polished and practical:
1. Priorities & Tags/Categories – Assign levels (high/medium/low) or labels (work/home)
2. Search & Filter – Search by keyword; filter by status, priority, or date
3. Sort Tasks – Reorder by due date, priority, or alphabetically


Advanced Level (Intelligent Features)
Recurring Tasks – Auto-reschedule repeating tasks (e.g., "weekly meeting")
Due Dates & Time Reminders – Set deadlines with date/time pickers; browser notifications


Use Agentic Dev Stack for building this hackathon project.
Hackathon Phases Overview:
Description, Technology Stack, Points

Phase I
In-Memory Python Console App Python, Claude Code, Spec-Kit Plus +100

Phase II
Full-Stack Web Application Next.js, FastAPI, SQLModel, Neon DB +150

Phase III
AI-Powered Todo Chatbot OpenAI ChatKit, OpenAI Agents SDK (https://openai.github.io/openai-agents-python), Official MCP SDK +200

Phase IV
Local Kubernetes Deployment Docker, Minikube, Helm, kubectl-ai, kagent +250

Phase V
Advanced Cloud Deployment Kafka, Dapr, DigitalOcean DOKS +300
TOTAL 1,000


Bonus Points
Participants can earn additional bonus points for exceptional implementations:
Bonus Feature Points
Reusable Intelligence – Create and use reusable intelligence via Claude Code Subagents and Agent Skills +200
Create and use Cloud-Native Blueprints via Agent Skills +200
Multi-language Support – Support Urdu in chatbot +100
Voice Commands – Add voice input for todo commands +200
TOTAL BONUS +600


Project Details: The Evolution of Todo
Focus and Theme: From CLI to Distributed Cloud-Native AI Systems.
Goal: Students act as Product Architects, using AI to build progressively complex software without writing boilerplate code.

Project Overview
This project simulates the real-world evolution of software. You will start with a simple script and end with a Kubernetes-managed, event-driven, AI-powered distributed system.

Phase Breakdown
Phase I: Todo In-Memory Python Console App
Basic Level Functionality
Objective: Build a command-line todo application that stores tasks in memory using Claude Code and Spec-Kit Plus.

💡Development Approach: Use the Agentic Dev Stack workflow:
This is a powerful integration. By combining the declarative nature of AGENTS.md, the structured workflow of Panaversity Spec-KitPlus, and the agentic execution of Claude Code
This section outlines a workflow where AGENTS.md acts as the Constitution, Spec-KitPlus acts as the Architect, and Claude Code acts as the Builder.

- Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual coding allowed. We will review the process, prompts, and iterations to judge each phase and project.

Requirements
Implement all 5 Basic Level features (Add, Delete, Update, View, Mark Complete)
Use spec-driven development with Claude Code and Spec-Kit Plus

Follow clean code principles and proper Python project structure

Technology Stack:
- UV package manager
Python 3.13+
Claude Code
Spec-Kit Plus

Deliverables
GitHub repository with:
- Constitution file
- specs history folder containing all specification files
- /src folder with Python source code
- README.md with setup instructions
- CLAUDE.md with Claude Code instructions

Working console application demonstrating:
- Adding tasks with title and description
- Listing all tasks with status indicators
- Updating task details
- Deleting tasks by ID
- Marking tasks as complete/incomplete
```

## Response snapshot

Based on the user requirements, I have successfully updated the project constitution file at `.specify/memory/constitution.md`. Here's what was accomplished:

1. Analyzed the user requirements for the "Evolution of Todo: From CLI to Distributed Cloud-Native AI Systems" project
2. Identified all placeholder tokens in the constitution template
3. Collected/derived values for all placeholders based on the user requirements
4. Drafted the updated constitution content with concrete values
5. Checked dependent templates for potential updates
6. Created a Sync Impact Report
7. Validated the updated constitution
8. Wrote the completed constitution back to `.specify/memory/constitution.md`

The new constitution includes six core principles:
- Spec-Driven Development First
- AI-Assisted Implementation
- Test-First (NON-NEGOTIABLE)
- Progressive Evolution
- Feature Completeness
- Agentic Dev Stack Integration

Additionally, it includes sections on Technology Stack Requirements, Development Workflow, and Governance, all tailored to the specific requirements of the Todo Spec-Driven Development project.

## Outcome

- ✅ Impact: Updated constitution file with 6 core principles and project-specific requirements
- 🧪 Tests: none required for constitution update
- 📁 Files: .specify/memory/constitution.md updated with new content
- 🔁 Next prompts: /sp.specify to implement feature specification based on updated constitution
- 🧠 Reflection: Constitution successfully updated to reflect the requirements of the Todo Spec-Driven Development project with 5 phases

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS - all requirements met
- Prompt variant (if applicable): standard constitution update
- Next experiment (smallest change to try): implement feature specification based on updated constitution