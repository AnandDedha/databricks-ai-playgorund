from databricks.vector_search.client import VectorSearchClient
vs = VectorSearchClient()
index = vs.create_index(
    name="customer_support_index",
    source_table="main.customer_issues",
    embedding_model="databricks-bge-large"
)
query = "How to change my shipping address?"
results = index.similarity_search(query, k=2)
print(results)
