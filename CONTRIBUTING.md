# Contributing to SOOPEX

Thank you for your interest in contributing to SOOPEX. This project is in early development and we welcome feedback, bug reports, and contributions.

## How to Contribute

### Specification Feedback

The most valuable contribution at this stage is **feedback on the format specification**. If you work with SoOp data, please:

1. Open a [GitHub Issue](../../issues) describing your use case
2. Identify any fields or structures that don't fit your workflow
3. Suggest additions or modifications

### Bug Reports

Please include:
- Python version and OS
- Minimal reproducible example
- Expected vs. actual behavior
- The `.soop` file (or a minimal excerpt) that triggers the issue

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Ensure tests pass (`pytest tests/ -v`)
4. Ensure code is formatted (`ruff format . && ruff check .`)
5. Submit a pull request

### Test Data

We especially welcome `.soop` files from different receiver/SDR setups. If you can share observation data (even short samples), it helps us validate parser robustness. Please confirm the data is shareable before submitting.

### Parser Implementations

Implementations in other languages (C, MATLAB, Julia, Rust, etc.) are welcome as separate repositories. Please open an issue to coordinate and we will link to your implementation.

## Development Setup

```bash
git clone https://github.com/h-shiono/soopex.git
cd soopex
uv sync --dev
pytest tests/ -v
```

## Code Style

- Formatter: `ruff format`
- Linter: `ruff check`
- Type annotations on all public APIs
- Docstrings: Google style

## Versioning

- Specification and package versions are aligned (spec v0.1 → package v0.1.x)
- Breaking changes to the specification require a MAJOR version bump
- All changes are documented in the changelog

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
