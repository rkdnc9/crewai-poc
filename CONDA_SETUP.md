# 🐍 Conda Setup Guide for CrewAI POC

Complete guide for setting up and running the CrewAI Wall Panel QC system with Conda.

## 📋 Prerequisites

- Conda or Miniconda installed
- OpenAI API key (get from https://platform.openai.com/api-keys)

## 🚀 Quick Start (5 Steps)

```bash
# 1. Create conda environment
conda create -n crewai-poc python=3.10 -y

# 2. Activate environment
conda activate crewai-poc

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
# Edit .env and add your OpenAI API key

# 5. Run demo
python create_sample_ifc.py
python main.py --ifc test_data/sample_wall.ifc
```

## 📖 Detailed Setup

### Step 1: Create Conda Environment

```bash
# Create environment with Python 3.10
conda create -n crewai-poc python=3.10 -y

# Verify creation
conda env list
```

You should see `crewai-poc` in the list.

### Step 2: Activate Environment

```bash
# Activate the environment
conda activate crewai-poc

# Your prompt should now show: (crewai-poc)
```

**Important**: You must activate this environment every time you work on the project!

### Step 3: Install Dependencies

**Option A: Quick Install (using pip)**

```bash
# Install all dependencies
pip install -r requirements.txt
```

**Option B: Optimized Install (using conda + pip)**

Some packages work better when installed via conda:

```bash
# Install scientific computing packages via conda
conda install -c conda-forge numpy pandas matplotlib pillow -y

# Install remaining packages via pip
pip install crewai crewai-tools ifcopenshell weasyprint jinja2 click python-dotenv pydantic
```

### Step 4: Configure OpenAI API Key

**Get API Key:**
1. Go to https://platform.openai.com/api-keys
2. Create account or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

**Set API Key in Conda Environment:**

```bash
# Method 1: Using conda env vars (Recommended for conda)
conda activate crewai-poc
conda env config vars set OPENAI_API_KEY=sk-your-actual-key-here
conda env config vars set OPENAI_MODEL_NAME=gpt-4

# Reactivate for changes to take effect
conda deactivate
conda activate crewai-poc

# Verify
conda env config vars list
```

**Alternative: Using .env file**

```bash
# Copy example file
cp .env.example .env

# Edit .env file
# Add your key: OPENAI_API_KEY=sk-your-key-here
```

### Step 5: Generate Test Data

```bash
python create_sample_ifc.py
```

Expected output:
```
✅ Sample IFC file created: test_data/sample_wall.ifc
📏 Contains:
   - 2 wall panels
   - 1 door opening
   - 1 HVAC duct
```

### Step 6: Run the POC

```bash
python main.py --ifc test_data/sample_wall.ifc
```

Expected output:
```
╔═══════════════════════════════════════════════════════════════════╗
║       🤖 CrewAI Wall Panel Quality Control System 🤖              ║
╚═══════════════════════════════════════════════════════════════════╝

✅ OpenAI API key found: sk-proj-...
🤖 Using model: gpt-4

📁 Input File: test_data/sample_wall.ifc
📂 Output Directory: results

[... agents processing ...]

✅ Quality control completed successfully!
```

## 🔧 Environment Management

### Daily Workflow

```bash
# Start working
conda activate crewai-poc

# Run the POC
python main.py --ifc test_data/sample_wall.ifc

# When done
conda deactivate
```

### Updating Dependencies

```bash
conda activate crewai-poc

# Update a specific package
pip install --upgrade crewai

# Update all packages
pip install --upgrade -r requirements.txt
```

### Environment Information

```bash
# List all conda environments
conda env list

# Show packages in current environment
conda list

# Show pip packages
pip list

# Show environment variables
conda env config vars list
```

### Exporting Environment

Share your exact setup with others:

```bash
# Export conda environment
conda env export > environment.yml

# Export pip requirements
pip freeze > requirements-frozen.txt
```

### Creating from Export

```bash
# Create from conda export
conda env create -f environment.yml

# Or create and install from frozen requirements
conda create -n crewai-poc python=3.10 -y
conda activate crewai-poc
pip install -r requirements-frozen.txt
```

### Removing Environment

```bash
# Deactivate if active
conda deactivate

# Remove environment
conda env remove -n crewai-poc

# Verify removal
conda env list
```

## 🐛 Troubleshooting

### Issue: "conda: command not found"

**Solution**: Conda is not installed or not in PATH.

```bash
# Install Miniconda
# Download from: https://docs.conda.io/en/latest/miniconda.html

# After installation, restart terminal
```

### Issue: Environment activation doesn't work

**Solution**: Initialize conda for your shell.

```bash
# Windows (PowerShell)
conda init powershell

# Windows (CMD)
conda init cmd.exe

# Linux/Mac (bash)
conda init bash

# Restart terminal
```

### Issue: "No module named 'crewai'"

**Solution**: Dependencies not installed or wrong environment.

```bash
# Verify you're in the right environment
conda activate crewai-poc

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: API key not found after setting with conda env vars

**Solution**: Reactivate environment.

```bash
conda deactivate
conda activate crewai-poc

# Verify
python -c "import os; print('API Key:', os.getenv('OPENAI_API_KEY')[:10])"
```

### Issue: WeasyPrint PDF generation fails

**Solution**: Use HTML output (automatic fallback) or install system dependencies.

**Windows:**
```bash
# Download and install GTK+
# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
```

**Linux:**
```bash
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0
```

**Mac:**
```bash
brew install pango
```

## 💡 Tips & Best Practices

### Tip 1: Use Conda Environments for Isolation

Each project should have its own environment to avoid dependency conflicts.

### Tip 2: Keep Environment Updated

```bash
conda activate crewai-poc
conda update conda
pip install --upgrade pip
```

### Tip 3: Document Your Environment

```bash
# Create environment.yml for sharing
conda env export --no-builds > environment.yml
```

### Tip 4: Use Environment-Specific API Keys

Set different API keys for dev/test/prod:

```bash
# Development
conda env config vars set OPENAI_API_KEY=sk-dev-key...

# Production (different environment)
conda create -n crewai-poc-prod python=3.10 -y
conda activate crewai-poc-prod
conda env config vars set OPENAI_API_KEY=sk-prod-key...
```

### Tip 5: Automate Activation

Add to your shell config:

```bash
# ~/.bashrc or ~/.zshrc
alias crewai='conda activate crewai-poc && cd ~/projects/crewai-poc'
```

Then just type `crewai` to activate and navigate!

## 📊 Verifying Installation

Run this test script:

```python
# test_installation.py
import sys
print(f"Python: {sys.version}")

try:
    import crewai
    print(f"✅ CrewAI: {crewai.__version__}")
except ImportError as e:
    print(f"❌ CrewAI: {e}")

try:
    import ifcopenshell
    print(f"✅ IfcOpenShell: {ifcopenshell.version}")
except ImportError as e:
    print(f"❌ IfcOpenShell: {e}")

try:
    import pandas
    print(f"✅ Pandas: {pandas.__version__}")
except ImportError as e:
    print(f"❌ Pandas: {e}")

try:
    import matplotlib
    print(f"✅ Matplotlib: {matplotlib.__version__}")
except ImportError as e:
    print(f"❌ Matplotlib: {e}")

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"✅ OpenAI API Key: {api_key[:8]}...{api_key[-4:]}")
else:
    print("❌ OpenAI API Key: Not found")

print("\n✅ All checks passed!" if api_key else "\n⚠️  Missing API key")
```

Run it:
```bash
conda activate crewai-poc
python test_installation.py
```

## 🎯 Complete Example Session

```bash
# Day 1: Initial Setup
conda create -n crewai-poc python=3.10 -y
conda activate crewai-poc
pip install -r requirements.txt
conda env config vars set OPENAI_API_KEY=sk-your-key
conda deactivate
conda activate crewai-poc
python create_sample_ifc.py
python main.py --ifc test_data/sample_wall.ifc

# Day 2+: Daily Usage
conda activate crewai-poc
python main.py --ifc path/to/your/model.ifc
# ... work ...
conda deactivate

# Updating
conda activate crewai-poc
pip install --upgrade crewai
conda deactivate

# Sharing with team
conda env export > environment.yml
# Team member: conda env create -f environment.yml
```

## 📚 Additional Resources

- **Conda Documentation**: https://docs.conda.io/
- **Managing Environments**: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
- **CrewAI Docs**: https://docs.crewai.com/
- **Python-dotenv**: https://pypi.org/project/python-dotenv/

## ✅ Checklist

Before running the POC:

- [ ] Conda installed and working
- [ ] Environment created: `crewai-poc`
- [ ] Environment activated
- [ ] All dependencies installed
- [ ] OpenAI API key configured
- [ ] API key verified
- [ ] Sample data generated
- [ ] Test run successful

**Ready?** Run: `python main.py --ifc test_data/sample_wall.ifc`

---

**Need help?** Check `LLM_SETUP.md` for detailed API configuration and `README.md` for general usage.
