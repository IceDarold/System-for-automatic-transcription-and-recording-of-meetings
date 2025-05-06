# Backend Tests

This directory contains the test suite for the backend application. The tests are organized into several categories:

## Test Structure

- `conftest.py` - Common test fixtures and configuration
- `test_models.py` - Tests for database models
- `test_api.py` - Tests for API endpoints
- `test_services.py` - Tests for business logic services

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up environment variables:
```bash
export TESTING=true
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_db
```

### Running Tests

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_models.py
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```

Run tests with verbose output:
```bash
pytest -v
```

## Test Categories

### Model Tests
- Test model creation and validation
- Test relationships between models
- Test model constraints and validations

### API Tests
- Test all HTTP endpoints
- Test request validation
- Test response formats
- Test error handling
- Test authentication and authorization

### Service Tests
- Test business logic
- Test external service integrations
- Test error handling
- Test edge cases

## Writing New Tests

1. Create a new test file in the appropriate category
2. Use existing fixtures from `conftest.py`
3. Follow the naming convention: `test_*.py`
4. Write descriptive test names
5. Include docstrings for test functions
6. Use appropriate assertions
7. Mock external dependencies

## Best Practices

1. Keep tests independent
2. Use meaningful test data
3. Clean up after tests
4. Mock external services
5. Test both success and failure cases
6. Test edge cases
7. Keep tests fast and focused

## Continuous Integration

Tests are automatically run on GitHub Actions for:
- Every push to main and develop branches
- Every pull request
- Scheduled runs

## Coverage Reports

Coverage reports are generated automatically and can be viewed:
1. In the terminal when running tests with coverage
2. In the GitHub Actions artifacts
3. On Codecov.io (if configured)

## Troubleshooting

Common issues and solutions:

1. Database connection issues:
   - Check DATABASE_URL environment variable
   - Ensure PostgreSQL is running
   - Check database permissions

2. Test failures:
   - Check test data
   - Verify environment variables
   - Check for missing dependencies

3. Slow tests:
   - Use appropriate fixtures
   - Mock external services
   - Optimize database queries 