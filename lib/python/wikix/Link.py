import re
from .Inline import Inline
from .Patterns import Patterns
from .String import String

class Link(Inline):
  def __init__( self, name, definition ):
    super(Link, self).__init__( name, definition )
    self.tag = 'a'
    self.uri_encode_map = [True]  # Initialize with default

    # Strip trailing punctuation if and only if we are given a link pattern
    # and the URL is the last thing
    self.strip_trailing_punctuation = (
      (None != definition.get('link', {}).get('pattern')) and
      (isinstance( definition['link']['pattern'], str )) and
      re.match( r'url$', definition['link']['pattern'] )
    )
    
  def match( self, lines ):
    self.cache = super( Link, self ).match( lines )

    # If the 'text' part of a link is devoid of significant characters,
    # this is not a match. e.g. [[ ! ]] is not a match, but [[ a! ]] is.
    if self.cache:   
      captures = list(self.cache.groups())
      for i in range(0, len(captures)):
        if i<len(self.uri_encode_map) and self.uri_encode_map[i] and 0==len(String(captures[i]).canonicalize()):
          return
    
    return self.cache
  
  def inner_emit( self, lines, parent, context ):
    # Duplicate the match array because we are going to manipulate it in place
    captures = list(map( lambda c: c or '', list(self.cache.groups()) ))
    if not self.sheet.preserve_whitespace:
      captures = list(map( str.strip, captures ))
    
    trailing_punctuation = ''
    if self.strip_trailing_punctuation:
      regexp = re.compile(r'([^\w\/]?)\Z')
      def capture_trailing_punctuation(md):
        trailing_punctuation = md.group(0)
        return ""
      captures[-1] = re.sub( regexp, capture_trailing_punctuation, captures[-1] )

    uri_captures = []
    for i in range(0,len(captures)):
      uri_captures.append( captures[i] )
      if i < len(self.uri_encode_map) and self.uri_encode_map[i]:
        uri_captures[i] = re.sub( r'\.', '%2e', String(uri_captures[i]).from_xs().encode_uri() )

    href = text = before = after = ''
    if self.definition['link'].get('href'):   
      href = String(self.definition['link']['href']).format_with_array( uri_captures ).format_with_hash( context ).unescape_variable_interpolations().decode_uri()
    if self.definition['link'].get('text'):
      text = String(self.definition['link']['text']).format_with_array( captures ).format_with_hash( context ).unescape_variable_interpolations()
    if self.definition['link'].get('before'):
      before = String(self.definition['link']['before']).format_with_array( captures ).format_with_hash( context ).unescape_variable_interpolations()
    if self.definition['link'].get('after'):
      after = String(self.definition['link']['after']).format_with_array( captures ).format_with_hash( context ).unescape_variable_interpolations()
    
    klass = self.name
    if None != self.definition['link'].get('page_missing') and not context['page_exists']( href, context ):
      klass = klass + ' ' + self.definition['link']['page_missing']
    
    result = None
    if None != self.definition['link'].get('image') and re.match( Patterns.patterns['image'], href):
      alt = ''
      if '' != self.definition['link']['image']:
        alt = " alt='" + String(self.definition['link']['image']).format_with_array( captures ) + "'"
      result = "<img src='" + href + "' class='" + klass + "'" + alt + "/>"

    elif None != self.definition['link'].get('name'):
      result = "<a name='" + String(self.definition['link']['name']).format_with_array( captures ) + "'/>"
      
    else:
      result = "<a href='" + href + "' class='" + klass + "'>" + text + "</a>";
    return before + result + after + trailing_punctuation

  def compile_link_pattern( self, pattern ):
    pattern = re.sub( r'\\ \\ ', r'\\s+', pattern )
    pattern = re.sub( r'\\ ', r'\\s*', pattern )
    
    # If the start of the link pattern is the same character
    # then we need to ensure the match is tight with some regexp magic
    # TODO: What is going on here?
    # pattern =~ /^\s*([^\w\s]+)\s*/
    
    # Build a map of which captures match to URLs or texts so we know
    # which captures to URI encode
    self.uri_encode_map = [ True ]  # first map entry corresponds to $0
    def uri_encoder(md):
      if md.group(1) == 'url':
        self.uri_encode_map.append( False )
        return Patterns.patterns['url']

      elif md.group(1) == 'text':
        self.uri_encode_map.append( True )
        return r'(\S.*?)'

      elif md.group(1) == 'word':
        self.uri_encode_map.append( True )
        return r'(\S+)'

      elif md.group(1) == 'slug':
        self.uri_encode_map.append( False )
        return r'(\w+)'

    pattern = re.sub( r'(url|text|word|slug)', uri_encoder, pattern )
    return pattern
  
  def save_regexp( self, regexp ):
    pass

  def _transform_xhtml( self, node, transformer ):
    """Reverse transform: recover WikiX link syntax from an <a> element.

    Args:
        node: BeautifulSoup Tag (a or img)
        transformer: XhtmlToWikix instance
    Returns:
        (list_of_strings, cost) or None if this rule doesn't match
    """
    from bs4 import NavigableString

    tag_name = node.name.lower() if node.name else ''

    if tag_name == 'a':
      href = node.get('href', '')
      text = node.get_text()
    elif tag_name == 'img':
      href = node.get('src', '')
      text = node.get('alt', '')
    else:
      return None

    # The CSS class on the <a> element is the rule name that produced it.
    # Use it to prefer the correct rule (bijection key).
    css_classes = node.get('class', [])
    if isinstance(css_classes, str):
      css_classes = css_classes.split()
    # If the class matches this rule's name, set cost to 0 (highest priority).
    # If it matches a different rule's name, return None (let the correct rule handle it).
    rule_name_classes = [c for c in css_classes if c in transformer.sheet.rules]
    if rule_name_classes:
      # A rule name class is present - only match if it's this rule
      if self.name not in rule_name_classes:
        return None

    link_def = self.definition.get('link', {})
    href_pattern = link_def.get('href', '')
    text_pattern = link_def.get('text', '')
    link_pattern = link_def.get('pattern', '')

    # Skip anchor (name=) rules
    if link_def.get('name'):
      if tag_name == 'a' and node.get('name'):
        anchor_name = node.get('name', '')
        return ['[#' + anchor_name + ']'], len(anchor_name)
      return None

    # Try to match href pattern to reconstruct $1, $2, etc.
    substitutions = self._recover_substitutions(href, text, href_pattern, text_pattern)
    if substitutions is None:
      return None

    # Reconstruct WikiX syntax from pattern and substitutions
    result = self._reconstruct_wikix(link_pattern, substitutions)
    if result is None:
      return None

    cost = sum(len(s) for s in substitutions if s)
    cost += len(result) / max(len(str(node)), 1)
    return [result], cost

  def _recover_substitutions(self, href, text, href_pattern, text_pattern):
    """Try to recover substitution values from href and text using patterns.

    Returns:
        list of substitutions [None, $1, $2, ...] or None if no match
    """
    import re

    def pattern_to_regex(pattern):
      """Convert href/text pattern like '/wiki/$1' or 'http://x.org$1' to (regex, slot_map).

      Splits pattern on $N tokens, escapes literal parts, inserts capture groups.
      """
      if not pattern:
        return None, []

      slot_map = []
      parts = re.split(r'(\$\d+)', pattern)
      regex_parts = []
      for part in parts:
        m = re.match(r'\$(\d+)$', part)
        if m:
          slot_map.append(int(m.group(1)))
          regex_parts.append(r'(.+?)')
        else:
          # Escape literal part; handle @ context variables
          escaped = re.escape(part)
          escaped = re.sub(r'@\w+', r'[^/]+', escaped)
          regex_parts.append(escaped)

      return ''.join(regex_parts), slot_map

    href_regex, href_slots = pattern_to_regex(href_pattern)
    text_regex, text_slots = pattern_to_regex(text_pattern)

    subs = [None] * 5  # $0..$4

    if href_regex:
      m = re.fullmatch(href_regex, href)
      if not m:
        return None
      for i, slot in enumerate(href_slots):
        if slot < len(subs):
          subs[slot] = m.group(i + 1) if m.lastindex and i + 1 <= m.lastindex else ''

    if text_regex and text_pattern != '$0':
      m = re.fullmatch(text_regex, text)
      if m:
        for i, slot in enumerate(text_slots):
          if slot < len(subs):
            if subs[slot] is None:
              subs[slot] = m.group(i + 1) if m.lastindex and i + 1 <= m.lastindex else ''

    return subs

  def _reconstruct_wikix(self, pattern, substitutions):
    """Reconstruct WikiX link syntax from pattern and substitutions.

    Args:
        pattern: link pattern string like '[ url text ]' or 'url' or camelcase regexp
        substitutions: list [$0, $1, $2, ...]
    Returns:
        WikiX string or None
    """
    import re

    if not pattern:
      return None

    # Pattern may be a dict with 'regexp' key (for camelcase)
    if isinstance(pattern, dict):
      # For regexp-based patterns (camelcase), the text IS the WikiX
      if substitutions[1]:
        return substitutions[1]
      return None

    # Simple substitution: replace url/text/word/slug tokens
    result = pattern

    # Replace $N references in pattern reconstruction
    # We need to convert the link pattern to output
    # e.g. '[ url text ]' → '[ http://example.com My Text ]'
    # e.g. 'url' → 'http://example.com'

    counter = [0]
    def replace_token(md):
      counter[0] += 1
      idx = counter[0]
      return substitutions[idx] if idx < len(substitutions) and substitutions[idx] is not None else ''

    result = re.sub(r'(url|text|word|slug)', replace_token, pattern)

    # Clean up double spaces that occur when text == url
    result = re.sub(r'  +', ' ', result)

    return result