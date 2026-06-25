#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'python'))

import unittest
import re
from wikix.Link import Link
from wikix.String import String

# Mock classes for testing
class MockSheet:
    def __init__(self):
        self.preserve_whitespace = False

class MockMatch:
    def __init__(self, groups):
        self._groups = groups

    def groups(self):
        return self._groups

class TestLink(unittest.TestCase):
    def setUp(self):
        self.basic_link_definition = {
            'link': {
                'pattern': 'url',
                'href': '{0}',
                'text': '{0}'
            }
        }

    def test_link_initialization_basic(self):
        """Test Link initialization with basic configuration"""
        link = Link('test_link', self.basic_link_definition)

        self.assertEqual(link.name, 'test_link')
        self.assertEqual(link.tag, 'a')
        self.assertTrue(link.strip_trailing_punctuation)

    def test_link_initialization_non_url_pattern(self):
        """Test Link initialization with non-URL pattern"""
        definition = {
            'link': {
                'pattern': 'text',
                'href': '{0}',
                'text': '{0}'
            }
        }

        link = Link('text_link', definition)
        self.assertFalse(link.strip_trailing_punctuation)

    def test_link_initialization_dict_pattern(self):
        """Test Link initialization with dictionary pattern"""
        definition = {
            'link': {
                'pattern': {'regexp': r'\d+'},
                'href': '{0}',
                'text': '{0}'
            }
        }

        link = Link('dict_link', definition)
        self.assertFalse(link.strip_trailing_punctuation)

    def test_compile_link_pattern_url(self):
        """Test compile_link_pattern with URL pattern"""
        link = Link('url_link', self.basic_link_definition)

        pattern = "url text"
        result = link.compile_link_pattern(pattern)

        self.assertIsInstance(result, str)
        self.assertIn('http', result)  # Should contain URL pattern

    def test_compile_link_pattern_text(self):
        """Test compile_link_pattern with text pattern"""
        link = Link('text_link', self.basic_link_definition)

        pattern = "text"
        result = link.compile_link_pattern(pattern)

        self.assertIn(r'(\S.*?)', result)  # Should contain text capture pattern

    def test_compile_link_pattern_word(self):
        """Test compile_link_pattern with word pattern"""
        link = Link('word_link', self.basic_link_definition)

        pattern = "word"
        result = link.compile_link_pattern(pattern)

        self.assertIn(r'(\S+)', result)  # Should contain word capture pattern

    def test_compile_link_pattern_slug(self):
        """Test compile_link_pattern with slug pattern"""
        link = Link('slug_link', self.basic_link_definition)

        pattern = "slug"
        result = link.compile_link_pattern(pattern)

        self.assertIn(r'(\w+)', result)  # Should contain slug capture pattern

    def test_compile_link_pattern_mixed(self):
        """Test compile_link_pattern with mixed patterns"""
        link = Link('mixed_link', self.basic_link_definition)

        pattern = "[url text]"
        result = link.compile_link_pattern(pattern)

        self.assertIn('http', result)  # Should contain URL pattern
        self.assertIn(r'(\S.*?)', result)  # Should contain text pattern

    def test_compile_link_pattern_spaces(self):
        """Test compile_link_pattern handles spaces correctly"""
        link = Link('space_link', self.basic_link_definition)

        pattern = "text\\ text"  # Escaped space
        result = link.compile_link_pattern(pattern)

        self.assertIn(r'\s*', result)  # Should handle escaped spaces

    def test_uri_encode_map_initialization(self):
        """Test that uri_encode_map is properly initialized"""
        link = Link('encode_link', self.basic_link_definition)

        pattern = "url text word slug"
        link.compile_link_pattern(pattern)

        # Should have entries for each pattern plus the initial True
        self.assertGreater(len(link.uri_encode_map), 1)
        self.assertTrue(link.uri_encode_map[0])  # First entry should be True

    def test_uri_encode_map_url_entries(self):
        """Test uri_encode_map correctly marks URL entries"""
        link = Link('url_map_link', self.basic_link_definition)

        pattern = "url"
        link.compile_link_pattern(pattern)

        # URL entries should be marked as False (don't URI encode)
        self.assertEqual(len(link.uri_encode_map), 2)  # Initial + 1 pattern
        self.assertFalse(link.uri_encode_map[1])

    def test_uri_encode_map_text_entries(self):
        """Test uri_encode_map correctly marks text entries"""
        link = Link('text_map_link', self.basic_link_definition)

        pattern = "text"
        link.compile_link_pattern(pattern)

        # Text entries should be marked as True (do URI encode)
        self.assertEqual(len(link.uri_encode_map), 2)
        self.assertTrue(link.uri_encode_map[1])

    def test_save_regexp_method(self):
        """Test save_regexp method exists and can be called"""
        link = Link('save_link', self.basic_link_definition)

        # Should not raise an exception
        link.save_regexp("test_pattern")

    def test_match_method_with_empty_cache(self):
        """Test match method when parent class returns None"""
        link = Link('match_link', self.basic_link_definition)

        # Mock the parent match method to return None
        original_match = Link.__bases__[0].match
        Link.__bases__[0].match = lambda self, lines: None

        try:
            result = link.match(["test line"])
            self.assertIsNone(result)
        finally:
            # Restore original method
            Link.__bases__[0].match = original_match

    def test_definition_access(self):
        """Test that link definition is accessible"""
        definition = {
            'link': {
                'pattern': 'url',
                'href': 'http://example.com/{0}',
                'text': 'Link to {0}',
                'before': 'Before:',
                'after': ':After'
            }
        }

        link = Link('def_link', definition)
        self.assertEqual(link.definition, definition)

    def test_link_with_page_missing_class(self):
        """Test link definition with page_missing class"""
        definition = {
            'link': {
                'pattern': 'text',
                'href': '{0}',
                'text': '{0}',
                'page_missing': 'missing'
            }
        }

        link = Link('missing_link', definition)
        self.assertIn('page_missing', link.definition['link'])
        self.assertEqual(link.definition['link']['page_missing'], 'missing')

    def test_link_with_image_configuration(self):
        """Test link definition with image configuration"""
        definition = {
            'link': {
                'pattern': 'url',
                'href': '{0}',
                'text': '{0}',
                'image': 'alt text'
            }
        }

        link = Link('image_link', definition)
        self.assertIn('image', link.definition['link'])

    def test_link_with_name_anchor(self):
        """Test link definition with name anchor"""
        definition = {
            'link': {
                'pattern': 'text',
                'name': '{0}'
            }
        }

        link = Link('anchor_link', definition)
        self.assertIn('name', link.definition['link'])

if __name__ == '__main__':
    unittest.main()