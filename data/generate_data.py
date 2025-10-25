from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Load sample datasets
orders_data = [
    ("A123", "C001", "Smartwatch Pro", "2025-10-01", "Delivered", "2025-10-05"),
    ("B456", "C002", "Noise Cancelling Headphones", "2025-10-10", "In Transit", "2025-10-28"),
    ("C789", "C003", "Fitness Band", "2025-09-28", "Cancelled", None),
    ("D234", "C004", "Wireless Charger", "2025-10-18", "Processing", None)
]
orders_columns = ["order_id", "customer_id", "product_name", "order_date", "delivery_status", "delivery_date"]

payments_data = [
    ("C001", "Paid", "2025-10-10", "Credit Card", 249.99),
    ("C002", "Pending", "2025-10-22", "PayPal", 129.50),
    ("C003", "Refunded", "2025-09-30", "UPI", 79.00),
    ("C004", "Paid", "2025-10-20", "Credit Card", 59.99)
]
payments_columns = ["customer_id", "payment_status", "last_payment_date", "payment_method", "total_amount"]

faq_data = [
    (1, "How can I return a product?", "You can return a product within 15 days of delivery through the 'My Orders' section."),
    (2, "How do I track my order?", "Go to the Order Details page, and click on 'Track Shipment' for real-time tracking."),
    (3, "What payment methods are accepted?", "We accept Credit/Debit cards, PayPal, and UPI."),
    (4, "How long does delivery take?", "Most deliveries take between 3–7 business days."),
    (5, "What if my product is damaged?", "If the product arrives damaged, initiate a return request immediately with photos.")
]
faq_columns = ["id", "question", "answer"]

# Create DataFrames
orders_df = spark.createDataFrame(orders_data, orders_columns)
payments_df = spark.createDataFrame(payments_data, payments_columns)
faq_df = spark.createDataFrame(faq_data, faq_columns)

# Write to Unity Catalog tables
orders_df.write.mode("overwrite").saveAsTable("main.customer_orders")
payments_df.write.mode("overwrite").saveAsTable("main.customer_payments")
faq_df.write.mode("overwrite").saveAsTable("main.customer_faqs")

print("✅ Sample datasets created successfully in Unity Catalog.")
