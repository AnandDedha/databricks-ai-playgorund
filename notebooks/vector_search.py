from databricks.vector_search.client import VectorSearchClient

vs = VectorSearchClient()

index = vs.create_index(
    name="faq_vector_index",
    source_table="main.customer_faqs",
    embedding_model="databricks-bge-large"
)

print("✅ Vector Search Index Created: faq_vector_index")
