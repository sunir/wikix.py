from Rule import Rule

class Line(Rule):
  def match( self, lines ):
    self.cache = self.regexp.search( lines[0] )
    return self.cache
  
  def emit( self, lines, parent, context ):
    lines.popleft()
    return (
    	[self.start_tag()] + 
    	self.transform_syntax([self.cache.group(1) if self.cache.lastindex else ''], context) + 
    	[self.end_tag()]
    )