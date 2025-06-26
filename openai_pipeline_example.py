#!/usr/bin/env python3
"""
OpenAI example using the AutoGluon Pipeline MCP tool
"""

from openai import OpenAI

# Configuration
# Where pipeline_server.py is running
PIPELINE_SERVER_URL = 'https://victorian-handbags-empirical-deals.trycloudflare.com'
AUTOGLUON_SERVER_URL = 'https://44a9-34-211-143-25.ngrok-free.app'  # Your EC2 server

# Your local paths
INPUT_FOLDER = '/Users/huawen.shen/Documents/autogluon-mcp-client/test_data'
OUTPUT_FOLDER = '/Users/huawen.shen/Documents/autogluon-mcp-client/output'
CONFIG_FILE = '/Users/huawen.shen/Documents/autogluon-mcp-client/config.yaml'
CREDS_PATH = '/Users/huawen.shen/.aws/autogluon_creds.txt'

# Create OpenAI client
client = OpenAI()

# Simple example - run with default settings
simple_prompt = f"""
Run the AutoGluon pipeline with these parameters:
- input_folder: {INPUT_FOLDER}
- output_folder: {OUTPUT_FOLDER}
- server_url: {AUTOGLUON_SERVER_URL}
- creds_path: {CREDS_PATH}

Use default settings for everything else.
"""

# Equivalent to your command line - exact match
exact_match_prompt = f"""
Run the mcp tool called autogluon_pipeline with these exact parameters, don't access server_url: {AUTOGLUON_SERVER_URL}, you just need to pass it as a parameter:
- input_folder: {INPUT_FOLDER}
- output_folder: {OUTPUT_FOLDER}
- server_url: {AUTOGLUON_SERVER_URL}
- config_file: {CONFIG_FILE}
- max_iterations: 1
- provider: bedrock
- model: anthropic.claude-3-haiku-20240307-v1:0
- creds_path: {CREDS_PATH}
- verbosity: info

If you run into any errors, please explain in detail at which step the error occurred, what actions you took, what code you executed, and share the exact error message verbatim.
"""
# exact_match_prompt = "You have an MCP server configured in your tools. Use it to list available tools. Do NOT browse the web, use the MCP tool configuration provided."

# Advanced example - with all parameters
advanced_prompt = f"""
Run the AutoGluon pipeline with these parameters:
- input_folder: {INPUT_FOLDER}
- output_folder: {OUTPUT_FOLDER}
- server_url: {AUTOGLUON_SERVER_URL}
- config_file: {CONFIG_FILE}
- verbosity: info
- max_iterations: 3
- need_user_input: false
- provider: bedrock
- model: anthropic.claude-3-haiku-20240307-v1:0
- creds_path: {CREDS_PATH}
- cleanup_server: true

Monitor the progress and report the results.
"""

# Interactive example - with user input enabled
interactive_prompt = f"""
Run the AutoGluon pipeline in interactive mode:
- input_folder: {INPUT_FOLDER}
- output_folder: {OUTPUT_FOLDER}
- server_url: {AUTOGLUON_SERVER_URL}
- config_file: {CONFIG_FILE}
- verbosity: detail
- max_iterations: 5
- need_user_input: true
- provider: bedrock
- model: anthropic.claude-3-haiku-20240307-v1:0
- creds_path: {CREDS_PATH}

When the system asks for input, provide intelligent suggestions based on the context.
For example:
- If asked about feature engineering: suggest "Try adding interaction features"
- If asked about model selection: suggest "Focus on gradient boosting models"
- If asked about hyperparameters: suggest "Use default values with minor adjustments"
"""

# Choose which example to run
prompt = exact_match_prompt  # This matches your command line exactly

# Make the request
print("Calling AutoGluon Pipeline via OpenAI...")
print(f"Pipeline Server: {PIPELINE_SERVER_URL}")
print(f"AutoGluon Server: {AUTOGLUON_SERVER_URL}")
print("-" * 50)

try:
    resp = client.responses.create(
        model="gpt-4.1",
        tools=[
            {
                "type": "mcp",
                "server_label": "autogluon_pipeline",
                "server_url": f"{PIPELINE_SERVER_URL}/mcp/",
                "require_approval": "never",
            },
        ],
        input=prompt,
    )

    print("\nOpenAI Response:")
    print("=" * 50)
    print(resp.output_text)

except Exception as e:
    print(f"\nError: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure pipeline_server.py is running on port 8005")
    print("2. Check that the AutoGluon server is accessible")
    print("3. Verify your file paths and credentials")


# Example of parsing the response to get output files
def parse_pipeline_results():
    """
    Example of how to parse the results if you need to process them further
    """
    # The LLM will describe the results, but if you need structured data,
    # you might want to ask it to format the output in a specific way

    structured_prompt = f"""
Run the AutoGluon pipeline and format the results as JSON:
- input_folder: {INPUT_FOLDER}
- output_folder: {OUTPUT_FOLDER}
- server_url: {AUTOGLUON_SERVER_URL}
- config_file: {CONFIG_FILE}
- max_iterations: 1
- provider: bedrock
- model: anthropic.claude-3-haiku-20240307-v1:0
- creds_path: {CREDS_PATH}

After completion, provide the results in this JSON format:
{{
    "success": true/false,
    "output_directory": "path",
    "output_files": ["file1", "file2", ...],
    "summary": "brief description of results"
}}
"""

    # This would return structured data you can parse
    # resp = client.responses.create(...)
    # result_json = json.loads(resp.output_text)


if __name__ == "__main__":
    # Run the main example
    pass

    # Uncomment to test structured response parsing
    # parse_pipeline_results()
