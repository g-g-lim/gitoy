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
import os
from pathlib import Path

def main():
    """Run tests using pytest with proper environment setup."""
    # Set PYTHONPATH to include src directory
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_path)
    
    # Build pytest command
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
    
    # Add coverage if available
    try:
        cmd.extend(["--cov=src", "--cov-report=term-missing"])
    except ImportError:
        pass
    
    # Run tests
    print(f"Running command: {' '.join(cmd)}")
    print(f"Working directory: {project_root}")
    print("=" * 50)
    
    result = subprocess.run(cmd, cwd=project_root, env=env)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 