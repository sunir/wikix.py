import re
try:
    # Python 2
    import urllib
    urllib_quote_func = urllib.quote
    urllib_unquote_func = urllib.unquote
except AttributeError:
    # Python 3
    import urllib.parse
    urllib_quote_func = urllib.parse.quote
    urllib_unquote_func = urllib.parse.unquote

class String(str):
  # TODO: test save_spaces^M
  def canonicalize( self, save_spaces = False ):
    result = String(self)
    result = result.lower()
    result = re.sub(r'\&\w+;', '', result)
    result = re.sub(r'&#\d+;', '', result)
    result = re.sub(r'_', '', result)
    if save_spaces:
      result = re.sub( r'\s+', '_', result ) 
    result = re.sub( r'\W+', '', result )
    if save_spaces:
      result = String(re.sub( r'_', ' ', result )).squeeze_spaces()
    return String(result)

  def escape_punctuation(self):
    return String(re.sub( r'([^\w\d\s])', r'\\\1', self ))

  def unescape_punctuation(self):
    return String(re.sub( r'\\(\\?)', r'\1', self ))

  # The only regexp command in Wikix patterns is +, so we'll re-unescape it after escaping
  def escape_regexp(self):
    return String(re.sub( r'\\\+', '+', re.escape(self)))

  def escape_variable_interpolations(self):
    return String(re.sub( r'([\$\@])', r'\1\\', self ))

  def unescape_variable_interpolations(self):
    return String(re.sub( r'([\$\@])\\', r'\1', self ))

  def encode_uri(self):
    return String(urllib_quote_func(self.encode('utf-8')))
    # return re.sub( r'([^a-zA-Z0-9\!\@\$\*\(\)\-\_\,\.])', lambda md: sprintf( "%%%02x", md.group(0) ), self )

  # TODO: I'm not sure this is all that safe. What about UTF8 attacks?
  def decode_uri(self):
    return String(urllib_unquote_func(self))

  # Existing to_xs does not escape quotes (') or doublequotes (")
  def to_xs(self):
    # First, escape & only if it's not already the start of an HTML entity
    text = re.sub(r'&(?!(?:\w+;|#\d+;))', '&amp;', self)
    # Then escape the other characters
    html_escape_table = {
      '"': "&quot;",
      "'": "&#039;",
      ">": "&gt;",
      "<": "&lt;",
    }
    return String( ''.join(map(lambda c: html_escape_table.get(c,c), text)) )

  def from_xs(self):
    return String(self.replace( r'&apos;', "'" ).replace( '&#039;', "'" ).replace( r'&quot;', '"' ).replace( '&gt;', '>' ).replace( '&lt;', '<' ).replace( '&amp;', '&'))

  def format_with_array( self, array ):
    def safe_substitute(match):
      index = int(match.group(1)) - 1
      if 0 <= index < len(array):
        return String(array[index]).escape_variable_interpolations()
      else:
        return ''
    return String(re.sub(r'\$(\d+)', safe_substitute, self ))

  def format_with_hash( self, hash ):
    return String(re.sub(r'\@(\d+)', lambda md: String(hash[md.group(1)]).escape_variable_interpolations() or '', self ))
  
  def minimal_regexp( self ):
    return String(re.sub( r'(.)[+]', r'\1', self ))

  def unchomp( self ):
    return String(self + "\n" if not self or self[-1] != "\n" else self)

  def squeeze_spaces( self ):
    return String(re.sub( r'\s+', ' ', self.strip() ))
