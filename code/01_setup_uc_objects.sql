-- =============================================================
-- ShopMate AI - Unity Catalog Setup Script
-- Run this in a Databricks SQL editor or notebook (SQL cell)
-- =============================================================
-- This script creates the catalog, schema, and Delta tables that
-- power the ShopMate AI demo. Run cells top to bottom.
-- =============================================================

-- STEP 1: Create catalog and schema in Unity Catalog
-- (skip catalog creation if it already exists in your workspace)
CREATE CATALOG IF NOT EXISTS techbazaar
COMMENT 'Catalog for TechBazaar e-commerce demo - ShopMate AI assistant';

CREATE SCHEMA IF NOT EXISTS techbazaar.shopmate
COMMENT 'Schema holding ShopMate AI tables, functions, and vector indexes';

-- Switch context for the rest of the script
USE CATALOG techbazaar;
USE SCHEMA shopmate;


-- STEP 2: Create the customers table
CREATE OR REPLACE TABLE customers (
  customer_id          STRING NOT NULL,
  full_name            STRING,
  email                STRING NOT NULL,
  phone                STRING,
  loyalty_tier         STRING COMMENT 'Bronze | Silver | Gold | Platinum',
  city                 STRING,
  signup_date          DATE,
  total_orders         INT,
  lifetime_value_inr   DECIMAL(12,2)
)
USING DELTA
COMMENT 'Master customer table for TechBazaar';


-- STEP 3: Create the orders table
CREATE OR REPLACE TABLE orders (
  order_id              STRING NOT NULL,
  customer_email        STRING NOT NULL,
  product_id            STRING,
  product_name          STRING,
  quantity              INT,
  unit_price_inr        DECIMAL(12,2),
  total_amount_inr      DECIMAL(12,2),
  order_date            DATE,
  status                STRING COMMENT 'Processing | Shipped | In Transit | Delivered | Cancelled',
  expected_delivery     STRING,
  tracking_number       STRING,
  shipping_address_city STRING,
  payment_method        STRING
)
USING DELTA
COMMENT 'All TechBazaar orders';


-- STEP 4: Create the products table (used as source for vector search)
CREATE OR REPLACE TABLE products (
  product_id    STRING NOT NULL,
  product_name  STRING,
  category      STRING,
  brand         STRING,
  price_inr     DECIMAL(12,2),
  stock_qty     INT,
  rating        DOUBLE,
  description   STRING COMMENT 'Rich product description - used as embedding source'
)
USING DELTA
TBLPROPERTIES (delta.enableChangeDataFeed = true)
COMMENT 'Product catalog with CDF enabled so Vector Search Index can auto-sync';


-- STEP 5: Create the knowledge base table (also a vector search source)
CREATE OR REPLACE TABLE knowledge_base (
  doc_id      STRING NOT NULL,
  doc_title   STRING,
  doc_type    STRING COMMENT 'policy | faq | warranty | shipping',
  content     STRING COMMENT 'Full markdown content - chunk in pipeline if needed'
)
USING DELTA
TBLPROPERTIES (delta.enableChangeDataFeed = true)
COMMENT 'Support knowledge base - powers RAG via Vector Search';


-- =============================================================
-- STEP 6: Data ingestion
-- =============================================================
-- Option A (recommended for the demo): Upload the four CSVs and
-- the four .md files to a Unity Catalog Volume, then COPY INTO.
--
-- Create a volume first:
--   CREATE VOLUME IF NOT EXISTS techbazaar.shopmate.raw_data;
-- Upload files via the Catalog Explorer UI to:
--   /Volumes/techbazaar/shopmate/raw_data/
-- Then run the COPY INTO statements below.
-- =============================================================

-- Customers
COPY INTO customers
FROM '/Volumes/techbazaar/shopmate/raw_data/customers.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true', 'mergeSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');

-- Orders
COPY INTO orders
FROM '/Volumes/techbazaar/shopmate/raw_data/orders.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true', 'mergeSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');

-- Products
COPY INTO products
FROM '/Volumes/techbazaar/shopmate/raw_data/products.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true', 'mergeSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');


-- =============================================================
-- STEP 7: Populate the knowledge_base table by reading the .md files
-- (Run this in a Python notebook cell, NOT SQL)
-- See: 03_vector_search_setup.py for the loader
-- =============================================================


-- STEP 8: Quick sanity checks
SELECT COUNT(*) AS customer_count FROM customers;
SELECT COUNT(*) AS order_count FROM orders;
SELECT COUNT(*) AS product_count FROM products;

SELECT status, COUNT(*) AS orders FROM orders GROUP BY status ORDER BY orders DESC;
SELECT category, COUNT(*) AS products, AVG(price_inr) AS avg_price FROM products GROUP BY category;
