# Contributing Guidelines

Thank you for your interest in contributing to this project! We welcome contributions from everyone. This document provides guidelines and best practices for contributing.


## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing. By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

There are many ways to contribute to this project:

- **Report Bugs**: Submit bug reports with detailed information
- **Suggest Features**: Propose new features or improvements
- **Improve Documentation**: Fix typos, clarify explanations, add examples
- **Submit Code**: Fix bugs or implement new features
- **Review Pull Requests**: Help review and test contributions from others

## Getting Started

### Prerequisites

- Python 3.8+
- Deepseek LLM access
- Git

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/LDFLK/gztarchiver.git`
3. Install dependencies: `pip install -r requirements.txt`
4. Create a branch: `git checkout -b feature/your-feature-name`

## Making Changes

### Branching Strategy

- `feature/` - for new features
- `fix/` - for bug fixes
- `docs/` - for documentation changes


Create a topic branch from the main branch for your changes:

```bash
git checkout -b feature/your-feature-name
```

### Commit Messages

Write clear and meaningful commit messages. We recommend following this format:

```
[TYPE] Short description (max 50 chars)

Longer description if needed. Explain the "why" behind the change,
not just the "what". Reference any related issues.

Fixes #123
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Coding Standards

- Follow PEP 8 for Python code
- Run `black` for formatting
- Run `flake8` for linting


### Testing

- Add unit tests for new functionality
- Ensure all tests pass: `pytest`
- Maintain or improve code coverage

All changes should include appropriate tests. Run the test suite before submitting:

```bash
python3 -m pytest
```

## Submitting Changes

### Pull Request Process

1. Ensure your code follows the project's coding standards
2. Update documentation if needed
3. Add or update tests as appropriate
4. Run the full test suite and ensure it passes
5. Push your branch and create a Pull Request

### Pull Request Guidelines

- Provide a clear title and description
- Reference any related issues (e.g., "Fixes #123")
- Keep changes focused and atomic
- Be responsive to feedback and review comments


### Review Process

- PRs require at least one approval from a maintainer
- CI checks must pass
- Changes may be requested before merging


## Communication

- GitHub Issues: For bug reports and feature requests
- GitHub Discussions: For questions and general discussion
- Mail: [contact@datafoundation.lk](mailto:contact@datafoundation.lk)
- Discord: [Lanka Data Foundation Discord Channel](https://discord.com/invite/mg94NtHD9Y)

## Recognition

We value all contributions and appreciate your effort to improve this project!

## Additional Resources

- Please reffer to the [Project Documentation](README.md)

---

*These guidelines are inspired by the [Apache Way](https://www.apache.org/theapacheway/) and [Open Source Guides](https://opensource.guide/).*