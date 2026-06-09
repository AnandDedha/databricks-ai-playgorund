# 01 — Getting Started

This doc walks you through the prerequisites and one-time workspace setup needed before you can build ShopMate AI.

---

## Prerequisites checklist

Before you touch any code, confirm you have:

- [ ] A **Databricks workspace** (any cloud: AWS / Azure / GCP)
- [ ] **Unity Catalog enabled** on that workspace
- [ ] **Workspace admin** access OR an admin who can run the catalog-creation step for you
- [ ] Access to **Mosaic AI Playground** (Premium plan or above)
- [ ] **Vector Search** enabled in your workspace region
- [ ] A **serverless SQL warehouse** running, OR a small all-purpose cluster (DBR 15.x ML or newer)
- [ ] (Optional, for MCP demo) A **Slack workspace** where you can install a bot — or willingness to use the FastMCP fallback

> **Note:** If you're on the **free Databricks trial**, you have everything you need.

---

## One-time workspace setup

### 1. Create the catalog and volume

If you have admin rights, run this once in a SQL editor:

```sql
CREATE CATALOG IF NOT EXISTS techbazaar;
CREATE SCHEMA IF NOT EXISTS techbazaar.shopmate;
CREATE VOLUME IF NOT EXISTS techbazaar.shopmate.raw_data;
```

If you don't have admin rights, ask your admin to run it, or pick an existing catalog you can write to and update the paths in `code/01_setup_uc_objects.sql` accordingly.

### 2. Upload sample data to the volume

You can do this three ways:

**Option A — UI (easiest)**
1. Navigate to **Catalog → techbazaar → shopmate → raw_data**
2. Click **Upload to this volume**
3. Drag-and-drop all files from this repo's `data/` folder (CSVs + the `knowledge_base/` subfolder)

**Option B — Databricks CLI**
```bash
databricks fs cp -r data/ dbfs:/Volumes/techbazaar/shopmate/raw_data/
```

**Option C — Notebook**
```python
dbutils.fs.cp("file:/path/to/data/", "/Volumes/techbazaar/shopmate/raw_data/", recurse=True)
```

### 3. Verify the upload

```sql
LIST '/Volumes/techbazaar/shopmate/raw_data/';
```

You should see `customers.csv`, `orders.csv`, `products.csv`, and a `knowledge_base/` folder with 4 markdown files.

---

## Next step

➡️ Open `code/01_setup_uc_objects.sql` and run it cell-by-cell.

If you hit any issues, the troubleshooting section of the main `README.md` covers the most common ones.
