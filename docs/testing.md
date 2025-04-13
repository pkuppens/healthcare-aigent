# Testing Strategy

## Test Categories

### Unit Tests
- **Database Tools**
  - Mock database operations (CRUD)
  - Audit logging functionality
  - Error handling for invalid operations
  - Data validation and sanitization
  - Transaction rollback scenarios

- **LLM Configuration**
  - Factory pattern implementation
  - Model selection based on task type
  - Environment variable handling
  - API key validation
  - Temperature and parameter configuration

- **Agent System**
  - Agent role and goal validation
  - Task assignment and execution
  - Memory and context management
  - Tool integration
  - Error handling and recovery

- **Task Processing**
  - Input validation
  - Output formatting
  - Task prioritization
  - Dependency resolution
  - Timeout handling

### Integration Tests
- **LLM Connectivity**
  - OpenAI API integration
  - Ollama local model integration
  - Model fallback mechanisms
  - Rate limiting handling
  - Connection timeout scenarios

- **Agent Collaboration**
  - Inter-agent communication
  - Task delegation
  - Result aggregation
  - Conflict resolution
  - Parallel execution

- **System Workflow**
  - End-to-end processing pipeline
  - Data flow validation
  - State management
  - Resource cleanup
  - Performance monitoring

### LLM Tests
- **Model Performance**
  - Response quality assessment
  - Latency measurements
  - Token usage tracking
  - Error rate monitoring
  - Model comparison metrics

- **Security & Compliance**
  - Data privacy validation
  - HIPAA compliance checks
  - Audit trail verification
  - Access control testing
  - Encryption validation

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit      # Unit tests only
pytest -m integration  # Integration tests only
pytest -m llm       # LLM tests only

# Skip integration tests that require external services
pytest -m "not integration"

# Run tests with detailed output
pytest -v

# Run tests and stop on first failure
pytest -x

# Run tests and show extra test summary info
pytest -ra
```

### Test Coverage
```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View coverage in terminal
pytest --cov=src --cov-report=term-missing

# Generate coverage report with branch coverage
pytest --cov=src --cov-branch --cov-report=html
```

### Debugging Tests

1. Using VSCode:
   - Set breakpoints in your test files
   - Use the "Python: Debug Tests" launch configuration
   - Use the "Python: Debug Current Test File" for focused debugging
   - Use the "Python: Debug All Tests" for full test suite debugging

2. Using pytest directly:
```bash
# Run tests with debugger
pytest --pdb

# Run specific test with debugger
pytest path/to/test_file.py::test_function --pdb
```

### Test Configuration

The project uses `tests/pytest.ini` for test configuration:
```ini
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    llm: LLM connectivity tests
testpaths = tests
python_files = test_*.py
```

## Test Examples

### Unit Test Example
```python
def test_database_read_patient_data():
    """Test reading patient data from database."""
    db = MockHealthcareDatabase()
    patient_data = db.read_patient_data("test_patient")
    assert patient_data is not None
    assert "history" in patient_data
    assert "allergies" in patient_data
```

### Integration Test Example
```python
@pytest.mark.integration
def test_agent_collaboration():
    """Test collaboration between preprocessing and clinical extraction agents."""
    preprocessing_agent = PreprocessingAgent()
    clinical_agent = ClinicalExtractionAgent()
    
    result = preprocessing_agent.process("Patient conversation")
    clinical_data = clinical_agent.extract(result)
    
    assert clinical_data is not None
    assert "diagnosis" in clinical_data
    assert "treatment" in clinical_data
```

### LLM Test Example
```python
@pytest.mark.llm
def test_llm_connectivity():
    """Test connectivity to OpenAI API."""
    llm = LLMFactory.create_llm(LLMType.CLOUD_FAST)
    response = llm.invoke("Test message")
    assert response is not None
    assert len(response.content) > 0
```

## Best Practices

### Test Organization
- Keep tests close to the code they test
- Use descriptive test names
- Group related tests in classes
- Use fixtures for common setup
- Follow the Arrange-Act-Assert pattern
- Use meaningful test data
- Document test dependencies

### Test Data
- Use realistic test data
- Include edge cases
- Mock external dependencies
- Clean up test data after tests
- Use factories for test data generation
- Consider using faker for realistic data
- Maintain separate test data files

### Test Maintenance
- Update tests when code changes
- Remove obsolete tests
- Keep test documentation current
- Monitor test performance
- Regular test suite maintenance
- Version control test data
- Document test environment requirements

### Additional Considerations

#### Performance Testing
- Response time benchmarks
- Resource usage monitoring
- Load testing scenarios
- Scalability testing
- Memory leak detection

#### Security Testing
- Input validation
- Authentication testing
- Authorization testing
- Data encryption
- Secure communication
- API security

#### Accessibility Testing
- WCAG compliance
- Screen reader compatibility
- Keyboard navigation
- Color contrast
- Text scaling

#### Local Development
- Fast feedback loops
- Incremental testing
- Test isolation
- Mock external services
- Local service containers

#### CI/CD Integration
- Automated test runs
- Test result reporting
- Coverage thresholds
- Performance benchmarks
- Security scanning
- Dependency updates

#### Test Environment
- Environment variables
- Service dependencies
- Database setup
- Network configuration
- Resource cleanup
- Logging configuration

#### Documentation
- Test purpose
- Setup instructions
- Dependencies
- Expected outcomes
- Edge cases
- Troubleshooting 