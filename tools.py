# tools.py
import subprocess
import tempfile
import time
import json
from typing import Tuple, Dict, Any


# ------------------------------------------------------
# 1. Code Evaluation Tool
# ------------------------------------------------------
def evaluate_python_code(code: str, input_data: str = "") -> Tuple[bool, str]:
    """
    Safely execute small Python code snippets by running them
    inside a separate subprocess.

    Returns:
        (success: bool, output_or_error: str)
    """
    try:
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(code)
            file_path = f.name

        start_time = time.time()

        # Run the temporary file using subprocess
        result = subprocess.run(
            ["python", file_path],
            capture_output=True,
            text=True,
            input=input_data,
            timeout=5
        )

        elapsed = time.time() - start_time

        # If Python returned an error code, return the stderr
        if result.returncode != 0:
            return False, f"Error:\n{result.stderr}"

        # Successful run
        return True, f"Output: {result.stdout.strip()}\nTime: {elapsed:.3f}s"

    except Exception as e:
        return False, f"Exception: {str(e)}"


# ------------------------------------------------------
# 2. Simple Search Tool (mock lookup)
# ------------------------------------------------------
def simple_search(query: str, topics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates an external knowledge search.

    It finds the closest matching topic by name.
    """
    query = query.lower()

    # Try exact or partial match
    for key in topics.keys():
        if query in key.lower():
            return topics[key]

    # Fallback: return the first topic
    return list(topics.values())[0]
