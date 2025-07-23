# gitoy

A simple Git-like File Version Control CLI tool built with Python. gitoy implements core version control functionalities including repository initialization, branch management, file tracking, and compression with SQLite-based storage.

## Features

- **Repository Management**: Initialize and manage local repositories with file system and database integration
- **Branch Operations**: Create, list, and manage branches with HEAD tracking
- **File Operations**: Add files to the index with hash-based content tracking
- **Database Storage**: SQLite-based persistent storage for version control metadata
- **Compression**: Zstandard compression for efficient storage
- **Entity Management**: Structured handling of commits, refs, trees, blobs, and index entries

## Commands

- `gitoy init`: Initialize a new Gitoy repository
- `gitoy branch`: List, create, or delete branches
- `gitoy add <files>`: Add file contents to the index
- `gitoy version`: Show version information

## Architecture

The project is organized into modular components:

- **CLI Layer**: `GitoyCLI` class with Fire framework integration
- **Commands**: Modular command implementations (`Init`, `Branch`, `Add`)
- **Repository**: Core repository operations and file management
- **Database**: SQLite-based persistence with entity mapping
- **Worktree**: File system operations and repository structure management
- **Utilities**: Console output, result handling, and custom types

## Development Setup

### Prerequisites

- Python 3.13+
- uv (for dependency management)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   uv sync --extra dev
   ```

## Testing

### Running Tests

The project uses pytest for testing with comprehensive test coverage:

```bash
# Run all tests
uvx pytest

# Run with verbose output
uvx pytest --verbose

# Run with specific test case
uvx pytest test/test_repository.py::TestRepositoryInit::test_init_repository

### Type Checking

This project uses `uvx ty` for type checking. The type checker runs automatically before each commit via pre-commit hooks.

To run type checking manually:
```bash
uvx ty check .
```

### Pre-commit Hooks

Pre-commit hooks are set up to run type checking before each commit. To install the hooks:

```bash
uv run pre-commit install
```

To run pre-commit hooks manually:
```bash
uv run pre-commit run --all-files
```

The hooks will prevent commits if there are type checking errors.

#### Troubleshooting VSCode Commits

If you encounter issues with VSCode not finding `uvx` when committing:

1. **Current Solution**: The project uses absolute paths in `.pre-commit-config.yaml`
2. **Alternative**: If issues persist, you can modify the configuration to use:
   ```yaml
   entry: bash -c 'export PATH="$HOME/.local/bin:$PATH" && uvx ty check .'
   ```

3. **Manual Setup**: Ensure your shell profile (`.zshrc`, `.bash_profile`) includes:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

## Usage

```bash
# Show help and available commands
uv run gitoy --help

# Show version information
uv run gitoy version

# Initialize a repository
uv run gitoy init

# List branches  
uv run gitoy branch

# Add files to the index
uv run gitoy add file1.txt file2.txt
```
