# Contributing to Adaptive MCP Server

## Welcome Contributors! 🚀

We're thrilled that you're interested in contributing to the Adaptive MCP Server. This document provides guidelines for contributing to the project.

## Code of Conduct

Please be respectful, inclusive, and considerate of others. Harassment and discrimination are not tolerated.

## How to Contribute

### 1. Reporting Issues

- Use GitHub Issues to report bugs
- Provide a clear and descriptive title
- Include steps to reproduce the issue
- Mention your environment (Python version, OS)
- Add error logs or screenshots if possible

#### Issue Template
```markdown
### Description
[Brief description of the issue]

### Steps to Reproduce
1. 
2. 
3. 

### Expected Behavior
[What you expected to happen]

### Actual Behavior
[What actually happened]

### Environment
- Python Version:
- OS:
- Adaptive MCP Server Version:
```

### 2. Feature Requests

- Suggest new features via GitHub Issues
- Explain the motivation and use case
- Provide potential implementation ideas if possible

### 3. Development Process

#### Setup
1. Fork the repository
2. Clone your fork
3. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Branching Strategy
- `main`: Stable release branch
- `develop`: Integration branch for next release
- Feature branches: `feature/description`
- Bugfix branches: `bugfix/description`

#### Coding Standards
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions
- 100% test coverage for new code
- Use `black` for formatting
- Use `mypy` for type checking

#### Commit Message Convention
```
<type>(<scope>): <subject>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Formatting changes
- refactor: Code restructuring
- test: Adding/modifying tests
- chore: Maintenance tasks
```

Example:
```
feat(reasoning): Add lateral thinking module
```

### 4. Pull Request Process

1. Ensure all tests pass
2. Update documentation
3. Add tests for new functionality
4. Squash commits
5. Get approval from maintainers

#### PR Template
```markdown
### Description
[Detailed description of changes]

### Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

### Checklist
- [ ] I have performed a self-review
- [ ] I have added tests
- [ ] Documentation updated
- [ ] Code follows project style guidelines
```

### 5. Testing

- Run tests: `pytest`
- Check coverage: `pytest --cov=.`
- Ensure 100% test coverage for new code

### 6. Documentation

- Update docstrings
- Maintain `README.md`
- Update `CHANGELOG.md`
- Add examples in documentation

## Development Workflow

```bash
# Create feature branch
git checkout -b feature/awesome-feature

# Make changes
# Write tests
# Run tests
pytest

# Commit changes
git add .
git commit -m "feat(module): Describe feature"

# Push to fork
git push origin feature/awesome-feature

# Create Pull Request
```

## Questions?

Contact project maintainers or open a GitHub Issue.

Happy Contributing! 🌟
