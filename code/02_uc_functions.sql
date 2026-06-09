-- =============================================================
-- ShopMate AI - Unity Catalog Functions (Agent Tools)
-- =============================================================
-- Each function below becomes a TOOL the agent can call from
-- AI Playground. Notes:
--   1) COMMENT on the function and on each parameter is what the
--      LLM reads to decide WHEN to call this tool. Be descriptive.
--   2) Functions must live in a UC schema where the agent has
--      EXECUTE privilege.
--   3) Test each function with a SELECT before attaching as a tool.
-- =============================================================

USE CATALOG techbazaar;
USE SCHEMA shopmate;


-- -------------------------------------------------------------
-- TOOL 1: Look up a customer's order status by order ID
-- -------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_order_status(
  order_id_input STRING COMMENT 'The order ID to look up. Format is ORD-XXXX, for example ORD-7842.'
)
RETURNS STRING
COMMENT 'Returns the current status, expected delivery date, and tracking number for a given order ID. Use this when a customer asks where their order is, when it will arrive, or any question about a specific order ID.'
RETURN (
  SELECT CASE
    WHEN status IS NULL THEN
      CONCAT('No order found with ID: ', order_id_input, '. Please verify the order ID and try again.')
    ELSE
      CONCAT(
        'Order ', order_id, ' | Product: ', product_name,
        ' | Status: ', status,
        ' | Expected delivery: ', COALESCE(expected_delivery, 'N/A'),
        ' | Tracking: ', COALESCE(tracking_number, 'Not yet assigned'),
        ' | Ship to: ', COALESCE(shipping_address_city, 'N/A'),
        ' | Amount: INR ', CAST(total_amount_inr AS STRING)
      )
    END
  FROM orders
  WHERE order_id = order_id_input
  LIMIT 1
);

-- Quick test
SELECT get_order_status('ORD-7842');
SELECT get_order_status('ORD-9999');  -- not found case


-- -------------------------------------------------------------
-- TOOL 2: Look up customer loyalty tier and benefits by email
-- -------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_customer_profile(
  email_input STRING COMMENT 'The customer email address to look up. Must be a valid email format.'
)
RETURNS STRING
COMMENT 'Returns customer profile information including loyalty tier, total orders placed, lifetime value, and city. Use this when a customer needs personalized service, tier specific benefits explained, or when checking if they qualify for premium support.'
RETURN (
  SELECT CASE
    WHEN full_name IS NULL THEN
      CONCAT('No customer found with email: ', email_input)
    ELSE
      CONCAT(
        'Customer: ', full_name,
        ' | Tier: ', loyalty_tier,
        ' | City: ', city,
        ' | Total orders: ', CAST(total_orders AS STRING),
        ' | Lifetime value: INR ', CAST(lifetime_value_inr AS STRING),
        ' | Member since: ', CAST(signup_date AS STRING)
      )
    END
  FROM customers
  WHERE email = email_input
  LIMIT 1
);

SELECT get_customer_profile('anand.verma@example.com');


-- -------------------------------------------------------------
-- TOOL 3: Get a customer's recent orders by email (list)
-- -------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_recent_orders(
  email_input STRING COMMENT 'The customer email address to look up orders for.',
  max_orders  INT    COMMENT 'Maximum number of recent orders to return. Pass a small number like 3 or 5.'
)
RETURNS STRING
COMMENT 'Returns the most recent orders placed by a customer, ordered by date descending. Use this when a customer asks about their order history, recent purchases, or wants to know about past orders without specifying an order ID.'
RETURN (
  SELECT CASE
    WHEN COUNT(*) = 0 THEN CONCAT('No orders found for ', email_input)
    ELSE CONCAT_WS(' || ', COLLECT_LIST(line))
    END
  FROM (
    SELECT CONCAT(
      order_id, ' (', CAST(order_date AS STRING), '): ',
      product_name, ' x', CAST(quantity AS STRING),
      ' - ', status,
      ' - INR ', CAST(total_amount_inr AS STRING)
    ) AS line
    FROM orders
    WHERE customer_email = email_input
    ORDER BY order_date DESC
    LIMIT max_orders
  )
);

SELECT get_recent_orders('priya.sharma@example.com', 5);


-- -------------------------------------------------------------
-- TOOL 4: Check current stock availability for a product
-- -------------------------------------------------------------
CREATE OR REPLACE FUNCTION check_product_stock(
  product_id_input STRING COMMENT 'The product ID to check stock for. Format is PROD-XXX, for example PROD-205.'
)
RETURNS STRING
COMMENT 'Returns current stock quantity, price, and rating for a specific product ID. Use this when a customer asks if a product is in stock, what the price is, or wants to verify availability before buying.'
RETURN (
  SELECT CASE
    WHEN product_name IS NULL THEN
      CONCAT('Product not found: ', product_id_input)
    WHEN stock_qty <= 0 THEN
      CONCAT(product_name, ' is currently OUT OF STOCK. Price was INR ', CAST(price_inr AS STRING))
    WHEN stock_qty < 10 THEN
      CONCAT(product_name, ' is LOW IN STOCK - only ', CAST(stock_qty AS STRING),
             ' units left. Price: INR ', CAST(price_inr AS STRING),
             '. Rating: ', CAST(rating AS STRING), '/5')
    ELSE
      CONCAT(product_name, ' is IN STOCK (', CAST(stock_qty AS STRING),
             ' units available). Price: INR ', CAST(price_inr AS STRING),
             '. Rating: ', CAST(rating AS STRING), '/5')
    END
  FROM products
  WHERE product_id = product_id_input
  LIMIT 1
);

SELECT check_product_stock('PROD-205');
SELECT check_product_stock('PROD-601');


-- -------------------------------------------------------------
-- TOOL 5: Calculate refund eligibility based on order date
-- -------------------------------------------------------------
CREATE OR REPLACE FUNCTION check_return_eligibility(
  order_id_input STRING COMMENT 'The order ID to check return eligibility for. Format ORD-XXXX.'
)
RETURNS STRING
COMMENT 'Determines whether an order is still within the return window. Premium electronics get 15 days, other products get 10 days from delivery. Use this when a customer wants to return a product and you need to check if they are still eligible.'
RETURN (
  SELECT CASE
    WHEN o.status IS NULL THEN CONCAT('Order ', order_id_input, ' not found.')
    WHEN o.status != 'Delivered' THEN
      CONCAT('Order ', order_id_input, ' is currently ', o.status,
             '. Return window only starts after delivery.')
    WHEN p.category IN ('Laptops', 'Tablets')
         AND DATEDIFF(CURRENT_DATE(), TO_DATE(o.expected_delivery)) <= 15 THEN
      CONCAT('ELIGIBLE for return. ',
             CAST(15 - DATEDIFF(CURRENT_DATE(), TO_DATE(o.expected_delivery)) AS STRING),
             ' days remaining in the 15-day premium electronics return window.')
    WHEN p.category NOT IN ('Laptops', 'Tablets')
         AND DATEDIFF(CURRENT_DATE(), TO_DATE(o.expected_delivery)) <= 10 THEN
      CONCAT('ELIGIBLE for return. ',
             CAST(10 - DATEDIFF(CURRENT_DATE(), TO_DATE(o.expected_delivery)) AS STRING),
             ' days remaining in the standard 10-day return window.')
    ELSE
      CONCAT('NOT ELIGIBLE for return. Order delivered on ', o.expected_delivery,
             '. Return window has expired.')
    END
  FROM orders o
  LEFT JOIN products p ON o.product_id = p.product_id
  WHERE o.order_id = order_id_input
  LIMIT 1
);

SELECT check_return_eligibility('ORD-7847');
SELECT check_return_eligibility('ORD-7842');


-- -------------------------------------------------------------
-- Verify all functions are registered and visible
-- -------------------------------------------------------------
SHOW FUNCTIONS IN techbazaar.shopmate;

-- Grant EXECUTE so the agent service principal can call them
-- (replace the principal with your workspace user or group)
-- GRANT EXECUTE ON FUNCTION techbazaar.shopmate.get_order_status TO `account users`;
-- GRANT EXECUTE ON FUNCTION techbazaar.shopmate.get_customer_profile TO `account users`;
-- GRANT EXECUTE ON FUNCTION techbazaar.shopmate.get_recent_orders TO `account users`;
-- GRANT EXECUTE ON FUNCTION techbazaar.shopmate.check_product_stock TO `account users`;
-- GRANT EXECUTE ON FUNCTION techbazaar.shopmate.check_return_eligibility TO `account users`;
