import re
from Rule import Rule
from unique import unique

class Cell(Rule):
  def __init__( self, name, definition ):
    super(Cell, self).__init__( name, definition )
    self.block_children = None
    self.cache = None

  def match( self, lines ):
    if not self.block_children:
      self.block_children = re.compile( 
        '^(' + 
          '|'.join( 
            unique(
              map(
                lambda rule: rule.regexp.pattern,
                filter( 
                  lambda rule: not rule.is_inline(), 
                  self.children 
                )
              )
            )
          ) +
        ')',
        re.MULTILINE
      )
    
    if 0 == len(lines):
      return

    self.cache = [ lines.popleft() ]
    while len(lines) > 0 and self.block_children.search( lines[0] ):        
      self.cache.append(lines.popleft())

    return self.cache
  
  def emit( self, ines, parent, context ):
    cdata = ''
    if not self.block_children.match( self.cache[0] ):
      cdata = self.cache[0]
      self.cache = self.cache[1:]
    return( 
      [self.start_tag()] + 
      self.transform_syntax([cdata], context) + 
      self.transform_syntax(self.cache, context) + 
      [self.end_tag()]
    )