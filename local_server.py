#!/usr/bin/env python3
"""
Mac Local MCP Server for file operations
Handles local file reading, preparation, and result saving
"""

import base64
import json
import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from fastmcp import FastMCP

# Reuse file_handler from client directory
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from file_handler import analyze_folder, read_files_for_upload

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("AutoGluon Local File Server 📁")

# Cache for prepared data
data_cache = {}
cache_timeout = 3600  # 1 hour


# ==================== File Operations ====================

@mcp.tool()
async def prepare_local_folder(
    folder_path: str,
    max_file_size: Optional[int] = 100 * 1024 * 1024,
    skip_patterns: Optional[list] = None
) -> dict:
    """
    Prepare local folder for upload with caching.
    
    Args:
        folder_path: Path to local folder
        max_file_size: Maximum file size in bytes (default: 100MB)
        skip_patterns: List of patterns to skip (e.g., ['*.log', '*.tmp'])
        
    Returns:
        dict: {"success": bool, "cache_id": str, "summary": dict}
    """
    try:
        # Validate path
        path = Path(folder_path)
        if not path.exists():
            return {
                "success": False,
                "error": f"Path not found: {folder_path}"
            }
        
        if not path.is_dir():
            return {
                "success": False,
                "error": f"Not a directory: {folder_path}"
            }
        
        logger.info(f"Preparing folder: {folder_path}")
        
        # Analyze folder structure
        folder_structure = analyze_folder(folder_path)
        
        # Read file contents with filtering
        file_contents = {}
        total_size = 0
        skipped_files = []
        
        for file_path in path.rglob("*"):
            if file_path.is_file():
                # Skip patterns
                if skip_patterns:
                    if any(file_path.match(pattern) for pattern in skip_patterns):
                        skipped_files.append(str(file_path))
                        continue
                
                # Skip large files
                file_size = file_path.stat().st_size
                if file_size > max_file_size:
                    skipped_files.append(f"{file_path} (too large: {file_size/1024/1024:.1f}MB)")
                    continue
                
                # Read and encode
                try:
                    content = file_path.read_bytes()
                    content_b64 = base64.b64encode(content).decode('utf-8')
                    rel_path = file_path.relative_to(path)
                    file_contents[str(rel_path)] = content_b64
                    total_size += file_size
                except Exception as e:
                    logger.error(f"Failed to read {file_path}: {e}")
                    skipped_files.append(f"{file_path} (error: {str(e)})")
        
        # Cache the data
        cache_id = f"folder_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(folder_path)}"
        data_cache[cache_id] = {
            "folder_structure": folder_structure,
            "file_contents": file_contents,
            "timestamp": datetime.now(),
            "source_path": folder_path
        }
        
        # Return summary
        return {
            "success": True,
            "cache_id": cache_id,
            "summary": {
                "total_files": len(file_contents),
                "total_size": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "skipped_files": len(skipped_files),
                "skipped_details": skipped_files[:10]  # First 10 only
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to prepare folder: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def get_cached_data(cache_id: str) -> dict:
    """
    Retrieve cached folder data for upload.
    
    Args:
        cache_id: Cache identifier from prepare_local_folder
        
    Returns:
        dict: {"success": bool, "folder_structure": dict, "file_contents": dict}
    """
    if cache_id not in data_cache:
        return {
            "success": False,
            "error": f"Cache ID not found: {cache_id}"
        }
    
    cached = data_cache[cache_id]
    
    # Check timeout
    age = (datetime.now() - cached["timestamp"]).seconds
    if age > cache_timeout:
        del data_cache[cache_id]
        return {
            "success": False,
            "error": f"Cache expired (age: {age}s)"
        }
    
    return {
        "success": True,
        "folder_structure": cached["folder_structure"],
        "file_contents": cached["file_contents"]
    }


@mcp.tool()
async def explore_directory(
    directory_path: str,
    max_depth: Optional[int] = 3,
    include_hidden: bool = False
) -> dict:
    """
    Explore directory structure without reading file contents.
    
    Args:
        directory_path: Path to explore
        max_depth: Maximum depth to explore
        include_hidden: Include hidden files/directories
        
    Returns:
        dict: Directory tree structure with metadata
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            return {
                "success": False,
                "error": f"Path not found: {directory_path}"
            }
        
        def explore_tree(p: Path, current_depth: int = 0):
            if current_depth >= max_depth:
                return {"type": "directory", "name": p.name, "truncated": True}
            
            if p.is_file():
                stat = p.stat()
                return {
                    "type": "file",
                    "name": p.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "extension": p.suffix
                }
            else:
                children = []
                try:
                    for child in sorted(p.iterdir()):
                        if not include_hidden and child.name.startswith('.'):
                            continue
                        children.append(explore_tree(child, current_depth + 1))
                except PermissionError:
                    return {"type": "directory", "name": p.name, "error": "Permission denied"}
                
                return {
                    "type": "directory",
                    "name": p.name,
                    "children": children,
                    "count": len(children)
                }
        
        tree = explore_tree(path)
        
        return {
            "success": True,
            "tree": tree,
            "base_path": str(path)
        }
        
    except Exception as e:
        logger.error(f"Failed to explore directory: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def read_local_file(
    file_path: str,
    as_text: bool = True,
    encoding: str = "utf-8"
) -> dict:
    """
    Read a single local file.
    
    Args:
        file_path: Path to file
        as_text: Return as text (True) or base64 (False)
        encoding: Text encoding (if as_text=True)
        
    Returns:
        dict: File content and metadata
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        if not path.is_file():
            return {
                "success": False,
                "error": f"Not a file: {file_path}"
            }
        
        stat = path.stat()
        
        if as_text:
            try:
                content = path.read_text(encoding=encoding)
                return {
                    "success": True,
                    "content": content,
                    "encoding": encoding,
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                }
            except UnicodeDecodeError:
                # Fallback to base64
                as_text = False
        
        if not as_text:
            content = path.read_bytes()
            content_b64 = base64.b64encode(content).decode('utf-8')
            return {
                "success": True,
                "content": content_b64,
                "encoding": "base64",
                "size": stat.st_size,
                "modified": stat.st_mtime
            }
            
    except Exception as e:
        logger.error(f"Failed to read file: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def validate_dataset(file_path: str) -> dict:
    """
    Validate and analyze dataset file (CSV, JSON, etc).
    
    Args:
        file_path: Path to dataset file
        
    Returns:
        dict: Validation results and data summary
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # Determine file type
        extension = path.suffix.lower()
        
        if extension == '.csv':
            # Use pandas if available, otherwise basic parsing
            try:
                import pandas as pd
                df = pd.read_csv(path)
                return {
                    "success": True,
                    "file_type": "csv",
                    "shape": list(df.shape),
                    "columns": list(df.columns),
                    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "missing_values": {col: int(df[col].isna().sum()) for col in df.columns},
                    "sample": df.head(5).to_dict(orient='records')
                }
            except ImportError:
                # Basic CSV validation without pandas
                with open(path, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        headers = lines[0].strip().split(',')
                        return {
                            "success": True,
                            "file_type": "csv",
                            "headers": headers,
                            "row_count": len(lines) - 1,
                            "sample_rows": [line.strip() for line in lines[1:6]]
                        }
                        
        elif extension == '.json':
            with open(path, 'r') as f:
                data = json.load(f)
                return {
                    "success": True,
                    "file_type": "json",
                    "data_type": type(data).__name__,
                    "length": len(data) if isinstance(data, (list, dict)) else None,
                    "keys": list(data.keys()) if isinstance(data, dict) else None,
                    "sample": str(data)[:500] + "..." if len(str(data)) > 500 else data
                }
        
        else:
            return {
                "success": True,
                "file_type": extension,
                "size": path.stat().st_size,
                "message": "File type not specifically validated"
            }
            
    except Exception as e:
        logger.error(f"Failed to validate dataset: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def read_credentials(
    creds_path: str,
    provider: Optional[str] = None
) -> dict:
    """
    Read and parse credentials file.
    
    Args:
        creds_path: Path to credentials file
        provider: Optional provider hint (bedrock/openai/anthropic)
        
    Returns:
        dict: Parsed credentials or raw content
    """
    try:
        path = Path(creds_path)
        if not path.exists():
            # Try common locations
            common_paths = [
                Path.home() / ".aws" / "credentials",
                Path.home() / ".aws" / path.name,
                Path.home() / path.name
            ]
            
            for common_path in common_paths:
                if common_path.exists():
                    path = common_path
                    break
            else:
                return {
                    "success": False,
                    "error": f"Credentials file not found: {creds_path}"
                }
        
        # Read content
        content = path.read_text()
        
        # Mask sensitive parts for logging
        masked_content = content
        for key in ['KEY', 'SECRET', 'TOKEN', 'PASSWORD']:
            import re
            masked_content = re.sub(
                rf'({key}[^=]*=\s*)"?([^"\s]+)"?',
                rf'\1"***MASKED***"',
                masked_content,
                flags=re.IGNORECASE
            )
        
        logger.info(f"Read credentials from: {path}")
        logger.debug(f"Masked content: {masked_content[:200]}...")
        
        return {
            "success": True,
            "credentials_text": content,
            "source_path": str(path),
            "provider_hint": provider
        }
        
    except Exception as e:
        logger.error(f"Failed to read credentials: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def save_download_locally(
    content_b64: str,
    target_path: str,
    create_dirs: bool = True
) -> dict:
    """
    Save downloaded content to local file.
    
    Args:
        content_b64: Base64 encoded content
        target_path: Where to save the file
        create_dirs: Create parent directories if needed
        
    Returns:
        dict: Save result
    """
    try:
        path = Path(target_path)
        
        # Create directories if needed
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Decode and save
        content = base64.b64decode(content_b64)
        path.write_bytes(content)
        
        logger.info(f"Saved file to: {path}")
        
        return {
            "success": True,
            "saved_path": str(path),
            "size": len(content)
        }
        
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def create_config_template(
    dataset_path: Optional[str] = None,
    task_type: str = "auto"
) -> dict:
    """
    Create AutoGluon config template based on dataset.
    
    Args:
        dataset_path: Optional path to dataset for analysis
        task_type: Task type (auto/classification/regression)
        
    Returns:
        dict: Config template
    """
    config = {
        "task": task_type,
        "label": "target",  # Update based on dataset
        "time_limit": 300,
        "presets": "best_quality",
        "eval_metric": "auto",
        "holdout_frac": 0.2,
        "num_trials": 5
    }
    
    if dataset_path:
        # Try to infer from dataset
        validation = await validate_dataset(dataset_path)
        if validation["success"] and validation.get("columns"):
            # Suggest label column
            columns = validation["columns"]
            likely_labels = [col for col in columns if 
                            col.lower() in ['target', 'label', 'y', 'class', 'output']]
            if likely_labels:
                config["label"] = likely_labels[0]
    
    return {
        "success": True,
        "config": config,
        "yaml_content": json.dumps(config, indent=2)  # Convert to YAML format
    }


@mcp.tool()
async def clear_cache(cache_id: Optional[str] = None) -> dict:
    """
    Clear cached data.
    
    Args:
        cache_id: Specific cache to clear (or None for all)
        
    Returns:
        dict: Clear result
    """
    if cache_id:
        if cache_id in data_cache:
            del data_cache[cache_id]
            return {
                "success": True,
                "message": f"Cleared cache: {cache_id}"
            }
        else:
            return {
                "success": False,
                "error": f"Cache ID not found: {cache_id}"
            }
    else:
        # Clear all expired caches
        expired = []
        for cid, cached in list(data_cache.items()):
            age = (datetime.now() - cached["timestamp"]).seconds
            if age > cache_timeout:
                del data_cache[cid]
                expired.append(cid)
        
        return {
            "success": True,
            "message": f"Cleared {len(expired)} expired caches",
            "active_caches": len(data_cache)
        }


# ==================== Prompts ====================

@mcp.prompt()
def local_file_workflow() -> str:
    """Complete local file handling workflow"""
    return """
    Local File Handling Workflow:
    
    1. Explore and Prepare:
       - Use explore_directory to browse local folders
       - Use validate_dataset to check data files
       - Use prepare_local_folder to prepare for upload
       
    2. Upload Process:
       - prepare_local_folder returns a cache_id
       - Use get_cached_data with cache_id to retrieve prepared data
       - Pass the data to remote server's upload_input_folder
       
    3. Credentials:
       - Use read_credentials to load AWS/API credentials
       - Pass credentials_text to remote server's start_task
       
    4. Save Results:
       - After remote task completes and files are downloaded
       - Use save_download_locally to save each file
       
    Tips:
    - Cache expires after 1 hour
    - Large files (>100MB) are skipped by default
    - Use skip_patterns to exclude file types
    """


# ==================== Main ====================

if __name__ == "__main__":
    # Run on a different port than the proxy
    mcp.run(transport="http", host="127.0.0.1", port=8001)
