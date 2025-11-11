# gitoy :)

A simple Git-like version control system built with Python, featuring SQLite-based storage and file compression
for my toy project.

## Features

- Repository initialization and management
- Branch operations (create, list, delete)
- File tracking with hash-based content storage
- SQLite database for metadata persistence
- Zstandard compression for efficient storage
- Commit and commit log operations
- Status and checkout functionalities

## Installation

```bash
git clone <repository-url>
cd gitoy
uv sync --extra dev

# Install gitoy development mode
uv pip install -e .
```

After installation, you can use `gitoy` command anywhere:

```bash
gitoy --help
gitoy version
```

## Usage

```bash
# Initialize a repository
gitoy init

# List branches
gitoy branch

# Create a new branch
gitoy branch create new_feature

# Add files to index
gitoy add file1.txt file2.txt

# Create a commit
gitoy commit -m "Your commit message"

# View commit history
gitoy log

# Checkout a branch or commit
gitoy checkout --ref_name main 

# status of the repository
gitoy status
```

## Requirements

- Python 3.13+
- uv (for dependency management)

## Testing

```bash
uv run pytest
```

## Formatting

```bash
uvx ruff format
```
