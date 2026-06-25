#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'python'))

import unittest
from wikix import Wikix
from wikix.WikixSheets import WikixSheets
from wikix.Intermap import Intermap

class TestWikix(unittest.TestCase):
    def setUp(self):
        self.intermap = Intermap()
        self.sheets = WikixSheets(self.intermap)

        def get_page_id(href):
            import re
            md = re.search(r'^/wiki/(\S+?)(#.*)?$', href)
            if md:
                return md.group(1)
            return None

        def does_page_exist(page_id):
            return page_id == 'TextFormattingRules'

        self.meatball = Wikix(self.sheets.meatball(), get_page_id, does_page_exist)
        self.bibwiki = Wikix(self.sheets.default(), get_page_id, does_page_exist)

    def test_wikix_initialization(self):
        """Test Wikix class initializes properly"""
        self.assertIsNotNone(self.meatball)
        self.assertIsNotNone(self.meatball.sheet)
        self.assertIsNotNone(self.meatball.get_page_id)
        self.assertIsNotNone(self.meatball.does_page_exist)

    def test_transform_syntax_basic(self):
        """Test basic text transformation"""
        result = self.meatball.transform_syntax("Hello World")
        self.assertIn("Hello World", result)

    def test_wiki_links(self):
        """Test WikiName linking"""
        result = self.meatball.transform_syntax("TextFormattingRules")
        self.assertIn('<a', result)
        self.assertIn('TextFormattingRules', result)

    def test_undefined_page_links(self):
        """Test undefined page linking shows question mark"""
        result = self.meatball.transform_syntax("SampleUndefinedPage")
        self.assertIn('?', result)
        self.assertIn('SampleUndefinedPage', result)

    def test_wiki_links_with_anchors(self):
        """Test WikiName links with anchor fragments"""
        result = self.meatball.transform_syntax("TextFormattingRules#anchor")
        self.assertIn('<a', result)
        self.assertIn('#anchor', result)

    def test_url_links(self):
        """Test automatic URL linking"""
        url = "http://www.usemod.com/cgi-bin/mb.pl?TextFormattingRules#anchor"
        result = self.meatball.transform_syntax(url)
        self.assertIn('<a', result)
        self.assertIn('href=', result)
        self.assertIn(url, result)

    def test_bracketed_links(self):
        """Test bracketed link syntax"""
        link_text = "[http://www.usemod.com/cgi-bin/mb.pl?TextFormattingRules#anchor anchor]"
        result = self.meatball.transform_syntax(link_text)
        self.assertIn('<a', result)
        self.assertIn('anchor', result)

    def test_interwiki_links(self):
        """Test InterWiki link syntax"""
        result = self.meatball.transform_syntax("[UseMod:TextFormattingRules text formatting rules]")
        self.assertIn('<a', result)
        self.assertIn('text formatting rules', result)

    def test_bold_text(self):
        """Test bold text formatting"""
        result = self.meatball.transform_syntax("<b>bold</b>")
        self.assertIn('<b>bold</b>', result)

    def test_italic_text(self):
        """Test italic text formatting"""
        result = self.meatball.transform_syntax("<i>italic</i>")
        self.assertIn('<i>italic</i>', result)

    def test_html_entities(self):
        """Test HTML entity handling"""
        result = self.meatball.transform_syntax("&lt;")
        self.assertIn('&lt;', result)

    def test_preformatted_text(self):
        """Test preformatted text blocks"""
        pre_text = "<pre>\nSample <b>bold</b>, <i>italic</i>, and <b><i>bold+italic</i></b>.\n</pre>"
        result = self.meatball.transform_syntax(pre_text)
        self.assertIn('<pre>', result)

    def test_mixed_formatting(self):
        """Test mixed bold and italic formatting"""
        text = "Sample <b>bold</b>, <i>italic</i>, and <b><i>bold+italic</i></b>."
        result = self.meatball.transform_syntax(text)
        self.assertIn('<b>bold</b>', result)
        self.assertIn('<i>italic</i>', result)
        self.assertIn('<b><i>bold+italic</i></b>', result)

    def test_anchor_references(self):
        """Test anchor reference syntax"""
        result = self.meatball.transform_syntax("[#N888_7_2_1]")
        self.assertIn('N888_7_2_1', result)

    def test_image_links(self):
        """Test automatic image linking"""
        result = self.meatball.transform_syntax("http://usemod.com/wiki.gif")
        self.assertIn('<img', result)
        self.assertIn('wiki.gif', result)

    def test_isbn_links(self):
        """Test ISBN linking"""
        result = self.meatball.transform_syntax("ISBN 0-471-25311-1")
        self.assertIn('ISBN', result)
        self.assertIn('0-471-25311-1', result)

    def test_starting_spaces_preformat(self):
        """Test starting spaces for preformatted text"""
        text = """   This is the starting-spaces version of
   preformatted text.  Note that links like
   UseModWiki still work and '''bolding''' works."""
        result = self.meatball.transform_syntax(text)
        self.assertIn('preformatted', result)

    def test_page_exists_callback(self):
        """Test page exists callback functionality"""
        self.assertTrue(self.meatball.does_page_exist('TextFormattingRules'))
        self.assertFalse(self.meatball.does_page_exist('NonExistentPage'))

    def test_get_page_id_callback(self):
        """Test get page ID callback functionality"""
        page_id = self.meatball.get_page_id('/wiki/TextFormattingRules')
        self.assertEqual(page_id, 'TextFormattingRules')

        page_id_with_anchor = self.meatball.get_page_id('/wiki/TextFormattingRules#anchor')
        self.assertEqual(page_id_with_anchor, 'TextFormattingRules')

    def test_link_collector(self):
        """Test link collection during transformation"""
        link_collector = {}
        result = self.meatball.transform_syntax("TextFormattingRules", link_collector)
        self.assertIn('TextFormattingRules', link_collector)

    def test_transform_xhtml(self):
        """Test XHTML transformation method exists"""
        self.assertTrue(hasattr(self.meatball, 'transform_xhtml'))

    def test_complex_markup_example(self):
        """Test complex markup from the example file"""
        complex_text = """
===== Translations =====
* TextFormattingRulesSpanish : Spanish / espanol
* ReglesDeMiseEnPageDesTextes : LangueFrancaise
-----
Simple editing is one of the major benefits of using a wiki.
"""
        result = self.meatball.transform_syntax(complex_text)
        self.assertIsNotNone(result)
        self.assertIn('Translations', result)

if __name__ == '__main__':
    unittest.main()