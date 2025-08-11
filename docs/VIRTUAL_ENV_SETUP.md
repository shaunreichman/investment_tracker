# Virtual Environment Setup

## Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Verify activation (should show .venv path)
which python

# Install dependencies (if needed)
pip install -r requirements.txt

# Run tests
python -m pytest
```

## Environment Details

- **Python Version**: 3.11+
- **Virtual Environment**: `.venv/` directory
- **Package Manager**: pip
- **Testing Framework**: pytest

## Common Commands

```bash
# Activate
source .venv/bin/activate

# Deactivate
deactivate

# Check installed packages
pip list

# Update pip
pip install --upgrade pip

# Install dev dependencies
pip install -r requirements-dev.txt
```

## VS Code Integration

The `.vscode/settings.json` file automatically:
- Sets the Python interpreter to `.venv/bin/python`
- Activates the environment in integrated terminals
- Enables pytest testing
- Configures linting and formatting

## Troubleshooting

If you get "command not found" errors:
1. Ensure `.venv/bin` is in your PATH
2. Try `source .venv/bin/activate` again
3. Check that the virtual environment was created correctly

If packages are missing:
1. Activate the environment: `source .venv/bin/activate`
2. Install: `pip install -r requirements.txt`
