#!/usr/bin/env python3
"""
Anthropic example using the AutoGluon Pipeline MCP tool
"""

import anthropic
from rich import print

# Configuration
# Where pipeline_server.py is running
PIPELINE_SERVER_URL = 'https://ears-worldcat-attending-polyester.trycloudflare.com'
AUTOGLUON_SERVER_URL = 'https://ff31-34-211-143-25.ngrok-free.app'  # Your EC2 server

# Your local paths
INPUT_FOLDER = '/Users/huawen.shen/Documents/autogluon-mcp-client/test_data'
OUTPUT_FOLDER = '/Users/huawen.shen/Documents/autogluon-mcp-client/output'
CONFIG_FILE = '/Users/huawen.shen/Documents/autogluon-mcp-client/config.yaml'
CREDS_PATH = '/Users/huawen.shen/.aws/autogluon_creds.txt'

# Create Anthropic client
client = anthropic.Anthropic()

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
Run the mcp tool called run_autogluon_pipeline with these exact parameters, don't access server_url: {AUTOGLUON_SERVER_URL}, you just need to pass it as a parameter:
- input_folder: {INPUT_FOLDER}
- output_folder: {OUTPUT_FOLDER}
- server_url: {AUTOGLUON_SERVER_URL}
- config_file: {CONFIG_FILE}
- max_iterations: 3
- provider: bedrock
- model: anthropic.claude-3-haiku-20240307-v1:0
- creds_path: {CREDS_PATH}
- verbosity: info
- cleanup_server: false

If you run into any errors, please explain in detail at which step the error occurred, what actions you took, what code you executed, and share the exact error message verbatim.
"""

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
print("Calling AutoGluon Pipeline via Anthropic...")
print(f"Pipeline Server: {PIPELINE_SERVER_URL}")
print(f"AutoGluon Server: {AUTOGLUON_SERVER_URL}")
print("-" * 50)

try:
    response = client.beta.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,  # Increased for longer outputs
        messages=[{"role": "user", "content": prompt}],
        mcp_servers=[
            {
                "type": "url",
                "url": f"{PIPELINE_SERVER_URL}/mcp/",
                "name": "autogluon-pipeline",
            }
        ],
        extra_headers={
            "anthropic-beta": "mcp-client-2025-04-04"
        }
    )

    print("\nAnthropic Response:")
    print("=" * 50)

    # Extract and print text content from the response
    for block in response.content:
        if block.type == 'text':
            print(f"[text]: {block.text}")
        elif block.type == 'mcp_tool_use':
            print(
                f"\n[Tool Call: {block.name} with server {block.server_name}]")
            print(f"[Parameters]: {block.input}")
        elif block.type == 'mcp_tool_result':
            print(f"\n[Tool Result]: ")
            for content in block.content:
                if hasattr(content, 'text'):
                    print(content.text)

except Exception as e:
    print(f"\nError: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure pipeline_server.py is running on port 8005")
    print("2. Check that the AutoGluon server is accessible")
    print("3. Verify your file paths and credentials")
    print("4. Ensure you have set ANTHROPIC_API_KEY environment variable")


# Example of parsing the response to get output files
def parse_pipeline_results():
    """
    Example of how to parse the results if you need to process them further
    """
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

    try:
        response = client.beta.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            messages=[{"role": "user", "content": structured_prompt}],
            mcp_servers=[
                {
                    "type": "url",
                    "url": f"{PIPELINE_SERVER_URL}/mcp/",
                    "name": "autogluon-pipeline",
                }
            ],
            extra_headers={
                "anthropic-beta": "mcp-client-2025-04-04"
            }
        )

        # Extract JSON from response
        import json
        for block in response.content:
            if block.type == 'text' and '{' in block.text:
                # Try to find and parse JSON
                text = block.text
                start = text.find('{')
                end = text.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = text[start:end]
                    result_json = json.loads(json_str)
                    print("Parsed results:", result_json)
                    return result_json

    except Exception as e:
        print(f"Error parsing results: {e}")
        return None


# Helper function to display full response structure (for debugging)
def display_full_response(response):
    """Display the full structure of the response for debugging"""
    print("\n--- Full Response Structure ---")
    for i, block in enumerate(response.content):
        print(f"\nBlock {i} - Type: {block.type}")
        if block.type == 'text':
            print(f"Text: {block.text[:200]}..." if len(
                block.text) > 200 else f"Text: {block.text}")
        elif block.type == 'mcp_tool_use':
            print(f"Tool: {block.name}")
            print(f"Server: {block.server_name}")
            print(f"ID: {block.id}")
            print(f"Input: {block.input}")
        elif block.type == 'mcp_tool_result':
            print(f"Tool Use ID: {block.tool_use_id}")
            print(f"Is Error: {block.is_error}")
            for j, content in enumerate(block.content):
                print(f"  Result {j}: {content}")


if __name__ == "__main__":
    # Run the main example
    pass

    # Uncomment to test structured response parsing
    # parse_pipeline_results()

    # Uncomment to see full response structure for debugging
    # if 'response' in locals():
    #     display_full_response(response)
