# 🛒 ShopMate AI — Databricks AI for Beginners

> A complete, end-to-end tutorial for building a production-style AI customer support agent on Databricks using **Mosaic AI Playground**, **AI Agents**, and three tool types: **Unity Catalog Functions**, **Vector Search**, and **MCP Server**.

[![Databricks](https://img.shields.io/badge/Databricks-Mosaic_AI-FF3621?logo=databricks&logoColor=white)](https://www.databricks.com/product/machine-learning/mosaic-ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![YouTube Tutorial](https://img.shields.io/badge/YouTube-Tutorial-red?logo=youtube)](#)

---

## 🎯 What you'll build

**ShopMate AI** is a customer support agent for a fictional Indian electronics retailer called **TechBazaar**. The same agent can:

| Customer asks... | Tool used |
|---|---|
| "Where's my order ORD-7842?" | 🔧 UC Function (`get_order_status`) |
| "Suggest a laptop under ₹60,000 for college" | 🔍 Vector Search (`product_catalog_index`) |
| "What's your return policy?" | 🔍 Vector Search (`knowledge_base_index`) |
| "I want to speak to a human, this is unacceptable!" | 🌐 MCP Server (Slack escalation) |

By the end you'll understand **why** you'd pick each tool type — not just how to wire them up.

---

## 📂 Repository layout

```
shopmate-ai/
├── docs/                          ← All written documentation
│   ├── YouTube_Script.docx          The full ~33-min tutorial script
│   ├── 01_getting_started.md        Prerequisites & workspace setup
│   ├── 02_architecture.md           How the pieces fit together
│   └── 03_mcp_server_setup.md       Slack MCP + FastMCP fallback
│
├── code/
│   ├── 01_setup_uc_objects.sql      Catalog, schema, Delta tables
│   ├── 02_uc_functions.sql          5 UC functions registered as tools
│   ├── 03_vector_search_setup.py    Endpoint + 2 indexes + UC wrappers
│   └── 05_agent_system_prompt.md    Drop into Playground "System" box
│
├── data/
│   ├── customers.csv                15 sample Indian customers
│   ├── orders.csv                   25 sample orders (₹ INR)
│   ├── products.csv                 15 electronics with rich descriptions
│   └── knowledge_base/
│       ├── return_policy.md
│       ├── shipping_policy.md
│       ├── warranty_info.md
│       └── faq.md
│
├── assets/                          ← Screenshots / B-roll (gitignored content)
├── .env.example                     Template for required env vars
├── .gitignore
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
└── README.md                        ← You are here
```

---

## 🚀 Quickstart (15 minutes to a working agent)

### Prerequisites

- ✅ Databricks workspace with **Unity Catalog enabled**
- ✅ Permission to create catalogs (or use an existing one — edit `01_setup_uc_objects.sql`)
- ✅ Access to **Mosaic AI Playground** and **Vector Search**
- ✅ A serverless SQL warehouse OR a small all-purpose cluster (DBR 15.x ML +)

### Step-by-step

```bash
# 1. Clone this repo
git clone https://github.com/<your-username>/shopmate-ai.git
cd shopmate-ai

# 2. Upload data/ contents to a Volume in your workspace
#    Target: /Volumes/techbazaar/shopmate/raw_data/
#    (You can do this via the UI or `databricks fs cp`)

# 3. Copy .env.example to .env and fill in your values (only if running locally)
cp .env.example .env
```

Then inside your Databricks workspace:

1. Run **`code/01_setup_uc_objects.sql`** in a SQL editor → creates catalog + tables
2. Run **`code/02_uc_functions.sql`** → registers 5 functions as agent tools
3. Run **`code/03_vector_search_setup.py`** as a notebook → creates 2 vector indexes (~10 min sync)
4. Follow **`docs/03_mcp_server_setup.md`** → wire up Slack MCP (or use FastMCP fallback)
5. Open **AI Playground**, paste **`code/05_agent_system_prompt.md`** into System prompt, attach all 7 tools
6. Try the demo prompts below ⬇️

---

## 💬 Demo prompts to try

Once your agent is live in Playground:

```text
1. "Hi! Can you check the status of my order ORD-7842?"
2. "My email is anand.verma@example.com — show me my recent orders"
3. "Suggest a lightweight laptop under ₹60,000 for a college student"
4. "What is your return policy for headphones?"
5. "Is order ORD-7849 eligible for return?"
6. "I've been waiting 3 weeks and my order is still not here, this is RIDICULOUS"
7. "Mera order kahan hai? ORD-7855" (Hinglish — the agent handles it)
```

Prompt #6 should trigger the MCP escalation tool. Prompt #7 demonstrates bilingual handling.

---

## 🏗️ Architecture at a glance

```
┌─────────────────┐
│   Customer      │
└────────┬────────┘
         │ chats with
         ▼
┌─────────────────────────────────┐
│  ShopMate AI Agent (Playground) │
│  ┌───────────────────────────┐  │
│  │   LLM (e.g. Claude/Llama) │  │
│  └────┬──────────────────────┘  │
│       │ tool calls               │
└───────┼─────────────────────────┘
        │
   ┌────┴────┬──────────────┬──────────────┐
   ▼         ▼              ▼              ▼
┌──────┐ ┌──────────┐  ┌──────────┐  ┌───────────┐
│  UC  │ │  Vector  │  │  Vector  │  │    MCP    │
│Funcs │ │  Search  │  │  Search  │  │  Server   │
│ x5   │ │ Products │  │    KB    │  │  (Slack)  │
└──┬───┘ └─────┬────┘  └─────┬────┘  └─────┬─────┘
   │          │              │              │
   ▼          ▼              ▼              ▼
┌──────┐  ┌────────┐    ┌────────┐    ┌──────────┐
│Delta │  │ Delta  │    │ Delta  │    │  Slack   │
│Tables│  │ Index  │    │ Index  │    │ Channel  │
└──────┘  └────────┘    └────────┘    └──────────┘
```

See `docs/02_architecture.md` for the deep dive.

---

## 🎬 The YouTube tutorial

The full ~33-minute video script lives at **`docs/YouTube_Script.docx`**.

**Sections covered:**

| Time | Section |
|------|---------|
| 00:00 — 00:50 | Cold open: live demo |
| 00:50 — 01:40 | What you'll learn |
| 01:40 — 03:30 | What is Mosaic AI? |
| 03:30 — 05:30 | AI Playground walkthrough |
| 05:30 — 07:30 | Agents vs Tools — the mental model |
| 07:30 — 09:00 | Building ShopMate AI: the plan |
| 09:00 — 15:30 | 🔧 UC Functions deep dive + demo |
| 15:30 — 22:30 | 🔍 Vector Search deep dive + demo |
| 22:30 — 28:30 | 🌐 MCP Server deep dive + demo |
| 28:30 — 31:00 | Putting it all together |
| 31:00 — 32:30 | Best practices for production |
| 32:30 — 33:30 | Recap & next steps |

---

## 🛣️ Roadmap

- [ ] MLflow agent evaluation suite (LLM-as-judge for each tool path)
- [ ] Deployment to Databricks Agent Framework (`mlflow.pyfunc` + Model Serving)
- [ ] Add Genie space integration for ad-hoc data questions
- [ ] CI/CD via Databricks Asset Bundles (DABs)
- [ ] Hinglish narration version of the script
- [ ] Short 15-minute version for follow-up video

---

## 🤝 Contributing

PRs welcome! See [`CONTRIBUTING.md`](CONTRIBUTING.md). For major changes, please open an issue first.

---

## 📜 License

[MIT](LICENSE) © 2026 Anand Verma

---

## 🙏 Acknowledgements

- The Databricks Mosaic AI team for shipping Playground, Agents, and managed MCP servers
- The Olist Kaggle dataset which inspired the e-commerce framing
- Every viewer who paused, rewound, and DM'd "bhai, ye samajh nahi aaya" 🙏

---

**⭐ If this helped, please star the repo and subscribe to the channel!**
