"""
Setup script for easy installation and demo
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and print status"""
    print(f"\n{'='*70}")
    print(f"⚙️  {description}")
    print(f"{'='*70}")
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED: {e}")
        return False


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║       CrewAI Wall Panel QC - Setup & Demo                        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)

    print(f"✅ Python {sys.version.split()[0]} detected\n")

    # Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    ):
        print("\n⚠️  Some dependencies failed to install.")
        print("This is often due to WeasyPrint requiring system libraries.")
        print("The system will still work, but PDF generation may fail.")
        print("HTML reports will be generated as a fallback.\n")

    # Create sample IFC file
    if run_command(
        f"{sys.executable} create_sample_ifc.py",
        "Creating sample IFC test file"
    ):
        print("\n" + "="*70)
        print("🎉 Setup Complete!")
        print("="*70)
        print("\n📋 Next steps:")
        print("\n1. Run the demo:")
        print(f"   {sys.executable} main.py --ifc test_data/sample_wall.ifc")
        print("\n2. View results in the 'results/' directory")
        print("\n3. Read README.md for more usage examples")
        print("\n4. Download real IFC files (see test_data/README.md)")
        print("="*70 + "\n")
    else:
        print("\n❌ Setup failed. Please check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
