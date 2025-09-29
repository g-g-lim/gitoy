# gitoy :)

A simple Git-like version control system built with Python, featuring SQLite-based storage and file compression.
for my toy project.

## Features

- Repository initialization and management
- Branch operations (create, list, delete)
- File tracking with hash-based content storage
- SQLite database for metadata persistence
- Zstandard compression for efficient storage
- Commit and commit log operations

## Installation

```bash
git clone <repository-url>
cd gitoy-2
uv sync --extra dev
uv pip install . -e
```

## Usage

```bash
# Initialize a repository
uv run gitoy init

# List branches
uv run gitoy branch

# Add files to index
uv run gitoy add file1.txt file2.txt

# Show version
uv run gitoy version
```

## Requirements

- Python 3.13+
- uv (for dependency management)

## Testing

```bash
uv run pytest
```
