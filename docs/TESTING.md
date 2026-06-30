<!-- generated-by: gsd-doc-writer -->
# Testing

## Test Framework and Setup

The project uses `pytest` for testing. You can install it if you haven't already by running `pip install pytest`.

## Running Tests

Run the full test suite using the following command:

```bash
pytest tests/
```

To run a specific test file:
```bash
pytest tests/test_filename.py
```

## Writing New Tests

- Test files should be placed in the `tests/` directory.
- Use the `test_*.py` naming convention for test files.
- Individual test functions should begin with `test_`.

## Coverage Requirements

No coverage threshold configured.

## CI Integration

No CI/CD pipeline detected. Tests should be run manually before submitting pull requests.
