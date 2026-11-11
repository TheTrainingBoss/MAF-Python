![MAF Python](./media/MAF-Python.png)

# Mastering Microsoft Agent Framework in Python

Welcome to **Mastering Microsoft Agent Framework in Python**, a hands-on, lab-driven course that teaches you how to build production-ready AI agents with [Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/) (MAF).

This repo is intended to accompany the full online video course with full demonstrations on the [Training Boss website](https://thetrainingboss.com/course/microsoft-agent-framework-fundamentals-in-python/) 

Every lab is a small, self-contained Python script that you can read in a few minutes and run on its own. The labs build on each other: you start by connecting to a model, then add streaming, chat loops, tools, MCP servers, middleware, structured output, embeddings and RAG, multimodal input and output, and context providers.

> 📚 **This course keeps growing.** New labs are added regularly. Watch or star the repository so you get notified when new labs are published.

---

## What you will learn

By the end of the course you will be able to:

- **Connect agents to any model provider:** OpenAI, Azure OpenAI, Anthropic, Google Gemini, xAI Grok, Mistral, and Microsoft Foundry, all through one `Agent` abstraction.
- **Run models locally** with Ollama and Foundry Local (CPU, GPU, or NPU), with no cloud account required.
- **Stream responses** token by token and build interactive console chat experiences.
- **Track token usage**, including input, output, and reasoning tokens.
- **Shape agent behavior** with instructions, personas, and default options such as `max_tokens` and reasoning effort.
- **Give agents tools** with Python function calling (`@tool`), hosted tools such as Code Interpreter and Web Search, and remote tools through the **Model Context Protocol (MCP)**.
- **Download files** that the Code Interpreter generates, such as charts.
- **Intercept and control execution** with function middleware for logging, auditing, and guardrails.
- **Compose agents** by exposing one agent as a tool of another (agent-as-a-tool).
- **Get typed, structured output** from an agent with Pydantic models and `response_format`.
- **Generate embeddings** and measure semantic similarity with cosine similarity.
- **Store and search vectors** in Azure AI Search with `AzureAISearchStore` and `@vectorstoremodel`.
- **Build Retrieval-Augmented Generation (RAG)**, first by injecting search results into the prompt, then agentically by giving the agent a search tool.
- **Work with multimodal content:** send images and PDFs to a model, and generate images with the hosted image generation tool.
- **Enrich every run** with a custom `ContextProvider` that injects instructions and tools before the LLM call and processes the result after it.
- In upcoming labs, you'll also work with memory, workflows, multi-agent orchestration, observability, evaluation, and deployment. See [Roadmap](#roadmap).

---

## Lab catalog

| #  | Lab | What it covers | Provider / requirement |
|----|-----|----------------|------------------------|
| 01 | [01-OpenAIDemo.py](./01-OpenAIDemo.py) | Your first agent with `OpenAIChatClient` | OpenAI API key |
| 02 | [02-AzureOpenAIDemo.py](./02-AzureOpenAIDemo.py) | The same agent on Azure OpenAI | Azure OpenAI resource |
| 03 | [03-AnthropicDemo.py](./03-AnthropicDemo.py) | Using Claude with `AnthropicClient` | Anthropic API key |
| 04 | [04-GoogleDemo.py](./04-GoogleDemo.py) | Gemini through its OpenAI-compatible endpoint | Google AI Studio key |
| 05 | [05-GrokDemo.py](./05-GrokDemo.py) | xAI Grok through a custom `base_url` | xAI API key |
| 06 | [06-MistralDemo.py](./06-MistralDemo.py) | Mistral through `OpenAIChatCompletionClient` | Mistral API key |
| 07 | [07-FoundryDemo.py](./07-FoundryDemo.py) | Microsoft Foundry with Entra ID auth (`AzureCliCredential`) | Foundry project + `az login` |
| 08 | [08-OllamaDemo.py](./08-OllamaDemo.py) | Local models with `OllamaChatClient` | Ollama running locally |
| 09 | [09-FoundryLocalDemo.py](./09-FoundryLocalDemo.py) | On-device models with Foundry Local (NPU > GPU > CPU) | `foundry-local-sdk` |
| 10 | [10-StreamingDemo.py](./10-StreamingDemo.py) | Streaming responses with `stream=True` | Azure OpenAI |
| 11 | [11-ChatDemo.py](./11-ChatDemo.py) | Interactive chat loop and token usage | Azure OpenAI |
| 12 | [12-SimpleAgentDemo.py](./12-SimpleAgentDemo.py) | Personas, `default_options`, reasoning effort | Azure OpenAI |
| 13 | [13-FunctionCallDemo.py](./13-FunctionCallDemo.py) | Function calling with `@tool` and typed parameters | Azure OpenAI |
| 14 | [14-CodeInterpreter.py](./14-CodeInterpreter.py) | Hosted Code Interpreter and downloading generated files | Azure OpenAI (Responses API) |
| 15 | [15-WebSearchTool.py](./15-WebSearchTool.py) | Hosted Web Search tool combined with a local tool | Azure OpenAI (Responses API) |
| 16 | [16-MCPTool.py](./16-MCPTool.py) | Remote MCP server (Microsoft Learn) with `MCPStreamableHTTPTool` | Azure OpenAI + internet |
| 17 | [17-AgentMiddleware.py](./17-AgentMiddleware.py) | Function middleware and agent-as-a-tool | Azure OpenAI (Responses API) |
| 18 | [18-StructuredOutput.py](./18-StructuredOutput.py) | Structured output with Pydantic models and `response_format` | Azure OpenAI (`gpt-5`, `gpt-5-mini`) |
| 19 | [19-EmbeddingDemo.py](./19-EmbeddingDemo.py) | Embeddings with `OpenAIEmbeddingClient` and cosine similarity | Azure OpenAI (`text-embedding-3-small`) |
| 20 | [20-VectorStoreDemo.py](./20-VectorStoreDemo.py) | Loading a knowledge base into a vector store with `AzureAISearchStore` | Azure OpenAI + Azure AI Search |
| 21 | [21-SemanticSearchDemo.py](./21-SemanticSearchDemo.py) | Semantic search, then answering with the results in the prompt (RAG) | Azure OpenAI + Azure AI Search |
| 22 | [22-AgenticRAGDemo.py](./22-AgenticRAGDemo.py) | Agentic RAG: the agent calls a vector search tool when it needs to | Azure OpenAI + Azure AI Search |
| 23 | [23-ReasoningEffortDemo.py](./23-ReasoningEffortDemo.py) | Comparing reasoning effort levels and their token usage | Azure OpenAI |
| 24 | [24-ModelImageDemo.py](./24-ModelImageDemo.py) | Sending an image to a model for analysis (base64 data URI or URL) | Azure OpenAI |
| 25 | [25-ImageGeneration-OpenAI.py](./25-ImageGeneration-OpenAI.py) | Hosted image generation tool, saving the generated image | OpenAI API key (`gpt-image-2`) |
| 26 | [26-ImageGeneration-AzureOpenAI.py](./26-ImageGeneration-AzureOpenAI.py) | Hosted image generation on Azure OpenAI | Azure OpenAI + image generation deployment |
| 27 | [27-ModelPDFDemo.py](./27-ModelPDFDemo.py) | Asking questions about a PDF document | OpenAI API key |
| 28 | [28-AIContextProviderDemo.py](./28-AIContextProviderDemo.py) | Custom `ContextProvider` with `before_run` and `after_run` hooks | Azure OpenAI |
| 29+ | *Coming soon* | See [Roadmap](#roadmap) | |

---

## Prerequisites

- **Python 3.10 or later.** Python 3.12+ is recommended.
- **Git.**
- **An editor.** [Visual Studio Code](https://code.visualstudio.com/) with the Python extension is recommended.
- **At least one model provider.** You don't need every provider. Most labs from 10 onward use **Azure OpenAI**, so that's the best one to set up first.
  - [OpenAI](https://platform.openai.com/api-keys) API key
  - [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/) resource with a deployed model (for example `gpt-5`)
  - [Anthropic](https://console.anthropic.com/) API key
  - [Google AI Studio](https://aistudio.google.com/apikey) API key
  - [xAI](https://console.x.ai/) API key
  - [Mistral](https://console.mistral.ai/) API key
  - [Microsoft Foundry](https://ai.azure.com/) project and the [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- **For the embedding and RAG labs (19–22):** a `text-embedding-3-small` deployment in Azure OpenAI and an [Azure AI Search](https://learn.microsoft.com/azure/search/) service.
- **For the Azure image generation lab (26):** an image generation model deployment (for example `gpt-image-2.5-flare`) in Azure OpenAI.
- **For the local labs (optional):**
  - [Ollama](https://ollama.com/download) with a pulled model (`ollama pull gemma4`)
  - [Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/)

---

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/TheTrainingBoss/MAF-Python.git
cd MAF-Python
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> In VS Code, you can also run **Python: Create Environment** from the Command Palette and select `requirements.txt`.

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Lab 09 (Foundry Local) also needs:

```bash
pip install foundry-local-sdk
```

### 4. Configure your environment variables

Copy the template, then fill in the keys for the providers you plan to use:

```powershell
# Windows
Copy-Item .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

| Variable | Used by |
|----------|---------|
| `OPENAI_API_KEY`, `OPENAI_MODEL` | Labs 01, 25, 27 |
| `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_MODEL` | Labs 02, 10–24, 26, 28 |
| `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_API_KEY`, `AZURE_SEARCH_INDEX_NAME` | Labs 21, 22 |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | Lab 03 |
| `GOOGLE_API_KEY`, `GOOGLE_MODEL` | Lab 04 |
| `GROK4_API_KEY`, `GROK4_MODEL`, `GROK4_BASE_URL` | Lab 05 |
| `MISTRAL_API_KEY`, `MISTRAL_MODEL` | Lab 06 |
| `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL` | Lab 07 |

> ⚠️ **Never commit your `.env` file.** It's already listed in `.gitignore`. Only `.env.example` is tracked.

Some labs from 18 onward use deployment names directly in the code (for example `gpt-5`, `gpt-5-mini`, `text-embedding-3-small`, and `gpt-image-2.5-flare`). If your Azure OpenAI deployments have different names, update the `model=` values in the script.

Lab 20 has placeholders for the Azure AI Search endpoint, key, and index name. Replace them before you run it, and use the same index name as `AZURE_SEARCH_INDEX_NAME` so labs 21 and 22 can search the data that lab 20 loads.

For lab 07 (Microsoft Foundry), sign in to Azure so `AzureCliCredential` can get a token:

```bash
az login
```

### 5. Run a lab

Each lab is a standalone script. Run it from the repository root with your virtual environment active:

```bash
python 01-OpenAIDemo.py
```

To exit the interactive labs (11, 12, and 13), type `exit` or `quit`. Labs 21 and 22 keep asking questions in a loop; press `Ctrl+C` to stop them.

Run the RAG labs in order: lab 20 loads the knowledge base into Azure AI Search (press `Y` when asked to import data), and labs 21 and 22 search it.

---

## Repository structure

```text
MAF-Python/
├── 01-OpenAIDemo.py … 28-AIContextProviderDemo.py   # Labs, numbered in learning order
├── media/                                           # Course images, sample PDF, and generated images
├── .env.example                                     # Environment variable template (copy to .env)
├── requirements.txt                                 # Pinned Python dependencies
└── README.md
```

Labs follow the naming convention `NN-ShortDescription.py`. To get the most out of the course, work through them in order.

---

## Roadmap

Many more labs are planned. Upcoming topics include:

- Persistent sessions and long-term memory
- Human-in-the-loop tool approvals
- Agent and chat middleware, guardrails, and content safety
- Workflows: sequential, concurrent, conditional, and looping executors
- Multi-agent orchestration: handoff, group chat, and magentic patterns
- Hosting your own MCP server and exposing agents as MCP tools
- Agent-to-Agent (A2A) protocol
- Observability with OpenTelemetry and Azure Monitor
- Evaluating agents
- Declarative (YAML) agents
- Deploying agents to Microsoft Foundry and Azure

When new labs are published, pull the latest changes and reinstall dependencies in case `requirements.txt` changed:

```bash
git pull
pip install -r requirements.txt
```

New labs might also add variables to `.env.example`. Compare it with your `.env` after each update.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: agent_framework` | Activate the virtual environment, then run `pip install -r requirements.txt`. |
| `401 Unauthorized` / invalid API key | Check the matching key in `.env`. Make sure the value has no quotes or trailing spaces. |
| Azure OpenAI `DeploymentNotFound` | `AZURE_OPENAI_MODEL` must match your **deployment name**, not just the model name. |
| Lab 07 credential error | Run `az login` and make sure your account has access to the Foundry project. |
| Lab 08 connection refused | Start Ollama and pull the model: `ollama pull gemma4`. |
| Hosted tools (labs 14, 15, and 17) fail | Use a model and region that support the Responses API with Code Interpreter or Web Search. |
| Labs 18–28 `DeploymentNotFound` | The deployment name is set in the script (for example `gpt-5` or `text-embedding-3-small`). Change `model=` to match your deployment. |
| Labs 21 and 22 return no results | Run lab 20 first and import the data into the same index named in `AZURE_SEARCH_INDEX_NAME`. |
| Lab 20 `ModuleNotFoundError: msvcrt` | Lab 20 uses `msvcrt` for single-key input, which is Windows-only. On macOS or Linux, replace `msvcrt.getwch()` with `input()`. |
| Lab 26 image generation fails | Set the `x-ms-oai-image-generation-deployment` header and `model` to your image generation deployment name. |
| Lab 27 PDF input fails on Azure OpenAI | PDF input in this lab uses OpenAI directly. Set `OPENAI_API_KEY`. |
| PowerShell blocks `Activate.ps1` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. |

---

## Resources

- [Microsoft Agent Framework documentation](https://learn.microsoft.com/agent-framework/)
- [Microsoft Agent Framework on GitHub](https://github.com/microsoft/agent-framework)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Microsoft Foundry](https://ai.azure.com/)

---

Happy building! 🚀
