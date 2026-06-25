#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'python'))

import unittest
from wikix.String import String

class TestString(unittest.TestCase):
    def test_string_inherits_from_str(self):
        """Test that String class inherits from str"""
        s = String("test")
        self.assertIsInstance(s, str)
        self.assertEqual(s, "test")

    def test_canonicalize_basic(self):
        """Test basic canonicalize functionality"""
        s = String("Hello World!")
        result = s.canonicalize()

        # Should be lowercase and remove non-word characters
        self.assertEqual(result, "helloworld")

    def test_canonicalize_with_html_entities(self):
        """Test canonicalize removes HTML entities"""
        s = String("Hello &amp; World &#123;!")
        result = s.canonicalize()

        # Should remove HTML entities and non-word chars, but leave some numbers
        self.assertIn("helloworld", result)

    def test_canonicalize_with_underscores(self):
        """Test canonicalize removes underscores"""
        s = String("hello_world_test")
        result = s.canonicalize()

        self.assertEqual(result, "helloworldtest")

    def test_canonicalize_with_save_spaces(self):
        """Test canonicalize with save_spaces=True"""
        s = String("Hello   World  Test")
        result = s.canonicalize(save_spaces=True)

        # Should preserve spaces as single spaces
        self.assertIn(" ", result)

    def test_escape_punctuation(self):
        """Test escape_punctuation method"""
        s = String("Hello! How are you? (Fine)")
        result = s.escape_punctuation()

        # Should escape punctuation with backslashes
        self.assertIn(r'\!', result)
        self.assertIn(r'\?', result)
        self.assertIn(r'\(', result)
        self.assertIn(r'\)', result)

    def test_unescape_punctuation(self):
        """Test unescape_punctuation method"""
        s = String(r"Hello\! How are you\?")
        result = s.unescape_punctuation()

        # Should remove backslashes before punctuation
        self.assertEqual(result, "Hello! How are you?")

    def test_escape_regexp(self):
        """Test escape_regexp method"""
        s = String("test+pattern")
        result = s.escape_regexp()

        # Should keep + unescaped but escape other regexp chars
        self.assertIn("+", result)

    def test_escape_variable_interpolations(self):
        """Test escape_variable_interpolations method"""
        s = String("$var @var")
        result = s.escape_variable_interpolations()

        # Should escape $ and @ with backslashes
        self.assertEqual(result, "$\\var @\\var")

    def test_unescape_variable_interpolations(self):
        """Test unescape_variable_interpolations method"""
        s = String("$\\var @\\var")
        result = s.unescape_variable_interpolations()

        # Should remove backslashes after $ and @
        self.assertEqual(result, "$var @var")

    def test_encode_uri(self):
        """Test encode_uri method"""
        s = String("hello world")
        result = s.encode_uri()

        # Should URL encode spaces and special characters
        self.assertIn("%20", result)  # Space should be encoded

    def test_decode_uri(self):
        """Test decode_uri method"""
        s = String("hello%20world")
        result = s.decode_uri()

        # Should decode URL encoded characters
        self.assertEqual(result, "hello world")

    def test_encode_decode_uri_roundtrip(self):
        """Test URI encoding/decoding roundtrip"""
        original = "Hello World! #test"
        s = String(original)
        encoded = s.encode_uri()
        decoded = String(encoded).decode_uri()

        self.assertEqual(decoded, original)

    def test_to_xs_html_escaping(self):
        """Test to_xs HTML escaping"""
        s = String('<script>alert("test");</script>')
        result = s.to_xs()

        # Should escape HTML characters
        self.assertIn("&lt;", result)
        self.assertIn("&gt;", result)
        self.assertIn("&quot;", result)

    def test_to_xs_all_entities(self):
        """Test to_xs escapes all required entities"""
        s = String('&<>"\'')
        result = s.to_xs()

        expected_entities = ["&amp;", "&lt;", "&gt;", "&quot;", "&#039;"]
        for entity in expected_entities:
            self.assertIn(entity, result)

    def test_from_xs_html_unescaping(self):
        """Test from_xs HTML unescaping"""
        s = String('&lt;script&gt;alert(&quot;test&quot;);&lt;/script&gt;')
        result = s.from_xs()

        # Should unescape HTML entities
        self.assertEqual(result, '<script>alert("test");</script>')

    def test_to_xs_from_xs_roundtrip(self):
        """Test HTML escaping/unescaping roundtrip"""
        original = '<div class="test">Hello & "World"</div>'
        s = String(original)
        escaped = s.to_xs()
        unescaped = String(escaped).from_xs()

        self.assertEqual(unescaped, original)

    def test_format_with_array(self):
        """Test format_with_array method"""
        s = String("Hello $1, welcome to $2!")
        array = ["John", "Wikix"]
        result = s.format_with_array(array)

        self.assertEqual(result, "Hello John, welcome to Wikix!")

    def test_format_with_array_empty_substitution(self):
        """Test format_with_array with missing array elements"""
        s = String("Hello $1, $2, $3")
        array = ["John"]  # Missing elements
        result = s.format_with_array(array)

        # Should handle missing array elements gracefully
        self.assertIn("John", result)

    def test_format_with_hash(self):
        """Test format_with_hash method"""
        s = String("Page exists: @1")
        hash_dict = {"1": "true"}
        result = s.format_with_hash(hash_dict)

        self.assertEqual(result, "Page exists: true")

    def test_minimal_regexp(self):
        """Test minimal_regexp method"""
        s = String("test+ pattern+ more+")
        result = s.minimal_regexp()

        # Should remove + after characters
        self.assertNotIn("+", result)
        self.assertIn("test", result)
        self.assertIn("pattern", result)
        self.assertIn("more", result)

    def test_unchomp_adds_newline(self):
        """Test unchomp adds newline when missing"""
        s = String("Hello World")
        result = s.unchomp()

        self.assertEqual(result, "Hello World\n")

    def test_unchomp_preserves_existing_newline(self):
        """Test unchomp preserves existing newline"""
        s = String("Hello World\n")
        result = s.unchomp()

        self.assertEqual(result, "Hello World\n")

    def test_squeeze_spaces(self):
        """Test squeeze_spaces method"""
        s = String("  Hello    World   Test  ")
        result = s.squeeze_spaces()

        # Should collapse multiple spaces to single spaces and trim
        self.assertEqual(result, "Hello World Test")

    def test_squeeze_spaces_tabs_and_newlines(self):
        """Test squeeze_spaces handles tabs and newlines"""
        s = String("Hello\t\tWorld\n\nTest")
        result = s.squeeze_spaces()

        # Should collapse all whitespace to single spaces
        self.assertEqual(result, "Hello World Test")

    def test_string_returns_string_instances(self):
        """Test that String methods return String instances"""
        s = String("test")

        # Test various methods return String instances
        methods_to_test = [
            ('canonicalize', []),
            ('escape_punctuation', []),
            ('unescape_punctuation', []),
            ('escape_regexp', []),
            ('to_xs', []),
            ('from_xs', []),
            ('squeeze_spaces', []),
            ('unchomp', []),
        ]

        for method_name, args in methods_to_test:
            with self.subTest(method=method_name):
                result = getattr(s, method_name)(*args)
                self.assertIsInstance(result, String)

    def test_complex_string_processing(self):
        """Test complex string processing workflow"""
        original = "Hello & <World>! How are you?"
        s = String(original)

        # Chain multiple operations
        result = (s.to_xs()
                  .squeeze_spaces()
                  .escape_punctuation()
                  .unescape_punctuation()
                  .from_xs())

        # Should survive the processing chain
        self.assertIsInstance(result, String)

if __name__ == '__main__':
    unittest.main()