import re
from Inline import Inline
from Patterns import Patterns
from String import String

class Link(Inline):
  def __init__( self, name, definition ):
    super(Link, self).__init__( name, definition )
    self.tag = 'a'
    
    # Strip trailing punctuation if and only if we are given a link pattern
    # and the URL is the last thing      
    self.strip_trailing_punctuation = (
      (None != definition['link']['pattern']) and
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
    captures = map( lambda c: c or '', list(self.cache.groups()) )
    if not self.sheet.preserve_whitespace:
      captures = map( str.strip, captures )
    
    trailing_punctuation = ''
    if self.strip_trailing_punctuation:
      regexp = re.compile(r'([^\w\/]?)\z')
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
    pattern = re.sub( r'\\ \\ ', '\\s+', pattern )
    pattern = re.sub( r'\\ ', '\\s*', pattern )
    
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