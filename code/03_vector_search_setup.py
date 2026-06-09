# =============================================================
# ShopMate AI - Vector Search Setup
# =============================================================
# Run this in a Databricks notebook (Python cells).
# Prerequisites:
#   - Catalog and schema created (see 01_setup_uc_objects.sql)
#   - customers, orders, products tables already loaded
#   - You have permission to create Vector Search endpoints
# =============================================================

# -------------------------------------------------------------
# CELL 1: Install / import the Vector Search SDK
# -------------------------------------------------------------
# %pip install databricks-vectorsearch
# dbutils.library.restartPython()

from databricks.vector_search.client import VectorSearchClient
from pyspark.sql import functions as F

vsc = VectorSearchClient()
CATALOG = "techbazaar"
SCHEMA  = "shopmate"


# -------------------------------------------------------------
# CELL 2: Load the .md knowledge base files into a Delta table
# -------------------------------------------------------------
# Assumes you uploaded the 4 .md files to:
#   /Volumes/techbazaar/shopmate/raw_data/knowledge_base/
import os

KB_VOLUME_PATH = "/Volumes/techbazaar/shopmate/raw_data/knowledge_base"

kb_files = [
    ("KB-001", "Return and Refund Policy", "policy",    f"{KB_VOLUME_PATH}/return_policy.md"),
    ("KB-002", "Shipping and Delivery",    "shipping",  f"{KB_VOLUME_PATH}/shipping_policy.md"),
    ("KB-003", "Warranty Information",     "warranty",  f"{KB_VOLUME_PATH}/warranty_info.md"),
    ("KB-004", "Frequently Asked Questions","faq",      f"{KB_VOLUME_PATH}/faq.md"),
]

rows = []
for doc_id, title, doc_type, path in kb_files:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    rows.append((doc_id, title, doc_type, content))

kb_df = spark.createDataFrame(rows, ["doc_id", "doc_title", "doc_type", "content"])
kb_df.write.mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.knowledge_base")
display(spark.table(f"{CATALOG}.{SCHEMA}.knowledge_base"))


# -------------------------------------------------------------
# CELL 3: (Optional but recommended) Chunk the knowledge base docs
# -------------------------------------------------------------
# Long documents work better when chunked into ~500 token sections
# so each chunk has a focused topic the embedding can capture.
from pyspark.sql.types import ArrayType, StringType

def chunk_markdown(text: str, max_chars: int = 1200) -> list:
    """Naive chunker - splits on H2/H3 headings, falls back to fixed size."""
    import re
    sections = re.split(r"\n(?=##\s)", text)
    chunks = []
    for sec in sections:
        if len(sec) <= max_chars:
            chunks.append(sec.strip())
        else:
            # further split overlong sections by paragraph
            paras = sec.split("\n\n")
            buf = ""
            for p in paras:
                if len(buf) + len(p) + 2 <= max_chars:
                    buf = (buf + "\n\n" + p).strip()
                else:
                    if buf: chunks.append(buf)
                    buf = p
            if buf: chunks.append(buf)
    return [c for c in chunks if c]

chunk_udf = F.udf(chunk_markdown, ArrayType(StringType()))

chunked = (
    spark.table(f"{CATALOG}.{SCHEMA}.knowledge_base")
         .withColumn("chunks", chunk_udf(F.col("content")))
         .withColumn("chunk", F.explode("chunks"))
         .withColumn("chunk_id",
                     F.concat(F.col("doc_id"), F.lit("_"),
                              F.expr("uuid()")))
         .select("chunk_id", "doc_id", "doc_title", "doc_type", "chunk")
)

(chunked.write
        .mode("overwrite")
        .option("delta.enableChangeDataFeed", "true")
        .saveAsTable(f"{CATALOG}.{SCHEMA}.knowledge_base_chunks"))

# Add CDF for delta sync if not set
spark.sql(f"""
ALTER TABLE {CATALOG}.{SCHEMA}.knowledge_base_chunks
SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")


# -------------------------------------------------------------
# CELL 4: Create a Vector Search Endpoint
# -------------------------------------------------------------
ENDPOINT_NAME = "shopmate_vs_endpoint"

try:
    vsc.create_endpoint(name=ENDPOINT_NAME, endpoint_type="STANDARD")
    print(f"Endpoint '{ENDPOINT_NAME}' creation started. This takes ~5-10 minutes.")
except Exception as e:
    if "ALREADY_EXISTS" in str(e):
        print(f"Endpoint '{ENDPOINT_NAME}' already exists. Continuing.")
    else:
        raise

# Wait until it is READY
vsc.wait_for_endpoint(name=ENDPOINT_NAME, timeout=900)
print("Endpoint is ONLINE.")


# -------------------------------------------------------------
# CELL 5: Create the PRODUCT CATALOG vector index
# -------------------------------------------------------------
# This index lets the agent answer "recommend me a laptop under 60k"
# style questions semantically.
PRODUCT_INDEX = f"{CATALOG}.{SCHEMA}.product_catalog_index"
PRODUCT_SOURCE = f"{CATALOG}.{SCHEMA}.products"

vsc.create_delta_sync_index(
    endpoint_name=ENDPOINT_NAME,
    index_name=PRODUCT_INDEX,
    source_table_name=PRODUCT_SOURCE,
    primary_key="product_id",
    pipeline_type="TRIGGERED",       # or CONTINUOUS for near-real-time
    embedding_source_column="description",
    embedding_model_endpoint_name="databricks-gte-large-en",   # built-in embedding
)
print(f"Index '{PRODUCT_INDEX}' is syncing. Wait ~3-5 minutes for first sync.")


# -------------------------------------------------------------
# CELL 6: Create the KNOWLEDGE BASE vector index
# -------------------------------------------------------------
KB_INDEX  = f"{CATALOG}.{SCHEMA}.knowledge_base_index"
KB_SOURCE = f"{CATALOG}.{SCHEMA}.knowledge_base_chunks"

vsc.create_delta_sync_index(
    endpoint_name=ENDPOINT_NAME,
    index_name=KB_INDEX,
    source_table_name=KB_SOURCE,
    primary_key="chunk_id",
    pipeline_type="TRIGGERED",
    embedding_source_column="chunk",
    embedding_model_endpoint_name="databricks-gte-large-en",
)
print(f"Index '{KB_INDEX}' is syncing.")


# -------------------------------------------------------------
# CELL 7: Test a similarity search against each index
# -------------------------------------------------------------
prod_idx = vsc.get_index(endpoint_name=ENDPOINT_NAME, index_name=PRODUCT_INDEX)
results = prod_idx.similarity_search(
    query_text="lightweight laptop for video editing under 60000",
    columns=["product_id", "product_name", "price_inr", "rating"],
    num_results=3,
)
print("PRODUCT SEARCH RESULTS:")
for r in results["result"]["data_array"]:
    print(r)

kb_idx = vsc.get_index(endpoint_name=ENDPOINT_NAME, index_name=KB_INDEX)
results = kb_idx.similarity_search(
    query_text="how long do I have to return a laptop",
    columns=["doc_title", "doc_type", "chunk"],
    num_results=2,
)
print("\nKNOWLEDGE BASE SEARCH RESULTS:")
for r in results["result"]["data_array"]:
    print(r)


# -------------------------------------------------------------
# CELL 8: Wrap each index as a UC function tool
# -------------------------------------------------------------
# This makes Vector Search callable from AI Playground / agents
# exactly like a UC function. The agent will see two more tools:
#   - search_products(query)
#   - search_knowledge_base(query)
# -------------------------------------------------------------
spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.search_products(
  query STRING COMMENT 'Natural language description of what the customer is looking for. Example: "wireless headphones with good noise cancellation under 30000 rupees"'
)
RETURNS TABLE(product_id STRING, product_name STRING, price_inr DECIMAL(12,2), rating DOUBLE)
COMMENT 'Searches the TechBazaar product catalog using semantic similarity. Use this whenever a customer is looking for a product recommendation, asks "what laptops do you have", "show me headphones for X", or any open-ended product discovery question. Do NOT use this if the customer gives a specific product ID; use check_product_stock instead.'
RETURN
  SELECT product_id, product_name, price_inr, rating
  FROM vector_search(
    index => '{PRODUCT_INDEX}',
    query => query,
    num_results => 5
  )
""")

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.search_knowledge_base(
  query STRING COMMENT 'Natural language question about TechBazaar policies, FAQs, shipping, returns, warranty, or general support. Example: "what is the return window for laptops"'
)
RETURNS TABLE(doc_title STRING, doc_type STRING, chunk STRING)
COMMENT 'Searches the TechBazaar support knowledge base including return policy, shipping policy, warranty information and FAQs. Use this whenever a customer asks a policy or how-to question that is NOT about a specific order or product ID.'
RETURN
  SELECT doc_title, doc_type, chunk
  FROM vector_search(
    index => '{KB_INDEX}',
    query => query,
    num_results => 3
  )
""")

# Test the new function-style tools
display(spark.sql(f"SELECT * FROM {CATALOG}.{SCHEMA}.search_products('budget headphones with noise cancellation')"))
display(spark.sql(f"SELECT * FROM {CATALOG}.{SCHEMA}.search_knowledge_base('what payment methods are accepted')"))


# =============================================================
# NEXT STEP
# =============================================================
# Open AI Playground in Databricks, pick a model that supports
# function calling (e.g. Llama 3.3 70B Instruct or Claude Sonnet
# on Databricks). Click the Tools icon and add:
#   1. techbazaar.shopmate.get_order_status
#   2. techbazaar.shopmate.get_customer_profile
#   3. techbazaar.shopmate.get_recent_orders
#   4. techbazaar.shopmate.check_product_stock
#   5. techbazaar.shopmate.check_return_eligibility
#   6. techbazaar.shopmate.search_products
#   7. techbazaar.shopmate.search_knowledge_base
# Then test with the demo prompts in the YouTube script.
# =============================================================
