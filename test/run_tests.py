#!/usr/bin/env python3
"""
Test runner script for Repository tests.

Usage:
  python test/run_tests.py                    # Run all tests
  python test/run_tests.py --verbose          # Run with detailed output
  python test/run_tests.py --specific <test>  # Run specific test
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run tests using pytest with proper environment setup."""
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    # Build pytest command - use uv run for consistent environment
    cmd = ["uv", "run", "pytest", "test/test_repository.py"]
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if "--verbose" in sys.argv or "-v" in sys.argv:
            cmd.append("-v")
        if "--specific" in sys.argv:
            try:
                idx = sys.argv.index("--specific")
                if idx + 1 < len(sys.argv):
                    test_name = sys.argv[idx + 1]
                    cmd[-1] = f"test/test_repository.py::{test_name}"
            except (IndexError, ValueError):
                print("Usage: --specific <TestClass::test_method>")
                return 1
    else:
        cmd.append("-v")  # Default to verbose
    
    # Add coverage if pytest-cov is available
    try:
        # Check if pytest-cov is available
        result = subprocess.run(
            ["uv", "run", "python", "-c", "import pytest_cov"], 
            capture_output=True, 
            cwd=project_root
        )
        if result.returncode == 0:
            cmd.extend(["--cov=src", "--cov-report=term-missing"])
    except Exception:
        pass  # Continue without coverage
    
    # Run tests
    print(f"Running command: {' '.join(cmd)}")
    print(f"Working directory: {project_root}")
    print("=" * 50)
    
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 