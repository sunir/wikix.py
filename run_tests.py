#!/usr/bin/env python
"""
Wikix Test Runner

This script runs all tests for the Wikix project using Python's unittest framework.
"""
import sys
import os
import unittest

# Add the lib/python directory to the path so we can import the wikix modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib', 'python'))

def discover_and_run_tests():
    """Discover and run all tests in the tests directory"""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(script_dir, 'tests')

    if not os.path.exists(tests_dir):
        print("Error: tests directory not found at", tests_dir)
        return False

    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir, pattern='test_*.py')

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    # Return True if all tests passed
    return result.wasSuccessful()

def run_specific_test_module(module_name):
    """Run tests from a specific module"""
    try:
        # Import the specific test module
        test_module = __import__(f'tests.{module_name}', fromlist=[''])

        # Load tests from the module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)

        # Run tests
        runner = unittest.TextTestRunner(verbosity=2, buffer=True)
        result = runner.run(suite)

        return result.wasSuccessful()
    except ImportError as e:
        print(f"Error importing test module '{module_name}': {e}")
        return False

def main():
    """Main test runner function"""
    if len(sys.argv) > 1:
        # Run specific test module
        module_name = sys.argv[1]
        if not module_name.startswith('test_'):
            module_name = 'test_' + module_name

        print(f"Running tests from module: {module_name}")
        success = run_specific_test_module(module_name)
    else:
        # Run all tests
        print("Running all Wikix tests...")
        success = discover_and_run_tests()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()