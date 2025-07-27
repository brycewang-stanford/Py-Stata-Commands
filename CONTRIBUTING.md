# Contributing to Py-Stata-Commands

We love your input! We want to make contributing to Py-Stata-Commands as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/yourusername/Py-Stata-Commands.git
cd Py-Stata-Commands

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,test,docs]"

# Install pre-commit hooks
pre-commit install
```

## Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting
- **mypy** for type checking

Run all checks:
```bash
black py_stata_commands tests
isort py_stata_commands tests
flake8 py_stata_commands tests
mypy py_stata_commands
```

## Testing

We use pytest for testing. Run tests with:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=py_stata_commands

# Run specific test file
pytest tests/test_tabulate.py
```

## Module Structure

Each module should follow this structure:

```
module_name/
├── __init__.py          # Module exports
├── core.py             # Main functionality
├── utils.py            # Helper functions (if needed)
└── exceptions.py       # Custom exceptions (if needed)
```

## Documentation

- All public functions should have docstrings following NumPy style
- Include examples in docstrings
- Update README.md if adding new features
- Add/update type hints

## Pull Request Process

1. **Create a branch** with a descriptive name:
   ```bash
   git checkout -b feature/add-new-egen-function
   git checkout -b fix/tabulate-missing-values
   ```

2. **Make your changes** following the code style guidelines

3. **Add tests** for any new functionality

4. **Update documentation** if needed

5. **Run the full test suite** to ensure nothing is broken

6. **Submit a pull request** with:
   - Clear title and description
   - Reference to related issues
   - List of changes made
   - Screenshots (if UI changes)

## Issue Reporting

Use GitHub issues to report bugs. When reporting a bug, include:

- **Environment details** (Python version, OS, package versions)
- **Steps to reproduce** the bug
- **Expected behavior** vs actual behavior  
- **Minimal code example** that reproduces the issue
- **Error messages** (full traceback if applicable)

## Feature Requests

Feature requests are welcome! Please:

- Check existing issues first to avoid duplicates
- Clearly describe the feature and its use case
- Explain why it would be useful to other users
- Consider if it fits within the scope of the project

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct:

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative
- Focus on what is best for the community
- Show empathy towards other community members

## Questions?

Feel free to contact the maintainers:
- Open an issue with the "question" label
- Email: brycew6m@stanford.edu

## Recognition

Contributors will be recognized in:
- The README.md contributors section
- Release notes for their contributions
- The project documentation

Thank you for contributing! 🎉
