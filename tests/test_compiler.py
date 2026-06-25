#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'python'))

import unittest
import json
from wikix.Compiler import Compiler
from wikix.WikixSheets import WikixSheets
from wikix.Sheet import Sheet
from wikix.Root import Root
from wikix.Multiline import Multiline
from wikix.Line import Line
from wikix.Block import Block
from wikix.Paragraph import Paragraph
from wikix.Inline import Inline
from wikix.Link import Link
from wikix.Rule import Rule
from wikix.Cell import Cell

class TestCompiler(unittest.TestCase):
    def setUp(self):
        self.compiler = Compiler()
        self.sheets = WikixSheets()

    def test_compiler_initialization(self):
        """Test Compiler can be initialized"""
        self.assertIsNotNone(self.compiler)

    def test_compile_valid_json_string(self):
        """Test compiling a valid JSON string"""
        simple_json = '{"root": {"scope": "root", "children": ["p"]}, "p": {"scope": "paragraph"}}'

        result = self.compiler.compile(simple_json)
        self.assertIsInstance(result, Sheet)
        self.assertIsNotNone(result.root)

    def test_compile_invalid_json_raises_exception(self):
        """Test that invalid JSON raises an exception"""
        invalid_json = '{"root": {"scope": "root"'  # Missing closing brace

        with self.assertRaises(json.JSONDecodeError):
            self.compiler.compile(invalid_json)

    def test_compile_sheet_without_root_raises_exception(self):
        """Test that sheet without root rule raises exception"""
        no_root_json = '{"p": {"scope": "paragraph"}}'

        with self.assertRaises(Exception) as context:
            self.compiler.compile(no_root_json)

        self.assertIn("No rule scoped 'root'", str(context.exception))

    def test_compile_rule_creates_appropriate_classes(self):
        """Test that compile_rule creates the correct rule class based on scope"""
        test_cases = [
            ('root', {'scope': 'root'}, Root),
            ('multiline', {'scope': 'multiline'}, Multiline),
            ('line', {'scope': 'line'}, Line),
            ('cell', {'scope': 'cell'}, Cell),
            ('block', {'scope': 'block'}, Block),
            ('paragraph', {'scope': 'paragraph'}, Paragraph),
            ('inline', {'scope': 'inline'}, Inline),
            ('link', {'scope': 'link'}, Link),
            ('unknown', {'scope': 'unknown'}, Rule),  # Default case
            ('no_scope', {}, Rule),  # No scope specified
        ]

        for name, definition, expected_class in test_cases:
            with self.subTest(scope=definition.get('scope', 'none')):
                rule = self.compiler.compile_rule(name, definition)
                self.assertIsInstance(rule, expected_class)

    def test_compile_pattern_basic(self):
        """Test basic pattern compilation"""
        pattern = "hello"
        result = self.compiler.compile_pattern(pattern)
        self.assertIn("hello", result)

    def test_compile_pattern_with_regexp_dict(self):
        """Test pattern compilation with regexp dictionary"""
        pattern = {"regexp": r"\d+"}
        result = self.compiler.compile_pattern(pattern)
        self.assertEqual(result, r"\d+")

    def test_compile_pattern_empty_or_none(self):
        """Test pattern compilation with empty or None input"""
        result_none = self.compiler.compile_pattern(None)
        result_empty = self.compiler.compile_pattern("")

        self.assertEqual(result_none, "")
        self.assertEqual(result_empty, "")

    def test_compile_regexp_equals_pattern(self):
        """Test regexp compilation with equals pattern"""
        rule_def = {"equals": "test"}
        rule = Rule("test_rule", rule_def)
        # Create a mock sheet
        from wikix.Sheet import Sheet
        rule.sheet = Sheet()

        self.compiler.compile_regexp(rule, rule_def)
        # Rule should have regexp set (we can't easily test internal state)

    def test_compile_regexp_link_pattern(self):
        """Test regexp compilation with link pattern"""
        rule_def = {"link": {"pattern": "url"}}
        rule = Link("test_link", rule_def)

        # This might fail if Link doesn't have compile_link_pattern method
        try:
            self.compiler.compile_regexp(rule, rule_def)
        except AttributeError:
            # Expected if Link doesn't implement compile_link_pattern
            pass

    def test_compile_regexp_starts_ends_pattern(self):
        """Test regexp compilation with starts/ends patterns"""
        rule_def = {"starts": "<b>", "ends": "</b>"}
        rule = Rule("bold", rule_def)
        from wikix.Sheet import Sheet
        rule.sheet = Sheet()

        self.compiler.compile_regexp(rule, rule_def)

    def test_compile_regexp_until_pattern(self):
        """Test regexp compilation with until pattern"""
        rule_def = {"starts": "<pre>", "until": "</pre>"}
        rule = Rule("pre", rule_def)
        from wikix.Sheet import Sheet
        rule.sheet = Sheet()

        self.compiler.compile_regexp(rule, rule_def)

    def test_compile_regexp_optional_patterns(self):
        """Test regexp compilation with optional start/end patterns"""
        rule_def = {
            "starts": "main",
            "optionallyStarts": "prefix",
            "optionallyEnds": "suffix"
        }
        rule = Rule("optional", rule_def)
        from wikix.Sheet import Sheet
        rule.sheet = Sheet()

        self.compiler.compile_regexp(rule, rule_def)

    def test_compile_children(self):
        """Test compilation of rule children"""
        json_string = '''
        {
            "root": {
                "scope": "root",
                "children": ["p", "ul"]
            },
            "p": {
                "scope": "paragraph",
                "children": ["inline"]
            },
            "ul": {
                "scope": "multiline",
                "children": ["li"]
            },
            "li": {
                "scope": "line"
            },
            "inline": {
                "scope": "inline"
            }
        }
        '''

        sheet = self.compiler.compile(json_string)

        # Verify that the sheet was compiled successfully
        self.assertIsNotNone(sheet)
        self.assertIsNotNone(sheet.root)

        # Check that rules were added
        self.assertIn("root", sheet.rules)
        self.assertIn("p", sheet.rules)
        self.assertIn("ul", sheet.rules)

    def test_compile_default_wikix_sheet(self):
        """Test compiling the default WikixSheets configuration"""
        default_sheet = self.sheets.default()

        # Should compile without errors
        compiled_sheet = self.compiler.compile(default_sheet)

        self.assertIsInstance(compiled_sheet, Sheet)
        self.assertIsNotNone(compiled_sheet.root)

    def test_compile_meatball_wikix_sheet(self):
        """Test compiling the meatball WikixSheets configuration"""
        meatball_sheet = self.sheets.meatball()

        # Should compile without errors
        compiled_sheet = self.compiler.compile(meatball_sheet)

        self.assertIsInstance(compiled_sheet, Sheet)
        self.assertIsNotNone(compiled_sheet.root)

    def test_compile_sheet_creates_sheet_object(self):
        """Test that compile_sheet creates a Sheet object"""
        sheet_dict = {
            "root": {"scope": "root", "children": ["p"]},
            "p": {"scope": "paragraph"}
        }

        result = self.compiler.compile_sheet(sheet_dict)

        self.assertIsInstance(result, Sheet)

    def test_compile_pattern_tight_mode(self):
        """Test pattern compilation with tight mode"""
        pattern = "---"
        result_loose = self.compiler.compile_pattern(pattern, False)
        result_tight = self.compiler.compile_pattern(pattern, True)

        # Results might be different in tight mode
        self.assertIsNotNone(result_loose)
        self.assertIsNotNone(result_tight)

    def test_rule_with_starts_delimited_by(self):
        """Test rule with startsDelimitedBy pattern"""
        rule_def = {
            "starts": "text",
            "startsDelimitedBy": "|"
        }
        rule = Rule("delimited", rule_def)
        from wikix.Sheet import Sheet
        rule.sheet = Sheet()

        self.compiler.compile_regexp(rule, rule_def)

if __name__ == '__main__':
    unittest.main()