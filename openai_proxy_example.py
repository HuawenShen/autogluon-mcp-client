#!/usr/bin/env python3
"""
OpenAI client example using the unified MCP Proxy
This demonstrates the complete workflow with local and remote operations
"""

from openai import OpenAI

# Configuration
# Unified proxy endpoint (port 8003)
PROXY_URL = 'https://design-important-nvidia-norman.trycloudflare.com'
INPUT_FOLDER = '/Users/huawen.shen/Documents/autogluon-mcp-client/test_data'
OUTPUT_FOLDER = '/Users/huawen.shen/Documents/autogluon-mcp-client/output'
CREDS_PATH = '/Users/huawen.shen/Documents/autogluon-mcp-client/credentials.txt'

# Create OpenAI client
client = OpenAI()

# Complete workflow prompt
workflow_prompt = f"""
I need to run an AutoGluon task using the MCP proxy. Please execute the following workflow:

1. **Explore and Prepare Local Files**:
   - Use `local_explore_directory` to explore: {INPUT_FOLDER}
   - Use `local_validate_dataset` to check any CSV files found
   - Use `local_prepare_local_folder` to prepare the folder for upload
   - Note the cache_id returned

2. **Load Credentials**:
   - Use `local_read_credentials` to read credentials from: {CREDS_PATH}
   - Provider is "bedrock"

3. **Upload to Remote Server**:
   - Use `local_get_cached_data` with the cache_id to retrieve the prepared data
   - Use `remote_upload_input_folder` to upload the folder_structure and file_contents
   - Note the server path returned

4. **Start AutoGluon Task**:
   - Use `remote_start_task` with:
     - input_dir: [server path from upload]
     - output_dir: {OUTPUT_FOLDER}
     - max_iterations: 1
     - provider: bedrock
     - model: anthropic.claude-3-haiku-20240307-v1:0
     - credentials_text: [from step 2]

5. **Monitor Progress**:
   - Use `remote_check_status` to monitor the task
   - Use `remote_get_progress` to show progress percentage
   - Continue until the task is completed

6. **Handle Results**:
   - Once completed, use `remote_list_outputs` to see the output files
   - Report the final results

Please execute each step and show me the results. If any step fails, explain the error and suggest solutions.
"""

# Make the request
print("Sending request to OpenAI with unified MCP Proxy...")
print(f"Proxy URL: {PROXY_URL}")
print("-" * 50)

try:
    resp = client.responses.create(
        model="gpt-4.1",
        tools=[
            {
                "type": "mcp",
                "server_label": "autogluon_unified",
                "server_url": f"{PROXY_URL}/mcp/",
                "require_approval": "never",
            },
        ],
        input=workflow_prompt,
    )
    
    print("\nOpenAI Response:")
    print("=" * 50)
    print(resp.output_text)
    
except Exception as e:
    print(f"\nError: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure the proxy is running: ./setup_proxy.sh")
    print("2. Check proxy logs: tail -f logs/proxy.log")
    print("3. Verify both local and remote servers are accessible")


# Alternative: Step-by-step interactive approach
def interactive_workflow():
    """Interactive workflow for debugging"""
    print("\n\nInteractive Mode")
    print("=" * 50)
    
    steps = [
        "You don't need to open a directory.If you do so, you will fail. You only need to make function calls to read directories.",
        
        f"use {INPUT_FOLDER} to call local_explore_directory",
        
        f"Prepare the folder {INPUT_FOLDER} for upload using local_prepare_local_folder",
        
        "Using the cache_id from the previous step, retrieve the data with local_get_cached_data",
        
        f"Read credentials from {CREDS_PATH} using local_read_credentials with provider='bedrock'",
        
        "Now we'll switch to remote operations. Upload the folder data using ag_upload_input_folder",
        
        "Start the AutoGluon task with ag_start_task using the parameters I specified",
        
        "Check the task status with ag_check_status",
        
        "Show the current progress with ag_get_progress"
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"\nStep {i}: {step}")
        input("Press Enter to continue...")
        
        resp = client.responses.create(
            model="gpt-4.1",
            tools=[
                {
                    "type": "mcp",
                    "server_label": "autogluon_unified",
                    "server_url": f"{PROXY_URL}/mcp/",
                    "require_approval": "never",
                },
            ],
            input=step,
        )
        
        print(resp.output_text)


if __name__ == "__main__":
    # Run the main workflow
    # Uncomment the next line to run interactive mode instead
    # interactive_workflow()
    pass
