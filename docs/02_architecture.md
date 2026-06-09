# 02 — Architecture

This doc explains **why** ShopMate AI is built the way it is. If you only want to ship the demo, you can skip this — but if you want to design your own agent, read on.

---

## The three tool types — when to use what

Agents become useful only when they have **tools** to act on. Databricks gives you three distinct ways to expose tools to an agent. They are NOT interchangeable — each one solves a different problem.

### 🔧 Unity Catalog Functions

**What:** A SQL or Python function registered in Unity Catalog with a clear `COMMENT` describing what it does.

**When to use:**
- The answer requires a **deterministic lookup** in your governed data (an order row, a customer record)
- You want **row-level security** and **column masking** to apply automatically
- The output should be exact, not "semantically similar"

**ShopMate examples:** `get_order_status`, `get_customer_profile`, `check_return_eligibility`

> 💡 **Key insight:** The LLM picks tools based on the `COMMENT` clause. Write it like a docstring — clear, specific, no jargon. Bad comment = wrong tool calls.

---

### 🔍 Vector Search

**What:** A managed vector index that lets you search Delta tables by **semantic similarity** instead of exact match.

**When to use:**
- Customer asks something fuzzy ("a lightweight laptop for college") and you need to match it against descriptions
- You need **RAG (Retrieval Augmented Generation)** — pulling relevant policy text into the agent's context before it answers
- The source data is text-heavy (product descriptions, policies, FAQs, support tickets)

**ShopMate examples:** `product_catalog_index` (semantic product search), `knowledge_base_index` (policy/FAQ retrieval)

> 💡 **Key insight:** You wrap a vector index as a UC function using the built-in `vector_search()` SQL function. That way the agent treats it like any other tool.

---

### 🌐 MCP Server

**What:** Model Context Protocol — a standard for connecting agents to **external systems** outside Databricks (Slack, GitHub, Jira, custom APIs).

**When to use:**
- The action lives outside Databricks (post to Slack, create a Jira ticket, call a third-party API)
- You want a clean separation between "things in my lakehouse" and "things in the outside world"
- You need to integrate with a SaaS product that already has an MCP server

**ShopMate example:** `escalate_to_human` — posts to a Slack channel when a customer is frustrated

> 💡 **Key insight:** Databricks offers both **managed MCP servers** (UC Functions, Vector Search, Genie — auto-generated) AND lets you **register external MCP servers** (Slack, custom). The agent doesn't care which is which.

---

## How the agent ties it together

When a customer message arrives in Playground, this is roughly what happens:

```
1. Customer message → Agent
2. LLM reads system prompt + available tool descriptions
3. LLM picks ONE tool (or none) to call
4. Tool runs → returns structured result
5. LLM reads result + decides:
       - Reply directly?
       - Call another tool?
6. Loop until LLM is ready to respond
7. Final natural-language reply → Customer
```

The LLM is the **orchestrator** — you don't write `if/else` logic for tool selection. The `COMMENT` clauses on your tools (or the descriptions in your MCP server) are what guide it.

---

## Data flow

```
┌──────────────┐         ┌──────────────────┐
│  Raw CSV/MD  │  COPY   │   Delta Tables   │
│  (Volume)    │ ──────▶ │   (Bronze)       │
└──────────────┘  INTO   └────────┬─────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  │                               │
                  ▼                               ▼
         ┌─────────────────┐            ┌──────────────────┐
         │   UC Functions  │            │  Vector Search   │
         │  (SQL on Delta) │            │ (Embedding Index)│
         └────────┬────────┘            └────────┬─────────┘
                  │                               │
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                         ┌────────────────┐
                         │  AI Playground │
                         │     Agent      │
                         └────────────────┘
```

The MCP server sits **outside** this lakehouse-centric flow — it calls Slack's API directly.

---

## Production considerations

For a real deployment you'd add:

1. **MLflow tracing** — log every tool call, latency, token usage
2. **Agent evaluation suite** — LLM-as-judge on golden test prompts (planned for v1.1)
3. **Model Serving** — deploy the agent behind an HTTPS endpoint via `mlflow.pyfunc.log_model`
4. **Inference tables** — auto-log every request/response for analysis
5. **AI Gateway** — rate limiting, content filtering, PII redaction in front of the model
6. **Asset bundles (DABs)** — version-controlled, repeatable deployment across dev/staging/prod

These are out of scope for the beginner tutorial but tracked in the roadmap.

---

## Why this stack is interesting in 2026

Two years ago you would have stitched this together with LangChain + Pinecone + Streamlit + custom Python webhooks + 4 different auth flows. Today every piece lives **inside Unity Catalog's governance perimeter**:

- Permissions, lineage, audit logs — handled by UC
- Vector indexes — fully managed, no separate cluster
- Agent orchestration — Playground/Agent Framework
- External integrations — standardised via MCP

The agent code shrinks from hundreds of lines to a system prompt + a tool list. That's the platform shift worth understanding.
