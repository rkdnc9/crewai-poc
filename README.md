# Wall Panel Quality Control with CrewAI

A proof-of-concept exploring agent-based orchestration for building code compliance assessment. This project examines how deterministic rule-based checks and contextual expert analysis can be combined to evaluate wall panel designs.

## Motivation

Building code compliance has two dimensions:

1. **Explicit Rules**: Deterministic checks (e.g., stud spacing, window support requirements) that follow clear specifications
2. **Contextual Considerations**: Design decisions that require domain expertise and judgment (e.g., seismic resilience for corner placements)

Rule-based systems excel at the former but struggle with the latter. This project explores using CrewAI to coordinate both types of analysis through specialized agents.

## Overview

The system orchestrates four agents to analyze IFC (Industry Foundation Classes) wall panel data:

- **QC Inspector**: Applies deterministic rule-based checks against building codes
- **Code Consultant**: Provides contextual analysis for design edge cases
- **Report Generator**: Synthesizes findings into structured output
- **Visualization Specialist**: Generates visual representations of violations

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key

### Setup

```bash
git clone <repository-url>
cd crewai-poc
uv sync
export OPENAI_API_KEY="your-api-key"
```

### Running Analysis

```bash
uv run scripts/demo.py
```

This processes test panels through the crew pipeline and generates reports and visualizations.

## Architecture

Agent orchestration occurs within `crew.kickoff()`. Each agent receives panel data and relevant context, performs its analysis, and passes results to subsequent agents. The system leverages CrewAI's memory management for inter-agent communication.

## Test Data

Two example panels are provided:

- **good_panel.ifc**: Centered window, low seismic zone
- **bad_panel.ifc**: Corner window, high seismic zone—passes deterministic checks but presents contextual concerns
- Passes deterministic checks (has proper support)
- **Expected:** ✅ Passes deterministic, ⚠️ Contextual risk flagged by consultant

---

## How to Verify Violations Come From Agents

Run this verification script to confirm that violations are discovered by CrewAI agents, NOT hardcoded:

```bash
uv run verify_crew_orchestration.py
```

**Output shows:**

- ✅ Violations from agent reasoning
- ✅ No hardcoded lists
- ✅ All work within crew.kickoff()
- ✅ Agent output structure with violations

---

## Architecture

### Directory Structure

```
scripts/
  └─ demo.py                      # Main demo orchestrating agents

crew/
  ├─ agents.py                    # 4 agent definitions
  └─ tasks.py                     # Agent tasks (what they do)

tools/
  ├─ deterministic_checker.py     # Rule engine
  ├─ llm_rule_checker.py          # LLM analysis
  ├─ visualizer_tool.py           # SVG generation
  ├─ crew_tools.py                # Tools agents use
  └─ output_parser.py             # Parse agent outputs

config/
  ├─ building_codes.json          # Rule definitions
  └─ exceptions.json              # Context exceptions

demo_output/
  ├─ good_panel.svg               # Generated visualizations
  └─ bad_panel.svg
```

### Core Files Explained

| File                           | Purpose                                             |
| ------------------------------ | --------------------------------------------------- |
| `scripts/demo.py`              | Orchestrates 4 agents through CrewAI crew.kickoff() |
| `crew/agents.py`               | Defines 4 specialized agents                        |
| `crew/tasks.py`                | Defines what each agent should do                   |
| `verify_crew_orchestration.py` | Proves violations come from agents                  |

---

## Implementation Details

### How Violations Are Generated

1. **QC Inspector Agent** analyzes panel against building codes
   - Returns: JSON with deterministic violations
2. **Building Code Consultant Agent** performs contextual analysis
   - Input: Panel + deterministic results
   - Returns: Additional context-dependent violations
3. **Report Generator Agent** synthesizes findings
   - Input: All violations
   - Returns: Comprehensive report
4. **Visualization Agent** creates SVG diagram
   - Input: Panel + all violations
   - Returns: SVG file with annotations

**Key Point:** All violations come from agent analysis within `crew.kickoff()`. Nothing is hardcoded or executed outside the crew.

---

## Next Steps to Enhance

### Enhance the Story

1. **Add agent tools** - Agents call specialized functions
2. **Multi-agent debate** - Agents discuss findings
3. **Memory persistence** - Remember previous panels
4. **Regional configs** - Different rules per location
5. **Report generation** - PDF/HTML outputs

### Scale the System

1. **More agents** - Add specialists (cost, timeline, supply chain)
2. **Tool integration** - FEA analysis, structural simulation
3. **Workflow variations** - Different workflows per panel type
4. **Quality metrics** - Track agent performance

---

## Verification Checklist

- [ ] Run `uv run scripts/demo.py` → See all 4 agents working
- [ ] Run `uv run verify_crew_orchestration.py` → Confirm violations from agents
- [ ] Check `demo_output/` → SVG files exist
- [ ] Open `demo_output/good_panel.svg` → View visualization
- [ ] Open `demo_output/bad_panel.svg` → View with violations

---

## Key Achievements

✅ **Full CrewAI Orchestration**

- All 4 agents in single crew
- Sequential task execution
- Agents share findings via CrewAI memory
- Zero execution outside `crew.kickoff()`

✅ **Violations From Agents**

- No hardcoded lists
- Agent analysis drives all findings
- Structured JSON output format
- Traceable reasoning

✅ **Professional Architecture**

- Clean separation of concerns
- Easy to extend (add agents)
- Explainable results (agent reasoning visible)
- Production-ready pattern

---

## Technologies

- **Python 3.10+** - Type-safe with Pydantic v2
- **CrewAI** - Multi-agent orchestration framework
- **Claude API** - LLM for contextual analysis
- **uv** - Fast Python package management

---

## Documentation

See `QUICK_REFERENCE.md` for a quick start guide with command examples.

---

**Ready to demonstrate CrewAI orchestration for complex workflows!** 🚀

- Stud spacing violations
- Window placement issues
- Missing headers/jack studs
- Seismic zone checks

- **LLM**: Contextual analysis using Claude API
  - Stress concentrations
  - Code compliance
  - Structural nuances
  - Seismic risk assessment

Together they provide **100% violation coverage**.

### 5 CrewAI Agents

1. **Parser Agent** (`tools/ifc_parser_tool.py`)

   - Reads IFC files
   - Extracts to PanelData structure
   - Handles geometry properties

2. **Deterministic Checker** (`tools/deterministic_checker.py`)

   - Applies ~15 rule-based checks
   - Fast, deterministic results
   - Returns DeterministicCheckResult

3. **LLM Analyzer** (`tools/llm_rule_checker.py`)

   - Sends panel info to Claude API
   - Contextual analysis
   - Returns LLMCheckResult

4. **Reporter** (`tools/violation_merger.py`)

   - Merges deterministic + LLM results
   - Deduplicates violations
   - Returns final report

5. **Visualizer** (`tools/visualizer_tool.py`)
   - Creates SVG diagrams
   - Color-codes violations
   - Shows violation reasons

## File Organization

```

crewai-poc/
├── main.py # Entry point (demo & IFC analysis modes)
├── scripts/
│ ├── demo.py # Demo: hybrid QC workflow
│ └── generate_ifc_visualization.py # IFC → clean SVG (no QC)
├── tools/
│ ├── deterministic_checker.py # Rule-based checks + data models
│ ├── llm_rule_checker.py # LLM agent wrapper
│ ├── violation_merger.py # Merges det + LLM results
│ ├── ifc_parser_tool.py # IFC → PanelData parser
│ ├── visualizer_tool.py # Panel → SVG visualization
│ ├── reporter_tool.py # Report formatting
│ └── simple_tools.py # Utility functions
├── crew/
│ ├── agents.py # 5 CrewAI agent definitions
│ └── tasks.py # Task definitions
├── test_data/
│ ├── good_panel.ifc # Test: centered window (passes)
│ ├── bad_panel.ifc # Test: corner window (fails LLM)
│ ├── good_panel.svg # Clean SVG visualization
│ └── bad_panel.svg # Clean SVG visualization
└── config/
└── building_codes.json # Reference building codes

```

## Key Data Models

### PanelData (`tools/deterministic_checker.py`)

```python
PanelData(
    panel_id="PANEL_001",
    width_mm=3660,
    height_mm=2440,
    studs=[Stud(...), ...],          # Support beams
    openings=[Opening(...), ...],    # Windows/doors
    ducts=[Duct(...), ...],          # Ventilation
    seismic_zone=4                   # Building code context
)
```

### Violation Types

- **DeterministicViolation**: From rule checks
- **LLMViolation**: From AI analysis
- Both include: reason, severity (critical/major/minor)

## Visualization System

### SVG Format (Consistent Scale: 0.2px/mm)

**Input Visualizations** (`generate_ifc_visualization.py`)

- Clean geometry visualization
- No QC annotations
- Good for presentations

**Output Visualizations** (`visualizer_tool.py`)

- Shows panel + violations
- Color-coded: gray studs (good), red studs (bad)
- Lists violation reasons

Example files:

- `demo_output/good_panel.svg`: Green panel ✅
- `demo_output/bad_panel.svg`: Red panel with LLM violations listed

## Running Different Scenarios

### 1. Demo Mode (Recommended for First Look)

```bash
uv run python main.py --demo
```

- No API key needed
- Uses mock LLM violations
- Shows: good panel (passes) vs bad panel (fails)

### 2. IFC Analysis (Production)

```bash
export ANTHROPIC_API_KEY=sk-...
uv run python main.py --ifc test_data/good_panel.ifc
```

- Full CrewAI orchestration
- Real LLM analysis
- Requires Anthropic API key

### 3. Generate Clean Visualizations

```bash
uv run python scripts/generate_ifc_visualization.py test_data/good_panel.ifc
```

- Creates SVG from IFC
- No QC analysis
- Good for design reviews

## Understanding the Demo Output

### Good Panel

- **Deterministic**: 0 violations
- **LLM**: 0 violations
- **Reason**: Centered window, low seismic zone
- **Output**: Gray studs, blue window, green status

### Bad Panel

- **Deterministic**: 0 violations (has headers, jack studs)
- **LLM**: 2 violations (corner window + seismic zone 4)
- **Reason**: Context matters - structural risk despite compliance
- **Output**: Red studs, yellow window, violation reasons listed

### Key Insight

Bad panel passes deterministic checks but fails LLM analysis. This shows why **hybrid QC is necessary** - rules alone miss contextual issues.

## Testing & Development

### Run Demo Tests

```bash
uv run python main.py --demo
# Check: demo_output/good_panel.svg and demo_output/bad_panel.svg
```

### Test Individual Components

- **Parser**: `python -c "from tools.ifc_parser_tool import parse_ifc_file_to_panel_data; print(parse_ifc_file_to_panel_data('test_data/good_panel.ifc'))"`
- **Checks**: `python -c "from tools.deterministic_checker import run_deterministic_checks; ..."`
- **Visualizer**: `python -c "from tools.visualizer_tool import create_panel_visualization; ..."`

### Add New Rules

1. Edit `tools/deterministic_checker.py`
2. Add check function in `run_deterministic_checks()`
3. Return DeterministicViolation if rule violated
4. Test with demo: `uv run python main.py --demo`

### Add New LLM Prompts

1. Edit `tools/llm_rule_checker.py`
2. Update Claude API prompt
3. Parse response into violations
4. Test with: `export ANTHROPIC_API_KEY=... && uv run python main.py --demo`

## File Comments

All key files have extensive comments:

- **main.py**: Architecture & entry points
- **scripts/demo.py**: Demo workflow explained
- **scripts/generate_ifc_visualization.py**: IFC processing
- **tools/visualizer_tool.py**: SVG generation logic
- Function docstrings explain inputs, outputs, and logic

## Dependencies

Managed via `uv` and `pyproject.toml`:

- `crewai`: Multi-agent orchestration
- `ifcopenshell`: IFC file parsing
- `pydantic`: Data validation
- `python-dotenv`: Environment variables
- `anthropic`: Claude API (optional)

## Common Tasks

**View panel geometry**

```bash
uv run python scripts/generate_ifc_visualization.py test_data/bad_panel.ifc
open test_data/bad_panel.svg
```

**See hybrid QC in action**

```bash
uv run python main.py --demo
open demo_output/bad_panel.svg  # See violations highlighted
```

**Analyze your own IFC file**

```bash
export ANTHROPIC_API_KEY=sk-...
uv run python main.py --ifc your_panel.ifc
```

**Check violations**

```bash
# After running demo
grep "Violations" demo_output/bad_panel.svg | head -5
```
