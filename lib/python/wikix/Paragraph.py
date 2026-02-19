import re
from .Rule import Rule

class Paragraph(Rule):
  # Paragraphs always match
  def match( self, lines ):
    return re.search( self.regexp, lines[0] )
  
  def emit( self, lines, parent, context ):
    # Grab everything until the next blank line
    body = []      
    while len(lines) > 0 and re.search(r'\S', lines[0] ) and self == parent.next_matching_child(lines):
      body.append( lines.popleft() )

    join_character = ' '
    if self.sheet.preserve_whitespace > 0 or self.must_preserve_whitespace():
      join_character = ''

    return [self.start_tag()] + self.transform_syntax([join_character.join(body)], context) + [self.end_tag()]
  
  # Paragraphs always match
  def set_regexp( self, *regexps ):
    self.regexp = re.compile(r'')

  def emit_syntax( self, inner ):
    """Paragraph: plain content + blank line (double newline).

    WikiX separates paragraphs with a blank line (\n\n).
    A single \n is not enough — the parser joins lines within
    the same paragraph.
    """
    result = ''.join(inner).strip()
    return [result, '\n\n']