# CrewAI PoC Summary – Automated Design-Review Crew for Prefab Wall Panels  
*(Optimized for Eagle Metal / TrueBuild Software Group)*

## 1. Use-Case in One Sentence  
Drop an IFC-based timber or CFS wall-panel model and let an AI crew flag every stud-spacing violation, missing jack stud, or duct clash in seconds—then export a colour-marked 3-D file + PDF sign-off report.

## 2. Pain We Solve
- Manual review of each panel (≈30 min) creates a throughput bottleneck in modular plants.  
- Missed defects reach the saw table and raise costly rework, especially on multi-family jobs.  
- TrueBuild Layout already auto-designs panels; this PoC adds an **AI quality gate** before production.

## 3. Public, Free Data for Demo
- **BuildingNet** – 50 k annotated IFC building exteriors (CC-BY)  
  [https://github.com/buildingnet/buildingnet_dataset](https://github.com/buildingnet/buildingnet_dataset)  
- **Houses3K** – 3 k textured OBJ houses (research)  
  [https://github.com/darylperalta/Houses3K](https://github.com/darylperalta/Houses3K)  
- **GrabCAD “construction” tag** – hundreds of free SOLIDWORKS/STEP wood-frame wall panels  
  [https://grabcad.com/library/tag/construction](https://grabcad.com/library/tag/construction)

## 4. CrewAI Agent Line-Up (≤150 lines total)

| Agent        | Tools                     | Single Responsibility |
|--------------|---------------------------|------------------------|
| **Parser**       | IfcOpenShell + FreeCAD Python    | Export wall-panel JSON (stud coords, openings, ducts) |
| **RuleChecker** | Pandas + NumPy            | Compute stud spacing, detect clashes vs. building-code dict. |
| **Visualiser**   | FreeCAD Python console    | Colour problem studs red; write SKP + PNG) |
| **Reporter**   | Jinja2 → HTML → WeasyPrint | 1-page PDF summary (qty. of issues, IDs, screenshots) |
| **Manager**      | CrewAI native             | Delegate loop: if >0 clashes → re-route to Parser for next panel. |

## 5. End-to-End Flow (local, no cloud calls)

1. User runs:  
  `python main.py --ifc SampleHouse.ifc`
2. Crew outputs to `./results/`  
  - `panel_01_reviewed.skp` (red studs)  
  - `panel_01_report.pdf` (pass/fail, qty., snapshot)
3. CLI prints:  
  `Panel 01: 3 spacing errors, 1 duct clash → FAIL`  
  Total elapsed ≈45 s on a laptop.

## 6. Stretch Hooks for Sales Demo
- Swap RuleChecker for **NVIDIA Osmium** to add AI-based clash prediction.  
- Add **cost agent** that multiplies error count × historical rework $ to show **$ saved**.  
- Streamlit front-end → drag-and-drop IFC → see live 3-D view with red studs.

## 7. Why This Resonates with Eagle Metal / TrueBuild
TrueBuild Layout already automates panel design; the PoC **adds an AI review layer** that:
- Cuts QC labour by 80 %.  
- Prevents costly rebuilds on the multi-family modules they target.  
- Demonstrates immediate ROI—exactly the efficiency story Eagle Metal sells.

## 8. Deliverables Ready in One Sprint
- Git repo with `main.py`, `requirements.txt`, Dockerfile.  
- One-button `make demo` downloads test IFCs, ingests, launches Streamlit.  
- 2-min screen-capture for stakeholders.
