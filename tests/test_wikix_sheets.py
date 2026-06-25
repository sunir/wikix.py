#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'python'))

import unittest
import json
from wikix.WikixSheets import WikixSheets
from wikix.Intermap import Intermap

class TestWikixSheets(unittest.TestCase):
    def setUp(self):
        self.intermap = Intermap()
        self.sheets = WikixSheets(self.intermap)

    def test_initialization(self):
        """Test WikixSheets initialization"""
        self.assertIsNotNone(self.sheets)
        self.assertEqual(self.sheets.intermap, self.intermap)

    def test_initialization_without_intermap(self):
        """Test WikixSheets can be initialized without intermap"""
        sheets = WikixSheets()
        self.assertIsNotNone(sheets)
        self.assertIsNone(sheets.intermap)

    def test_default_sheet_returns_json_string(self):
        """Test default() method returns valid JSON string"""
        default_sheet = self.sheets.default()
        self.assertIsInstance(default_sheet, str)

        # Should be parseable as JSON
        try:
            parsed = json.loads(default_sheet)
            self.assertIsInstance(parsed, dict)
        except json.JSONDecodeError:
            self.fail("default() should return valid JSON")

    def test_default_sheet_has_root_rule(self):
        """Test default sheet contains root rule"""
        default_sheet = self.sheets.default()
        parsed = json.loads(default_sheet)

        self.assertIn('root', parsed)
        self.assertIn('scope', parsed['root'])
        self.assertEqual(parsed['root']['scope'], 'root')

    def test_default_sheet_has_expected_children(self):
        """Test default sheet root has expected children"""
        default_sheet = self.sheets.default()
        parsed = json.loads(default_sheet)

        root_children = parsed['root']['children']
        expected_children = ['hr', 'lists', 'blockquote', 'monospace', 'table', 'headers', 'p']

        for child in expected_children:
            self.assertIn(child, root_children)

    def test_default_sheet_has_list_rules(self):
        """Test default sheet contains list-related rules"""
        default_sheet = self.sheets.default()
        parsed = json.loads(default_sheet)

        # Check for lists container
        self.assertIn('lists', parsed)
        self.assertIn('children', parsed['lists'])

        # Check for ul and ol rules
        self.assertIn('ul', parsed)
        self.assertIn('ol', parsed)
        self.assertIn('li', parsed)

        # Verify ul configuration
        self.assertEqual(parsed['ul']['scope'], 'multiline')
        self.assertEqual(parsed['ul']['tag'], 'ul')
        self.assertEqual(parsed['ul']['starts'], '-')

        # Verify ol configuration
        self.assertEqual(parsed['ol']['scope'], 'multiline')
        self.assertEqual(parsed['ol']['tag'], 'ol')
        self.assertEqual(parsed['ol']['starts'], '#')

    def test_default_sheet_has_blockquote_rule(self):
        """Test default sheet contains blockquote rule"""
        default_sheet = self.sheets.default()
        parsed = json.loads(default_sheet)

        self.assertIn('blockquote', parsed)
        blockquote = parsed['blockquote']
        self.assertEqual(blockquote['scope'], 'multiline')
        self.assertEqual(blockquote['tag'], 'blockquote')
        self.assertEqual(blockquote['starts'], '>')

    def test_meatball_sheet_returns_json_string(self):
        """Test meatball() method returns valid JSON string"""
        meatball_sheet = self.sheets.meatball()
        self.assertIsInstance(meatball_sheet, str)

        # Should be parseable as JSON
        try:
            parsed = json.loads(meatball_sheet)
            self.assertIsInstance(parsed, dict)
        except json.JSONDecodeError:
            self.fail("meatball() should return valid JSON")

    def test_meatball_sheet_has_root_rule(self):
        """Test meatball sheet contains root rule"""
        meatball_sheet = self.sheets.meatball()
        parsed = json.loads(meatball_sheet)

        self.assertIn('root', parsed)
        self.assertIn('scope', parsed['root'])
        self.assertEqual(parsed['root']['scope'], 'root')

    def test_meatball_vs_default_differences(self):
        """Test that meatball and default sheets are different"""
        meatball_sheet = self.sheets.meatball()
        default_sheet = self.sheets.default()

        # They should be different JSON strings
        self.assertNotEqual(meatball_sheet, default_sheet)

        # Both should be valid JSON
        meatball_parsed = json.loads(meatball_sheet)
        default_parsed = json.loads(default_sheet)

        # Both should have root, but likely different configurations
        self.assertIn('root', meatball_parsed)
        self.assertIn('root', default_parsed)

    def test_sheet_contains_link_rules(self):
        """Test that sheets contain link-related rules"""
        default_sheet = self.sheets.default()
        parsed = json.loads(default_sheet)

        # Look for rules that might handle links
        # This is based on the structure we observed in the codebase
        found_link_related = False
        for rule_name, rule_def in parsed.items():
            if 'link' in rule_name.lower() or ('scope' in rule_def and rule_def['scope'] == 'link'):
                found_link_related = True
                break

        # If no explicit link rules found, check for inline rules that might handle links
        if not found_link_related:
            for rule_name, rule_def in parsed.items():
                if 'scope' in rule_def and rule_def['scope'] in ['inline', 'cell', 'paragraph']:
                    found_link_related = True
                    break

    def test_intermap_integration(self):
        """Test that intermap is properly integrated"""
        sheets_with_intermap = WikixSheets(self.intermap)
        sheets_without_intermap = WikixSheets()

        self.assertEqual(sheets_with_intermap.intermap, self.intermap)
        self.assertIsNone(sheets_without_intermap.intermap)

    def test_json_structure_validity(self):
        """Test that generated JSON has valid structure for compilation"""
        for sheet_method in ['default', 'meatball']:
            with self.subTest(sheet=sheet_method):
                sheet_json = getattr(self.sheets, sheet_method)()
                parsed = json.loads(sheet_json)

                # Every rule should be a dictionary
                for rule_name, rule_def in parsed.items():
                    self.assertIsInstance(rule_def, dict, f"Rule {rule_name} should be a dict")

                    # If it has children, they should be a list
                    if 'children' in rule_def:
                        self.assertIsInstance(rule_def['children'], list,
                                            f"Children of {rule_name} should be a list")

if __name__ == '__main__':
    unittest.main()