from openai import OpenAI

client = OpenAI()
resp = client.responses.create(
    model="gpt-4.1",
    tools=[{
        "type": "mcp",
        "server_label": "autogluon_proxy",
        "server_url": "https://round-abstracts-promises-qualities.trycloudflare.com/mcp/",
        # "server_url": "https://0d49-34-211-143-25.ngrok-free.app/mcp/",
        "require_approval": "never",
    }],
    input="List all available MCP tools in the proxy server. Show both local tools and remote tools. Show all the tools",
)
print(resp.output_text)

# I want to use mcp to generate a model and predict results. my input folder is:/Users/huawen.shen/Documents/autogluon-mcp-client/test_data, my output folder is /Users/huawen.shen/Documents/autogluon-mcp-client/test_data,
# my credentials are in /Users/huawen.shen/.aws/autogluon_creds.txt,
# just run 1 iteration using bedrock as provider and use anthropic.claude-3-haiku-20240307-v1:0, tell me what is the final output.
