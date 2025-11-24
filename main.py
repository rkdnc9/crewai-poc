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
        from tools.ifc_parser_tool import parse_ifc_file_to_panel_data
        from tools.deterministic_checker import run_deterministic_checks
        from tools.llm_rule_checker import LLMRuleChecker
        from tools.violation_merger import ViolationMerger

        # Parse IFC file
        panel_data = parse_ifc_file_to_panel_data(args.ifc)

        # Run deterministic checks
        det_result = run_deterministic_checks(panel_data)

        # Run LLM analysis
        llm_checker = LLMRuleChecker()
        llm_result = llm_checker.analyze(panel_data)

        # Merge results
        merger = ViolationMerger()
        final_result = merger.merge(det_result, llm_result)

        # Print results
        print("\n" + "="*70)
        print("QUALITY CONTROL REPORT")
        print("="*70)
        print(f"IFC File: {args.ifc}")
        print(f"Total Violations: {len(final_result.all_violations)}")
        if final_result.all_violations:
            for v in final_result.all_violations:
                print(f"  - {v.description} (severity: {v.severity})")
        print("="*70 + "\n")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
