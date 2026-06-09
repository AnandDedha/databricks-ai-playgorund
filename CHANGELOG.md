# Changelog

All notable changes to **ShopMate AI** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- MLflow agent evaluation suite
- Databricks Asset Bundle (DAB) for one-command deployment
- Hinglish narration version of the script
- Genie space integration

---

## [1.0.0] — 2026-06-09

### Added
- 📄 Full YouTube tutorial script (~33 min, 12 sections) as `docs/YouTube_Script.docx`
- 🗃️ Sample datasets: 15 customers, 25 orders, 15 products (all in ₹ INR, Indian context)
- 📚 Knowledge base: return policy, shipping policy, warranty info, FAQ
- 🔧 SQL setup script for Unity Catalog (catalog, schema, 4 Delta tables with CDF)
- 🔧 5 UC Functions registered as agent tools:
  - `get_order_status`
  - `get_customer_profile`
  - `get_recent_orders`
  - `check_product_stock`
  - `check_return_eligibility`
- 🔍 Vector Search setup notebook with 2 indexes:
  - `product_catalog_index` (semantic product search)
  - `knowledge_base_index` (policy/FAQ retrieval)
- 🌐 MCP server setup guide covering both Slack MCP and FastMCP fallback
- 🤖 Agent system prompt with bilingual (English + Hindi/Hinglish) support
- 📖 Comprehensive README with quickstart, architecture diagram, and demo prompts
- ⚖️ MIT license
- 🙅 `.gitignore` covering Python, Databricks, secrets, and IDE artifacts
- 🔐 `.env.example` template for environment variables

### Notes
- All prices are in Indian Rupees (₹)
- Customer names and cities follow Indian context (Anand Verma, Priya Sharma, Noida, Mumbai, etc.)
- The agent is configured to handle Hindi/Hinglish queries naturally

---

[Unreleased]: https://github.com/your-username/shopmate-ai/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-username/shopmate-ai/releases/tag/v1.0.0
