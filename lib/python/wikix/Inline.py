import re
from Rule import Rule
from String import String

class Inline(Rule):
  def is_inline(self):
    return True

  def match( self, lines ):
    self.cache = self.regexp.search(lines[0])
    return self.cache
  
  # Contract: Inline does not consume the line, but merely transforms it into the
  # storage, so other inline elements can continue to consume the line. 
  def emit( self, lines, parent, context ):
    pre_match = lines[0][0:self.cache.start()]
    post_match = lines[0][self.cache.end():]
    
    xhtml = self.inner_emit( lines, parent, context )      
    result = [pre_match, self.store(context, xhtml), post_match]
    
    # An exception to the contract! Prevent looping by actually consuming the front part of the line. 
    if len(pre_match) == 0:        
      lines[0] = post_match
      result.pop()
      return result

    lines[0] = ''.join(result)
    return []
  
  def inner_emit( self, lines, parent, context ):
    if None != self.definition.get('emit'):
      captures = map( lambda s: String(s).to_xs(), list(self.cache) ) 
      return String(self.definition['emit']).format_with_array(captures)
    
    group = ''
    if self.cache.lastindex:
      group = self.cache.group(1)
    return ''.join([self.start_tag()] + self.transform_syntax([group], context) + [self.end_tag()])
  
  def emit_syntax( self, inner ):
    start_spaces = []
    end_spaces = []
    inner = ''.join(inner)
    md = re.match( r'^\s*', inner )
    if md:
      start_spaces = [md.group(0)]
    md = re.match( r'\s*$', inner )
    if md:
      end_spaces = [md.group(0)]
    inner = inner.strip()
    return start_spaces + super([inner]) + end_spaces
  
  def regexp_absolute_start( self ):
    return ''

  def regexp_absolute_end( self ):
    return ''

  def save_regexp( self, regexp ):
    if regexp and len(regexp) > 0 and not re.search(regexp, ''):
      self.sheet.inline_regexps.append( regexp ) 
