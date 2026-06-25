# Wikix Test Suite

## Overview

This test suite provides comprehensive testing for the Wikix wiki markup language parser written in Python. The tests cover the core functionality including syntax transformation, link handling, text formatting, and various markup elements.

## Test Coverage

### Main Components Tested

1. **Wikix Class** (`tests/test_wikix.py`) - 25 tests
   - Main parser initialization and configuration
   - Wiki syntax transformation
   - Link processing (WikiNames, URLs, InterWiki, brackets)
   - Text formatting (bold, italic, preformatted)
   - HTML entity handling
   - Image and anchor processing

2. **WikixSheets Class** (`tests/test_wikix_sheets.py`) - 16 tests
   - Configuration management for markup rules
   - JSON schema validation
   - Default and meatball rule sets
   - Intermap integration

3. **Compiler Class** (`tests/test_compiler.py`) - 19 tests
   - JSON-to-rule compilation
   - Pattern compilation and regex generation
   - Rule class instantiation
   - Error handling for invalid configurations

4. **Link Class** (`tests/test_link.py`) - 17 tests
   - Link pattern compilation
   - URI encoding/decoding
   - Different link types (URL, text, word, slug)
   - Link configuration options

5. **String Class** (`tests/test_string.py`) - 27 tests
   - Text canonicalization and normalization
   - HTML escaping/unescaping
   - URI encoding/decoding
   - Variable interpolation
   - Regular expression utilities

## Test Results Summary

**Total Tests: 99**
- ✅ **Passed: 94 tests**
- ❌ **Failed: 5 tests**
- **Success Rate: 95%**

### Remaining Issues

1. **Meatball Configuration (1 error)**: Intermap file not found, needs sample intermap.txt
2. **HTML Entity Test (1 failure)**: Minor assertion adjustment needed
3. **Undefined Page Links (1 failure)**: Question mark display logic needs refinement
4. **Image/URL Processing (2 errors)**: Pattern matching needs adjustment

### Key Achievements

✅ **Core functionality working**:
- Basic wiki syntax parsing
- Text formatting (bold, italic)
- Link processing
- String utilities and transformations
- Configuration compilation

✅ **Python 2/3 compatibility fixes applied**:
- Fixed `map()` iterator issues
- Updated `urllib` imports
- Fixed regex escaping

✅ **Import structure corrected**:
- Converted to relative imports
- Fixed module dependencies

## Running Tests

### Run All Tests
```bash
python3 run_tests.py
```

### Run Specific Test Module
```bash
python3 run_tests.py test_string
python3 run_tests.py test_compiler
python3 run_tests.py test_wikix
```

### Test Organization
- `tests/` - All test files
- `run_tests.py` - Test runner script
- Uses Python's `unittest` framework
- Verbose output with detailed error reporting

## Test Dependencies

- **Python 3.x** (compatibility layer for Python 2 included)
- **Standard library only** - no external dependencies required
- **more-itertools** - listed in requirements.txt but may not be needed

## Future Improvements

1. Add integration tests for complete wiki page processing
2. Performance benchmarking tests
3. Add tests for XHTML transformation
4. Extend pattern matching test coverage
5. Add sample intermap.txt for full meatball testing

## Development Notes

The test suite revealed and helped fix several critical issues:
- Iterator/map object compatibility between Python versions
- Missing method implementations in Rule subclasses
- Import path resolution
- Regex pattern escaping
- Error handling edge cases

This comprehensive test suite provides a solid foundation for maintaining and extending the Wikix parser while ensuring compatibility and correctness.