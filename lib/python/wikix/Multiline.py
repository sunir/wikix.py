import re
from Rule import Rule
from String import String

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