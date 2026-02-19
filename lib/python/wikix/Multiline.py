import re
from .Rule import Rule
from .String import String

class Multiline(Rule):
  def match( self, lines ):
    return re.search( self.regexp, lines[0] )
  
  def emit( self, lines, parent, context ):
    def match_lines(lines):
      body = []
      while len(lines) > 0:
        match_data = re.search( self.regexp, lines[0] )
        if not match_data:
          return body

        line = match_data.group(1)
        if self.must_preserve_whitespace() or self.sheet.preserve_whitespace > 0:       
          line = String(line).unchomp()
        
        if self.regexps.get('starts_delimited_by'):
          line = re.sub( '^' + self.regexps.get('starts_delimited_by'), '', line )
        
        body.append( line )
        lines.popleft()
      return body

    body = match_lines(lines)
    return [ self.start_tag() ] + self.transform_syntax( body, context ) + [ self.end_tag() ]

  def emit_syntax( self, inner ):
    """Prefix each line of inner content with this multiline's starts character."""
    inner_text = ''.join(inner)
    # Strip leading/trailing blank lines
    inner_text = re.sub(r'^\n+', '', inner_text)
    inner_text = re.sub(r'\n+$', '', inner_text)
    # Collapse multiple blank lines to single
    inner_text = re.sub(r'\n+', '\n', inner_text)

    starts = self.start_syntax()
    if self.regexps.get('starts_delimited_by'):
      # Each line is already prefixed by starts; add delimiter
      lines = inner_text.split('\n')
      prefixed = '\n'.join(starts + line for line in lines)
    else:
      lines = inner_text.split('\n')
      prefixed = '\n'.join(starts + ' ' + line for line in lines)

    return [prefixed, '\n']