# 🚀 QuickStart Guide - Get Running in 5 Minutes

## ✅ What's Done

- All dependencies installed
- Tools fixed to use correct CrewAI API
- WeasyPrint issue handled (will generate HTML reports instead of PDF - totally fine!)
- `.env` file created

## 🔑 Step 1: Add Your OpenAI API Key

**You MUST do this step before running the POC!**

### Get API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### Add to .env File

Edit the `.env` file in the project root:

```bash
# Open .env in notepad or your favorite editor
notepad .env
```

Change this line:
```
OPENAI_API_KEY=sk-your-openapi-key-here
```

To your actual key:
```
OPENAI_API_KEY=sk-proj-abc123...your-actual-key
```

Save and close the file.

### Choose Model (Optional)

By default, it uses GPT-4. To save money during testing, you can use GPT-3.5-turbo:

```
OPENAI_MODEL_NAME=gpt-3.5-turbo
```

**Cost comparison:**
- GPT-4: ~$0.50 per run (best quality)
- GPT-3.5-turbo: ~$0.10 per run (good quality, 5x cheaper)

## 📝 Step 2: Generate Test Data

```bash
python create_sample_ifc.py
```

This creates `test_data/sample_wall.ifc` with intentional code violations for testing.

## 🤖 Step 3: Run the POC!

```bash
python main.py --ifc test_data/sample_wall.ifc
```

## 📊 What to Expect

The system will:
1. Check your API key (ERROR if missing - go back to Step 1!)
2. Start 4 AI agents working sequentially:
   - **Parser** - Extracts wall panel data from IFC
   - **RuleChecker** - Validates against building codes
   - **Visualiser** - Creates PNG diagrams with violations marked in red
   - **Reporter** - Generates HTML report (PDF if GTK+ installed)
3. Save results to `results/` directory

**Expected output files:**
- `panel_01_visualization.png` - First panel diagram
- `panel_02_visualization.png` - Second panel diagram
- `panel_qc_report.html` - Executive report (or .pdf if GTK+ available)

**Processing time:** ~45-90 seconds (depends on OpenAI API response time)

## ⚠️ Common Issues

### Issue 1: "OpenAI API Key Not Found"

**Solution:** You forgot Step 1! Edit `.env` and add your API key.

### Issue 2: "Rate limit exceeded"

**Solution:** Your OpenAI account hit the rate limit. Wait a few minutes or upgrade your plan.

### Issue 3: PDF generation not working

**This is NORMAL on Windows!** The system automatically generates HTML reports instead.
HTML reports have the exact same information and look great in any browser.

To get PDF support (optional):
- Download and install GTK+ from https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

### Issue 4: Slow processing

**This is normal for the first run!** CrewAI agents need to:
- Load models
- Parse IFC files
- Make API calls to OpenAI
- Generate visualizations

Typical timing:
- Fast run: 45 seconds
- Slow run: 2-3 minutes (depends on OpenAI API load)

## 💰 Cost Information

Each run costs approximately:
- **GPT-4**: $0.30 - $0.70 per run
- **GPT-3.5-turbo**: $0.05 - $0.15 per run

The POC sample file should cost less than $0.50 to run with GPT-4.

## 📚 Next Steps

### Test with Real IFC Files

Once the sample works, try your own IFC files:

```bash
python main.py --ifc path/to/your/model.ifc
```

### Customize Building Codes

Edit `config/building_codes.json` to match your local codes:

```json
{
  "stud_spacing": {
    "rules": {
      "standard_spacing_mm": 406.4,  // Change these values
      "tolerance_mm": 6.35
    }
  }
}
```

### Use Different Models

In `.env`:
- `gpt-4` - Best quality, most expensive
- `gpt-3.5-turbo` - Good quality, 5x cheaper
- `gpt-4-turbo` - Medium cost, good speed

### Scale Up

Process multiple files:
```bash
for file in *.ifc; do
  python main.py --ifc "$file" --output "results_${file%.*}"
done
```

## 🎯 Verification Checklist

Before reporting issues, verify:

- [ ] OpenAI API key is set in `.env` file
- [ ] API key starts with `sk-`
- [ ] You have credits in your OpenAI account
- [ ] You're running from the project directory
- [ ] Sample IFC file exists (`test_data/sample_wall.ifc`)
- [ ] Python environment has all dependencies installed

## 📖 Full Documentation

- **README.md** - Complete usage guide
- **LLM_SETUP.md** - Detailed API configuration
- **CONDA_SETUP.md** - Conda environment setup
- **DEMO.md** - Demo presentation guide

## 🆘 Getting Help

1. Check `LLM_SETUP.md` for API key issues
2. Check `CONDA_SETUP.md` for environment issues
3. Review error messages - they're designed to be helpful!
4. Make sure you followed Step 1 (API key)!

## ✅ Success Indicators

You'll know it's working when you see:

```
✅ OpenAI API key found: sk-proj-...
🤖 Using model: gpt-4

🚀 Initializing AI agents...

[Agent output...]

✅ Quality control completed successfully!
```

And you have files in `results/` directory.

---

**Ready?**

1. Add API key to `.env`
2. `python create_sample_ifc.py`
3. `python main.py --ifc test_data/sample_wall.ifc`

That's it! 🚀
