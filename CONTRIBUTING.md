# Contributing to SVAF

Thank you for your interest in contributing to SVAF! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **SVAF version** and environment details
- **Sample container** (if applicable)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Provide:

- **Use case** description
- **Proposed solution**
- **Alternative approaches** considered
- **Impact** on existing functionality

### Pull Requests

1. **Fork** the repository
2. **Create a branch** (`git checkout -b feature/amazing-feature`)
3. **Make changes** following coding standards
4. **Add tests** for new functionality
5. **Run tests** (`pytest`)
6. **Update documentation**
7. **Commit** with clear messages
8. **Push** to your fork
9. **Open a Pull Request**

## Development Setup

### Prerequisites

- Python 3.9+
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/Schamane-MadMax/SVAF.git
cd svaf

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,all]"

# Run tests
pytest

# Check code style
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Coding Standards

### Python Style

- Follow **PEP 8**
- Use **Black** for formatting (line length: 100)
- Use **type hints** for all functions
- Write **docstrings** for public APIs

Example:

```python
def parse_transcript(
    file_path: Path,
    language: str = "en"
) -> Transcript:
    """Parse transcript from JSON file.

    Args:
        file_path: Path to transcript JSON file
        language: Language code (default: "en")

    Returns:
        Parsed Transcript object

    Raises:
        TranscriptParseError: If file is invalid
    """
    pass
```

### Testing

- **Minimum 90% code coverage**
- Write tests for:
  - Happy path
  - Edge cases
  - Error conditions
- Use **pytest** fixtures for reusable test data
- Name tests descriptively: `test_<function>_<scenario>`

Example:

```python
def test_parser_handles_missing_transcript():
    """Test that parser handles containers without transcripts."""
    parser = SVAFParser()
    container = parser.parse("minimal.svaf")
    assert container.transcripts == {}
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance

Examples:
```
feat(parser): add lazy loading for large containers
fix(builder): validate event timestamps
docs(readme): update installation instructions
```

## RFC Process

Major changes require an RFC (Request for Comments):

1. **Create RFC document** in `docs/rfcs/`
2. **Open GitHub issue** for discussion
3. **Gather feedback** from community
4. **Update RFC** based on feedback
5. **Get approval** from core team
6. **Implement** the RFC

RFC Template: `docs/rfcs/RFC-TEMPLATE.md`

## Documentation

- **Keep docs updated** with code changes
- **Add examples** for new features
- **Update changelog** (`CHANGELOG.md`)
- **Document breaking changes**

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=svaf --cov-report=html

# Specific test file
pytest tests/test_parser.py

# Specific test
pytest tests/test_parser.py::test_parse_minimal_container
```

### Test Fixtures

Add test containers in `tests/fixtures/`:
- `minimal.svaf` - Minimal valid container
- `podcast.svaf` - Podcast example
- `lecture.svaf` - Lecture with slides
- `invalid_*.svaf` - Invalid containers for error testing

## Release Process

(For maintainers)

1. **Update version** in `pyproject.toml` and `src/svaf/__init__.py`
2. **Update CHANGELOG.md**
3. **Create release commit**: `chore: release v1.0.0`
4. **Tag release**: `git tag v1.0.0`
5. **Push**: `git push && git push --tags`
6. **Build**: `python -m build`
7. **Publish**: `twine upload dist/*`

## Community

- **GitHub Discussions**: For questions and ideas
- **Discord**: (coming soon)
- **Monthly Meetups**: (coming soon)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to reach out via:
- GitHub Issues
- GitHub Discussions
- Email: [maintainer email]

Thank you for contributing! 🎉
