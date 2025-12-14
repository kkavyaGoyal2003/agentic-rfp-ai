# Agentic RFP AI - Setup Guide

## Step 1: Install Python Dependencies

```bash
# Navigate to the project root directory
cd agentic-rfp-ai

# Install required Python packages
pip install -r requirements.txt
```

## Step 2: Install Ollama

Download and install Ollama from the official website:
👉 **[https://ollama.com/download](https://ollama.com/download)**

Choose your operating system:
- **Windows**: Run the downloaded `.exe` installer
- **macOS**: Run the downloaded `.dmg` file
- **Linux**: Run the installation script

## Step 3: Start Ollama Server

Open a new terminal/command prompt and run:

```bash
ollama serve
```

The server will run at `http://localhost:11434`

## Step 4: Download LLM Model

Open another terminal/command prompt and run:

```bash
ollama pull llama3.2

```


### Test Python integration
```
python test.py
```

