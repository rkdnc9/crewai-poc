# 🤖 LLM Configuration Guide for CrewAI POC

This guide explains how to configure the AI models for the CrewAI Wall Panel QC system.

## 🎯 Quick Summary

**Default LLM**: OpenAI GPT-4 or GPT-3.5-turbo
**Required**: OpenAI API Key
**Cost per run**: ~$0.10-$0.50 (depending on model and panel complexity)

## 📋 Setup Steps

### 1. Get an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. **Important**: Save it securely - you can't view it again!

### 2. Configure the API Key

**Option A: Using .env file (Recommended)**

```bash
# 1. Copy the example file
cp .env.example .env

# Windows alternative:
copy .env.example .env

# 2. Edit .env and add your key
# Open .env in a text editor and replace:
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL_NAME=gpt-4
```

**Option B: System Environment Variable**

**Windows:**
```bash
setx OPENAI_API_KEY "sk-your-actual-key-here"
# Restart your terminal after this
```

**Linux/Mac:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY="sk-your-actual-key-here"

# Or for current session only:
export OPENAI_API_KEY="sk-your-actual-key-here"
```

**Option C: Conda Environment Variable**

```bash
# Activate your environment
conda activate crewai-poc

# Set the variable for this environment
conda env config vars set OPENAI_API_KEY=sk-your-actual-key-here

# Reactivate environment for changes to take effect
conda deactivate
conda activate crewai-poc
```

### 3. Verify Configuration

```bash
# Windows
echo %OPENAI_API_KEY%

# Linux/Mac
echo $OPENAI_API_KEY

# Python check
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('OPENAI_API_KEY')[:10] + '...')"
```

## 🎛️ Model Selection

### GPT-4 (Default - Recommended)

```bash
# In .env file
OPENAI_MODEL_NAME=gpt-4
```

**Pros:**
- Most capable model
- Best accuracy for code interpretation
- Better handling of complex validation logic

**Cons:**
- More expensive (~$0.50/run)
- Slower than GPT-3.5

**Best for:** Production use, critical validations

### GPT-3.5-turbo (Budget Option)

```bash
# In .env file
OPENAI_MODEL_NAME=gpt-3.5-turbo
```

**Pros:**
- Much cheaper (~$0.10/run)
- Faster responses
- Still very capable

**Cons:**
- Less accurate on complex reasoning
- May miss subtle violations

**Best for:** Testing, demos, high-volume processing

### Cost Comparison

| Model | Cost per Run | Speed | Accuracy |
|-------|--------------|-------|----------|
| GPT-4 | ~$0.50 | Slower | Excellent |
| GPT-3.5-turbo | ~$0.10 | Faster | Good |
| GPT-4-turbo | ~$0.30 | Medium | Excellent |

**Note**: Actual costs depend on panel complexity and number of violations found.

## 🆓 Free/Local Alternatives

### Option 1: Using Ollama (Local LLM - FREE)

Run models locally on your machine - no API costs!

**1. Install Ollama**

Download from: https://ollama.ai/

**2. Pull a model**

```bash
# Recommended models:
ollama pull llama2          # 7B - Fast, decent quality
ollama pull mistral         # 7B - Better reasoning
ollama pull codellama       # 7B - Better with technical content
ollama pull llama2:13b      # 13B - Better quality, slower
```

**3. Configure CrewAI to use Ollama**

Update your `.env` file:

```bash
# Comment out OpenAI
# OPENAI_API_KEY=sk-...

# Configure Ollama
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

**4. Update agent configuration**

You'll need to modify the agents to use Ollama. Add to `crew.py`:

```python
import os
from langchain.llms import Ollama

# After load_dotenv()
llm = None
if os.getenv('OLLAMA_MODEL'):
    llm = Ollama(
        model=os.getenv('OLLAMA_MODEL', 'mistral'),
        base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    )
```

Then pass `llm=llm` to each agent creation.

**Pros:**
- Completely free
- No data leaves your machine
- No API rate limits

**Cons:**
- Requires powerful computer (16GB+ RAM recommended)
- Slower than cloud APIs
- Lower accuracy than GPT-4

### Option 2: Using LM Studio (Local - FREE)

Alternative to Ollama with GUI:

1. Download from https://lmstudio.ai/
2. Download a model (Mistral, Llama2, etc.)
3. Start local server
4. Configure similar to Ollama above

## 🔐 Security Best Practices

### DO:
✅ Use `.env` file for API keys
✅ Add `.env` to `.gitignore` (already done)
✅ Rotate keys regularly
✅ Use environment-specific keys (dev/prod)
✅ Set spending limits in OpenAI dashboard

### DON'T:
❌ Commit API keys to git
❌ Share keys in chat/email
❌ Use production keys for testing
❌ Store keys in code files
❌ Share your `.env` file

## 💰 Cost Management

### Monitor Usage

Check your usage at: https://platform.openai.com/usage

### Set Spending Limits

1. Go to https://platform.openai.com/account/billing/limits
2. Set monthly budget
3. Enable email alerts

### Optimize Costs

**For Development:**
- Use GPT-3.5-turbo
- Test with small IFC files
- Use local models (Ollama)

**For Production:**
- Use GPT-4 for final validation
- Batch process multiple panels
- Cache common results

### Estimated Costs

Based on typical usage:

| Scenario | Model | Cost/Panel | Cost/100 Panels |
|----------|-------|------------|-----------------|
| Development | GPT-3.5 | $0.10 | $10 |
| Production | GPT-4 | $0.50 | $50 |
| High Volume | GPT-4-turbo | $0.30 | $30 |
| Local/Free | Ollama | $0.00 | $0.00 |

## 🔧 Advanced Configuration

### Using Azure OpenAI

```bash
# In .env file
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Using Anthropic Claude

```bash
# In .env file
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Requires modifying agents to use Claude instead of OpenAI.

### Custom Model Parameters

You can configure model parameters by modifying the agent creation. Example:

```python
from crewai import Agent
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.1,      # Lower = more deterministic
    max_tokens=4096,      # Max response length
    timeout=120           # Request timeout
)

agent = Agent(
    role="...",
    goal="...",
    backstory="...",
    llm=llm,
    tools=[...]
)
```

## 🐛 Troubleshooting

### Error: "OpenAI API key not found"

**Solution**: Check that your `.env` file exists and contains the key.

```bash
# Verify .env file exists
ls -la .env

# Check content (be careful not to share output!)
cat .env
```

### Error: "Incorrect API key provided"

**Solution**: Verify your key is correct and active.

1. Check for extra spaces or quotes
2. Verify key at https://platform.openai.com/api-keys
3. Try regenerating the key

### Error: "Rate limit exceeded"

**Solution**: You've hit OpenAI's rate limit.

- Wait a few minutes and try again
- Upgrade your OpenAI plan
- Use a different model
- Switch to local model (Ollama)

### Error: "Insufficient credits"

**Solution**: Add credits to your OpenAI account.

https://platform.openai.com/account/billing

### Slow Response Times

**Solutions:**
- Switch to GPT-3.5-turbo
- Use local model (Ollama)
- Check your internet connection
- Try during off-peak hours

## 📊 Testing Your Configuration

Run this test script to verify everything is working:

```python
# test_llm_config.py
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew

load_dotenv()

print("Testing LLM Configuration...")
print(f"API Key: {os.getenv('OPENAI_API_KEY', 'NOT FOUND')[:10]}...")
print(f"Model: {os.getenv('OPENAI_MODEL_NAME', 'gpt-4')}")

# Simple test agent
agent = Agent(
    role="Test Agent",
    goal="Respond to a test query",
    backstory="You are a test agent",
    verbose=True
)

task = Task(
    description="Say 'Configuration working!' in 3 words or less.",
    expected_output="A brief confirmation message",
    agent=agent
)

crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()

print("\n✅ Configuration test successful!")
print(f"Response: {result}")
```

Run it:
```bash
python test_llm_config.py
```

## 📞 Support

If you're still having issues:

1. **Check OpenAI Status**: https://status.openai.com/
2. **Review Logs**: Look for error messages in terminal output
3. **Documentation**: https://docs.crewai.com/
4. **OpenAI Help**: https://help.openai.com/

---

## ✅ Quick Checklist

Before running the POC, verify:

- [ ] OpenAI API key obtained
- [ ] `.env` file created with API key
- [ ] Model selected (GPT-4 or GPT-3.5-turbo)
- [ ] API key validated (run test script)
- [ ] Spending limits set (optional but recommended)
- [ ] `.env` in `.gitignore` (for security)

**Ready to go?** Run: `python main.py --ifc test_data/sample_wall.ifc`
