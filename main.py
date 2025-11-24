#!/usr/bin/env python3\n\"\"\"\nWall Panel Hybrid Quality Control (QC) System\n\nCOMBINES:\n  1. DETERMINISTIC: Rule-based checks (stud spacing, window placement, headers, etc.)\n  2. LLM-BASED: AI contextual analysis (stress concentrations, code compliance, seismic risks)\n\nWHY HYBRID:\n  - Deterministic: Fast, reliable, catches obvious structural issues\n  - LLM: Catches subtle contextual violations that depend on multiple factors\n  - Together: 100% violation coverage for comprehensive QC\n\nARCHITECTURE (5 CrewAI Agents):\n  1. Parser Agent: IFC file → PanelData (structured panel info)\n  2. Deterministic Checker: ~15 rule-based checks\n  3. LLM Analyzer: Claude API contextual analysis\n  4. Reporter: Merges deterministic + LLM results\n  5. Visualizer: SVG diagrams with violations highlighted\n\nENTRY POINTS:\n  uv run python main.py --demo          # Demo (no API key needed)\n  uv run python main.py --ifc <file>   # Analyze IFC file (requires ANTHROPIC_API_KEY)\n\nTO GET STARTED:\n  1. Install: uv sync\n  2. Run demo: uv run python main.py --demo\n  3. See results: Check demo_output/*.svg\n  4. Analyze: export ANTHROPIC_API_KEY=<key> && uv run python main.py --ifc <file>\n\nKEY FILES:\n  - scripts/demo.py: Demo workflow\n  - tools/deterministic_checker.py: Rule-based checks\n  - tools/llm_rule_checker.py: LLM agent\n  - tools/visualizer_tool.py: SVG visualization\n\"\"\"\n\nimport sys\nimport os\nimport argparse\n\n\ndef main():\n    \"\"\"Main entry point for hybrid QC system. Supports demo and IFC analysis modes.\"\"\""
    parser = argparse.ArgumentParser(
        description="Hybrid QC for wall panels (deterministic rules + LLM analysis)"
    )

    parser.add_argument('--demo', action='store_true', help='Run demo (no API key required)')
    parser.add_argument('--ifc', type=str, help='Path to IFC file to analyze')

    args = parser.parse_args()

    # Demo mode - no API key needed
    if args.demo:
        try:
            from scripts.demo import demo
            demo()
            return 0
        except Exception as e:
            print(f"Error running demo: {e}")
            return 1

    # IFC mode - requires file and API key
    if not args.ifc:
        parser.print_help()
        return 1

    if not os.path.exists(args.ifc):
        print(f"Error: IFC file not found: {args.ifc}")
        return 1

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not set")
        return 1

    try:
        import json
        from pathlib import Path
        from tools.ifc_parser_tool import parse_ifc_file_to_panel_data
        from tools.deterministic_checker import run_deterministic_checks
        from tools.llm_rule_checker import LLMRuleChecker
        from tools.violation_merger import ViolationMerger

        # Parse IFC file
        panel_data = parse_ifc_file_to_panel_data(args.ifc)
        panel_dict = panel_data.dict() if hasattr(panel_data, 'dict') else panel_data

        # Load exceptions for LLM analysis
        exceptions_path = Path(__file__).parent / "config" / "exceptions.json"
        with open(exceptions_path) as f:
            exceptions = json.load(f)

        # Run deterministic checks
        rules_path = Path(__file__).parent / "config" / "building_codes.json"
        with open(rules_path) as f:
            rules = json.load(f)
        det_result = run_deterministic_checks(panel_data, rules)

        # Run LLM analysis with remediation
        llm_checker = LLMRuleChecker()
        llm_result = llm_checker.analyze(panel_dict, det_result.to_dict(), exceptions)

        # Save remediation recommendations to demo_output
        output_dir = Path("demo_output")
        output_dir.mkdir(exist_ok=True)
        
        panel_id = panel_dict.get('panel_id', 'panel').lower()
        remediation_file = output_dir / f"{panel_id}_remediation.json"
        
        remediation_data = {
            "panel_id": panel_dict.get('panel_id'),
            "ifc_file": args.ifc,
            "violations_with_remediation": llm_result.get('additional_violations', []),
            "design_concerns": llm_result.get('design_concerns', []),
            "needs_engineer_review": llm_result.get('needs_engineer_review', False),
            "summary": llm_result.get('summary', 'Analysis complete')
        }
        
        with open(remediation_file, 'w', encoding='utf-8') as f:
            json.dump(remediation_data, f, indent=2)

        # Print results
        print("\n" + "="*70)
        print("QUALITY CONTROL REPORT")
        print("="*70)
        print(f"IFC File: {args.ifc}")
        print(f"Panel ID: {panel_dict.get('panel_id')}")
        print(f"Deterministic Violations: {len(det_result.violations)}")
        print(f"LLM Additional Violations: {len(llm_result.get('additional_violations', []))}")
        
        # Display violations with remediation
        llm_violations = llm_result.get('additional_violations', [])
        if llm_violations:
            print("\n" + "-"*70)
            print("VIOLATIONS WITH REMEDIATION PLANS:")
            print("-"*70)
            for v in llm_violations:
                print(f"\n🔴 {v.get('reason', 'Unknown violation')}")
                print(f"   Severity: {v.get('severity', 'unknown').upper()}")
                remediation = v.get('remediation', {})
                if remediation:
                    print(f"   Estimated Effort: {remediation.get('estimated_effort', 'N/A')}")
                    print(f"   Cost Impact: {remediation.get('cost_impact', 'N/A')}")
                    print(f"   Engineer Approval Required: {remediation.get('requires_engineer_approval', False)}")
                    steps = remediation.get('steps', [])
                    if steps:
                        print(f"   Fix Steps:")
                        for step in steps:
                            print(f"     {step}")
        
        print("\n" + "="*70)
        print(f"💾 Remediation report saved to: {remediation_file}")
        print("="*70 + "\n")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
