"""XHTML → WikiX reverse transform.

Python port of the Ruby xhtml_to_wikix.rb implementation.
Uses BeautifulSoup instead of Nokogiri.

The transform is designed to be bijective when combined with the forward
WikiX → XHTML transform. Precedence: tokens > blocks > inlines.
"""

import re
from bs4 import BeautifulSoup, NavigableString, Tag


class XhtmlToWikix:
    """Transforms XHTML (xhtmlbasic subset) back to WikiX markup."""

    def __init__(self, sheet):
        """
        Args:
            sheet: Compiled WikiX Sheet object (from Compiler)
        """
        self.sheet = sheet

    def transform(self, xhtml: str) -> str:
        """Transform XHTML string to WikiX markup.

        Args:
            xhtml: XHTML string (fragment or full document)

        Returns:
            WikiX markup string
        """
        xhtml = xhtml.replace('\r\n', '\n').replace('\r', '\n')

        soup = BeautifulSoup(xhtml, 'html.parser')

        # If there's a body element, use it; otherwise use the document root
        body = soup.find('body')
        if body:
            node = body
        else:
            node = soup

        parts, _ = self._transform_node(node, self.sheet.root)
        result = ''.join(parts)
        # Normalize trailing newlines
        result = re.sub(r'\n+$', '', result)
        return result

    def _transform_node(self, node, rule):
        """Transform a DOM node using the given rule.

        Returns:
            (list_of_strings, cost)
        """
        inner, cost = self._transform_children(node, rule)
        emitted = rule.emit_syntax(inner)
        return emitted, cost

    def _transform_children(self, node, rule):
        """Transform all children of a node.

        Returns:
            (list_of_strings, total_cost)
        """
        result = []
        total_cost = 0

        for child in node.children:
            parts, cost = self._transform_child(child, rule)
            result.extend(parts)
            total_cost += cost

        return result, total_cost

    def _transform_child(self, child, parent_rule):
        """Transform a single child node.

        Tries all matching rules; picks lowest cost.
        Falls back to flattening (extracting text) if no rule matches.

        Returns:
            (list_of_strings, cost)
        """
        if isinstance(child, NavigableString):
            # Text node: escape any inline syntax characters
            text = str(child)
            escaped = self.sheet.escape_inline_syntax(text)
            return [escaped], 0

        if not isinstance(child, Tag):
            return [], 0

        tag_name = child.name.lower() if child.name else ''

        # Find matching rules for this tag
        matching_rules = self._find_children_by_tag(parent_rule, tag_name)

        transformations = []
        for rule in matching_rules:
            result = self._try_transform(child, rule)
            if result is not None:
                parts, cost = result
                transformations.append((parts, cost, rule))

        if not transformations:
            # No rule matched: flatten to text (cost += 1 per flattened node)
            parts, cost = self._transform_children(child, parent_rule)
            return parts, cost + 1

        # Pick lowest cost
        transformations.sort(key=lambda x: x[1])
        best_parts, best_cost, _ = transformations[0]
        return best_parts, best_cost

    def _try_transform(self, node, rule):
        """Try to transform a node with a specific rule.

        Returns:
            (list_of_strings, cost) or None if rule doesn't apply
        """
        # Check if rule handles this tag
        if not self._rule_handles_tag(rule, node.name):
            return None

        # Delegate to rule-specific transform
        transform_fn = getattr(rule, '_transform_xhtml', None)
        if transform_fn:
            return transform_fn(node, self)

        # Default: transform children recursively, wrap with rule's syntax
        parts, cost = self._transform_children(node, rule)
        emitted = rule.emit_syntax(parts)
        return emitted, cost

    def _rule_handles_tag(self, rule, tag_name):
        """Check if a rule handles the given HTML tag."""
        tag_name = (tag_name or '').lower()

        # Rules without a tag handle their children's tags (grouping rules)
        if rule.tag is None:
            return False

        return rule.tag.lower() == tag_name

    def _find_children_by_tag(self, rule, tag_name):
        """Find all descendant rules that handle the given tag."""
        result = []
        for child in rule.children:
            # Skip rules that only transform to syntax (direction='xhtml' means xhtml-only output)
            if child.definition.get('direction') == 'xhtml':
                continue

            if child.tag is None:
                # Grouping rule: check its children
                result.extend(self._find_children_by_tag(child, tag_name))
            elif self._rule_handles_tag(child, tag_name):
                result.append(child)

        return result


def install_transform_xhtml(sheet, transformer: XhtmlToWikix):
    """Install transform_xhtml method on sheet and rules.

    This monkey-patches the sheet to add reverse transform capability.
    Called after compiling the sheet.
    """
    sheet._xhtml_transformer = transformer


