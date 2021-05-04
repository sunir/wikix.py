import re
import urllib

class String(str):
  # TODO: test save_spaces^M
  def canonicalize( self, save_spaces = False ):
    result = self
    result = result.lower()
    result = re.sub(r'\&\w+;', '', result)
    result = re.sub(r'/\&#\d+;', '', result)
    result = re.sub(r'_', '', result)
    if save_spaces:
      result = re.sub( r'\s+', '_', result ) 
    result = re.sub( r'\W+', '', result )
    if save_spaces:
      result = String(result.sub( r'_', ' ' )).squeeze_spaces()
    return result

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
    return String(urllib.quote(self.encode('utf-8')))
    # return re.sub( r'([^a-zA-Z0-9\!\@\$\*\(\)\-\_\,\.])', lambda md: sprintf( "%%%02x", md.group(0) ), self )

  # TODO: I'm not sure this is all that safe. What about UTF8 attacks?
  def decode_uri(self):
    return String(urllib.unquote(self).decode('utf-8'))

  # Existing to_xs does not escape quotes (') or doublequotes (")
  def to_xs(self):
    html_escape_table = {
      "&": "&amp;",
      '"': "&quot;",
      "'": "&#039;",
      ">": "&gt;",
      "<": "&lt;",
    }
    return String( ''.join(map(lambda c: html_escape_table.get(c,c), self)) )

  def from_xs(self):
    return String(self.replace( r'&apos;', "'" ).replace( '&#039;', "'" ).replace( r'&quot;', '"' ).replace( '&gt;', '>' ).replace( '&lt;', '<' ).replace( '&amp;', '&'))

  def format_with_array( self, array ):
    return String(re.sub(r'\$(\d+)', lambda md: String(array[int(md.group(1))-1]).escape_variable_interpolations() or '', self ))

  def format_with_hash( self, hash ):
    return String(re.sub(r'\@(\d+)', lambda md: String(hash[md.group(1)]).escape_variable_interpolations() or '', self ))
  
  def minimal_regexp( self ):
    return String(re.sub( r'(.)\+', '\1', self ))

  def unchomp( self ):
    return String(self + "\n" if self[-1] != "\n" else self)

  def squeeze_spaces( self ):
    return String(re.sub( r'\s+', ' ', self.strip() ))
