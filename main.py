#!/usr/bin/env python3
"""
CrewAI Wall Panel QC - Main Entry Point
Automated design review for prefab wall panels

Usage:
    python main.py --ifc path/to/model.ifc
    python main.py --ifc path/to/model.ifc --output results_custom
"""

import sys
import os
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv
from crew import create_qc_crew

# Load environment variables
load_dotenv()


def check_api_key():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("\n" + "="*70)
        print("ERROR: OpenAI API Key Not Found")
        print("="*70)
        print("\nCrewAI requires an OpenAI API key to function.")
        print("\nTo fix this:")
        print("\n1. Get an API key from: https://platform.openai.com/api-keys")
        print("\n2. Create a .env file in the project directory:")
        print("   Copy .env.example to .env")
        print("   Add your key: OPENAI_API_KEY=sk-your-key-here")
        print("\n3. Or set environment variable:")
        print("   Windows: setx OPENAI_API_KEY \"sk-your-key-here\"")
        print("   Linux/Mac: export OPENAI_API_KEY=\"sk-your-key-here\"")
        print("\n💡 Alternative: Use local LLM (see README.md for Ollama setup)")
        print("="*70 + "\n")
        return False

    # Validate key format
    if not api_key.startswith('sk-'):
        print(f"\nWarning: API key format looks incorrect")
        print(f"   OpenAI keys typically start with 'sk-'")
        print(f"   Current value starts with: {api_key[:5]}...")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return False

    print(f"OpenAI API key found: {api_key[:8]}...{api_key[-4:]}")
    model = os.getenv('OPENAI_MODEL_NAME', 'gpt-4')
    print(f"Using model: {model}\n")

    return True


def print_banner():
    """Print application banner"""
    banner = """
===================================================================

      CrewAI Wall Panel Quality Control System

      Automated Design Review for Prefab Wall Panels
      Powered by AI Agents & Building Code Intelligence

===================================================================
    """
    print(banner)


def validate_ifc_file(file_path: str) -> bool:
    """Validate that the IFC file exists and is readable"""
    if not os.path.exists(file_path):
        print(f"Error: IFC file not found: {file_path}")
        return False

    if not file_path.lower().endswith('.ifc'):
        print(f"Warning: File does not have .ifc extension: {file_path}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return False

    return True


def print_results_summary(output_dir: str):
    """Print summary of generated files"""
    print("\n" + "="*70)
    print("📊 Generated Files:")
    print("="*70)

    results_path = Path(output_dir)
    if results_path.exists():
        files = list(results_path.glob("*"))
        if files:
            for file in sorted(files):
                file_size = file.stat().st_size / 1024  # KB
                print(f"  {file.name} ({file_size:.1f} KB)")
        else:
            print("  Warning: No files generated")
    else:
        print("  Warning: Results directory not created")

    print("="*70 + "\n")


def main():
    """Main entry point"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="CrewAI Wall Panel Quality Control - Automated Design Review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --ifc test_data/sample_house.ifc
  python main.py --ifc models/panel_01.ifc --output results_panel_01

For more information, visit: https://github.com/yourusername/crewai-wall-panel-qc
        """
    )

    parser.add_argument(
        '--ifc',
        type=str,
        required=True,
        help='Path to the IFC building model file to analyze'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='results',
        help='Output directory for results (default: results)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output from agents'
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Check API key configuration
    if not check_api_key():
        sys.exit(1)

    # Validate input file
    print(f"Input File: {args.ifc}")
    print(f"Output Directory: {args.output}\n")

    if not validate_ifc_file(args.ifc):
        sys.exit(1)

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    try:
        # Record start time
        start_time = time.time()

        print("Initializing AI agents...\n")

        # Create and run the crew
        crew = create_qc_crew(
            ifc_file_path=args.ifc,
            output_dir=args.output
        )

        result = crew.run()

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Print results summary
        print_results_summary(args.output)

        print(f"Total Execution Time: {elapsed_time:.1f} seconds\n")

        print("Quality control completed successfully!")
        print(f"Results saved to: {os.path.abspath(args.output)}\n")

        return 0

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        return 130

    except Exception as e:
        print(f"\n\nError during quality control: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
