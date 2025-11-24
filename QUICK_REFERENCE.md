# Quick Reference: Running the CrewAI Wall Panel QC Demo

## What is This?

A demonstration of **CrewAI orchestrating a complete quality control workflow** for building wall panels. Instead of sequential scripts, multiple specialized agents work together within the CrewAI framework to provide comprehensive analysis.

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Run the demo
uv run scripts/demo.py

# 3. Verify orchestration
uv run verify_crew_orchestration.py
```

## What Happens When You Run the Demo

```
┌─────────────────────────────────────────────┐
│  Demo Starts                                │
│  Creates 2 test panels (good & bad)         │
└────────────────┬────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────┐
│  For Each Panel:                            │
│                                             │
│  crew.kickoff()  ← ALL WORK HAPPENS HERE   │
│                                             │
│  Executes:                                  │
│  ├─ QC Inspector (deterministic checks)    │
│  ├─ Code Consultant (contextual analysis)  │
│  ├─ Report Generator (synthesis)           │
│  └─ Visualization (creates SVG)            │
└────────────────┬────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────┐
│  Outputs:                                   │
│                                             │
│  Console:                                   │
│  • CrewAI execution logs                   │
│  • Agent task completion status            │
│  • Violations found                        │
│                                             │
│  Files:                                     │
│  • demo_output/good_panel_001.svg          │
│  • demo_output/bad_panel_001.svg           │
└─────────────────────────────────────────────┘
```

## The 4 Agents

### 1. QC Inspector Agent

- **Expertise:** Building code compliance
- **Job:** Run deterministic rule checks
- **Uses:** Building codes JSON
- **Returns:** Violations with rule references

### 2. Building Code Consultant Agent

- **Expertise:** Contextual analysis
- **Job:** Identify risks requiring judgment
- **Uses:** Panel data + deterministic results
- **Returns:** Context-dependent violations

### 3. Report Generator Agent

- **Expertise:** Technical writing
- **Job:** Synthesize all findings
- **Uses:** All agent outputs
- **Returns:** Comprehensive QC report

### 4. Visualization Specialist Agent

- **Expertise:** Visual communication
- **Job:** Create SVG diagrams
- **Uses:** Panel + violations
- **Returns:** SVG with annotations

## Key Design Decisions

✅ **Full Orchestration:** All work within `crew.kickoff()`  
✅ **No Hardcoding:** Violations from agent analysis  
✅ **Agent Collaboration:** Agents pass results through CrewAI memory  
✅ **Traceability:** See agent reasoning in verbose output  
✅ **Extensibility:** Add agents/tools without changing core

## Test Panels

### Good Panel

- Centered window, low seismic zone
- Passes all deterministic checks
- No violations expected

### Bad Panel

- Corner window, high seismic zone
- Passes deterministic checks (proper support)
- Contextual issue: corner + seismic = risky

## Files to Review

| File                           | Purpose                                       |
| ------------------------------ | --------------------------------------------- |
| `README.md`                    | Overview + agent flow diagram                 |
| `CREW_ARCHITECTURE.md`         | Deep dive into architecture                   |
| `IMPLEMENTATION_SUMMARY.md`    | How all 4 questions were addressed            |
| `scripts/demo.py`              | Main demo script                              |
| `verify_crew_orchestration.py` | Verification that violations come from agents |
| `crew/agents.py`               | Agent definitions (4 agents)                  |
| `crew/tasks.py`                | Task definitions                              |

## Verification: Violations Are From Agents

Run this to prove violations come from CrewAI agents, not hardcoding:

```bash
uv run verify_crew_orchestration.py
```

Output will show:

```
✓ QC Inspector Agent finds violations
✓ All work within crew.kickoff()
✓ No hardcoding, no execution outside crew
✓ Violations in agent output structure
```

## The Story

You're demonstrating how **CrewAI can orchestrate complex workflows** where multiple experts need to collaborate.

Traditional approach:

- Hard to maintain (multiple scripts)
- Hard to scale (changing logic is brittle)
- Hard to explain (no reasoning visible)

CrewAI approach:

- Easy to maintain (agents encapsulate expertise)
- Easy to scale (add agents without core changes)
- Easy to explain (see agent reasoning)

**For Wall Panel QC:** Show how combining deterministic rules + expert judgment through multi-agent orchestration provides comprehensive quality control that's professional, scalable, and explainable.

## Support

Questions? Check these docs:

1. **"How does data flow?"** → See `CREW_ARCHITECTURE.md` for diagram
2. **"Are violations hardcoded?"** → Run `verify_crew_orchestration.py`
3. **"What changed from before?"** → See `IMPLEMENTATION_SUMMARY.md`
4. **"How do I add a new agent?"** → See `crew/agents.py` and `crew/tasks.py`

---

**Ready to demonstrate CrewAI orchestration for complex workflows!** 🚀
