# ShopMate AI - MCP Server Setup

This file walks through the third tool type you will demo: connecting an
**MCP (Model Context Protocol) server** to your agent in Databricks AI Playground.

---

## What MCP is, in plain English

MCP is an open standard (created by Anthropic, now adopted broadly) that
defines a uniform way for an LLM to talk to external tools. Think of it as
"USB-C for AI tools". Instead of writing a custom integration for every API
your agent needs, you point the agent at an MCP server and it automatically
gets a list of tools it can call.

In Databricks, MCP shows up in **two flavors**:

### 1. Managed MCP servers (built into Databricks)
Databricks exposes some platform capabilities as MCP servers automatically.
The three main ones for the demo:

| Managed MCP server | What it exposes | URL pattern |
|---|---|---|
| Unity Catalog Functions | Every UC function in a schema as a tool | `https://<workspace>/api/2.0/mcp/functions/<catalog>/<schema>` |
| Vector Search | Every Vector Search index in a schema as a tool | `https://<workspace>/api/2.0/mcp/vector-search/<catalog>/<schema>` |
| Genie Spaces | A Genie space (text-to-SQL over your tables) | `https://<workspace>/api/2.0/mcp/genie/<space_id>` |

This is powerful: the UC functions and Vector Search indexes you built in
steps 02 and 03 are already MCP-accessible. No extra code.

### 2. Custom (external) MCP servers
You can also connect any MCP-compliant server hosted outside Databricks.
Common ones in the ecosystem:

- **Slack MCP** — post messages, look up channels, escalate issues
- **GitHub MCP** — read issues, PRs, file contents
- **Jira / Linear MCP** — create and update tickets
- **Web fetch MCP** — pull live data from URLs

For the YouTube demo we will use a **Slack MCP** server so ShopMate can
escalate to a human agent by posting to a `#shopmate-escalations` channel.

---

## Demo setup: connecting the Slack MCP server

### Step 1 - Get a Slack bot token
1. Go to `https://api.slack.com/apps` and create a new app
2. Add OAuth scopes: `chat:write`, `channels:read`, `users:read`
3. Install the app to your workspace and copy the **Bot User OAuth Token**
   (starts with `xoxb-`)
4. Invite the bot to your `#shopmate-escalations` channel

### Step 2 - Register the MCP server in Databricks AI Playground
1. Open **AI Playground** (left sidebar > Machine Learning > Playground)
2. Pick a function-calling capable model (Llama 3.3 70B, Claude Sonnet, GPT-4o)
3. Click the **Tools** icon (wrench), then **Add MCP Server**
4. Provide:
   - **Name**: `shopmate-slack`
   - **Server URL**: the deployed Slack MCP endpoint
     (e.g. `https://your-slack-mcp.example.com/sse`)
   - **Authentication**: paste your Slack bot token as a bearer token

Once connected, the available tools list will show new entries like:
- `slack__post_message`
- `slack__list_channels`
- `slack__lookup_user`

### Step 3 - Test escalation from the agent
With the Slack MCP attached, try this prompt:

> "I bought a laptop and it arrived with a cracked screen. This has happened
> twice now. I want to talk to a human right now."

Expected agent behavior:
1. Recognizes the complaint pattern and frustration cue
2. Calls `search_knowledge_base` to confirm the damaged-item policy
3. Calls `slack__post_message` with channel `#shopmate-escalations` and a
   formatted message containing the customer issue, order ID and tier
4. Confirms to the customer that a human agent has been pinged

---

## Alternative: stand up a local MCP server (advanced)

If you do not have a Slack workspace, you can stand up a minimal MCP server
in Python and expose a custom escalation tool. Use this for the demo by
running it locally and tunneling through ngrok.

```python
# minimal_mcp_server.py
# Requires: pip install mcp fastapi uvicorn
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("shopmate-escalation")

@mcp.tool()
def escalate_to_human(
    customer_email: str,
    order_id: str,
    issue_summary: str,
    urgency: str = "normal"
) -> str:
    """Escalate a customer issue to the human support team.

    Args:
        customer_email: The email of the customer needing help.
        order_id: The relevant order ID, or 'N/A' if not order-specific.
        issue_summary: A 1-2 sentence summary of the customer issue.
        urgency: One of 'low', 'normal', 'high', 'urgent'.

    Returns:
        Confirmation message with ticket ID.
    """
    # In a real implementation this would write to a ticketing system.
    # For the demo we just return a generated ticket ID.
    import uuid
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    print(f"[ESCALATION] {ticket_id} | {urgency.upper()} | {customer_email} | "
          f"{order_id} | {issue_summary}")
    return (f"Ticket {ticket_id} created with {urgency} priority. "
            f"A human agent will reach out to {customer_email} within "
            f"{'15 minutes' if urgency=='urgent' else '2 hours'}.")

if __name__ == "__main__":
    mcp.run(transport="sse", port=8765)
```

Run it:
```bash
python minimal_mcp_server.py
# In another terminal:
ngrok http 8765
```

Then in Playground, register the MCP server with the ngrok HTTPS URL.

---

## Why MCP matters (recap for the video)

1. **Standardization** - Same protocol works across Claude Desktop, Cursor,
   Databricks Playground, OpenAI Agents SDK, etc. Tools written once are
   reusable everywhere.
2. **Governance** - In Databricks, managed MCP servers respect Unity Catalog
   permissions. The agent can only call tools the caller is allowed to use.
3. **Discovery** - The agent discovers available tools at runtime by querying
   the MCP server, so you can add or remove tools without redeploying the agent.
4. **Composability** - You can attach multiple MCP servers to one agent and
   it picks the right tool from the right server based on the user query.
