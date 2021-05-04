import re
from unique import unique
from String import String
from Root import Root
from collections import deque

class Sheet(object):  
  def __init__(self):
    self.preserve_whitespace = 0
    self.rules = {}
    self.line_regexps = []
    self.inline_regexps = []
    self.root = None
  
  def transform_syntax( self, text, context ):
    if not context:
      context = {} 
    if not context.get('store'):
      context['store'] = [] 
    text = self.normalize( text )
    lines = text.split( "\n" )
    return ''.join( self.restore( context, self.root.transform_syntax(lines, context) ) )
      
  def add( self, rule ):
    self.rules[rule.name] = rule
    rule.sheet = self
    if Root == rule.__class__:
      self.root = rule
      
  def escape_inline_syntax( self, text ):
    if not self.escape_inline_syntax_regexp:
      self.escape_inline_syntax_regexp = re.compile(
        String(
          '|'.join(
            map( 
              lambda r: "(#" + r + ")", 
              unique(self.inline_regexps)
            ) 
          )
        ).from_xs()
      )
    return re.sub( 
      self.escape_inline_syntax_regexp, 
      lambda md: "`" + md.group(0) + "`",
      text
    )

  def escape_line_syntax( self, text ):
    if not self.escape_line_syntax_regexp:
      self.escape_line_syntax_regexp = re.compile(
        '^(' + 
        String( 
          '|'.join( 
            map( 
              lambda r: "(#" + r + ")", 
              unique(self.line_regexps)
            )
          )
        ).from_xs() + 
        ')'
      )
    return re.sub(
      self.escape_line_syntax_regexp,
      lambda md: "`" + md.group(0) + "`",
      text
    )
  
  def normalize( self, text ):
    # Normalize new lines
    text = re.sub( r'\r\n', "\n", text )
    text = re.sub( r'\r', "\n", text )
    
    # Join lines with trailing backslash (\)
    text = re.sub( r'\s*\\\s*(\n|$)', ' ', text )  
          
    # Escape character entities
    text = String(text).to_xs()
    
    return text
  
  def restore( self, context, lines ):
    result = []
    for line in lines:
      n = 1
      while n > 0:
        (line, n) = re.subn( 
          r'\0(\d+)',
          lambda md: context['store'][int(md.group(1))],
          line
        )
      result.append(line)
    return result