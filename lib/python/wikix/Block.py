import re
from Rule import Rule
from String import String

# TODO: Why is Block.cache an array instead of match_data?
class Block(Rule):
  def __init__( self, name, definition ):
    super(Block, self).__init__( name, definition )
    self.starts_regexp = None

  def match( self, lines ):
    if not self.starts_regexp:
      self.starts_regexp = re.compile('^' + self.regexps['starts'] + '$')
      self.ends_regexp = re.compile('^' + self.regexps['ends'] + '$')
    self.cache = []
    if self.starts_regexp.search(lines[0]):
      for line in list(lines)[1:]:
        if self.ends_regexp.search(line):
          return self.cache
        self.cache.append( line )
    self.cache = None
    return
  
  def emit( self, lines, parent, context ):
    for i in range(0,len(self.cache)+2):
      lines.popleft()
    
    if self.must_preserve_whitespace() or self.sheet.preserve_whitespace > 0:   
      self.cache = map( lambda s: String(s).unchomp(), self.cache )

    return [self.start_tag() + "\n"] + self.transform_syntax(self.cache, context) + [self.end_tag()]