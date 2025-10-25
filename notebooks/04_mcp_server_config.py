import os
os.environ["DBT_HOST"] = "cloud.getdbt.com"
os.environ["DBT_USER_ID"] = "your-user-id"
os.environ["DBT_TOKEN"] = "your-service-token"
os.environ["DBT_PROJECT_DIR"] = "/Workspace/dbt_project"
print("MCP Server environment variables configured successfully.")
