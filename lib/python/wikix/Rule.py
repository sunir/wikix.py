import re
import json
from collections import deque

class Rule(object):
  def __init__( self, name, definition ):
    self.name = name
    self.definition = definition
    self.tag = definition.get('tag')
    self.children = []
    self.regexp = None
    self.regexps = {}
    self.sheet = None

  def add_child( self, child ):
    self.children.append( child )
  
  def add_children( self, children  ):
    children = children or []
    for name in children:
      child = self.sheet.rules[name]
      if not child:
          raise Exception("Unknown child " + name)
      elif Rule == child.__class__:
        self.add_children( child.definition['children'] )          
      else:
        self.add_child( child )

  def transform_syntax( self, lines, context  ):
    # print self.name + " (" + str(self.__class__) + "): " + lines[0] 
    if deque != type(lines):
      lines = deque(lines)
    output = []
    if self.must_preserve_whitespace():
      self.sheet.preserve_whitespace += 1
    
    while len(lines) > 0:
      # Skip useless blank lines
      if not self.is_inline() and not re.search( r'\S', lines[0] ):
        line = lines.popleft()
        if self.sheet.preserve_whitespace > 0:
          output.append( line )
        continue

      child = self.next_matching_child( lines )
      if not child:
        output = output + list(lines)
        break

      emitted = child.emit( lines, self, context )
      output.extend( emitted )
      # if len(lines) > 0:
      #   print self.name + " : child ("+child.name+") emitted: " + lines[0] 
 
    if self.must_preserve_whitespace():
      self.sheet.preserve_whitespace -= 1
    
    if 0 == len(output):
      return list(lines)
    return list(output)

  # regexp_start is a regular expression fragment that matches everything upto but not
  # including the inner fragment (which will be matched by child rules). regexp_end
  # is a regular expression that follows the inner fragment.
  #
  # They are split in two to allow for regular expressions that may begin on one line
  # and end on another, and thus require two regular expressions.
  def regexp_absolute_start( self ): 
    return r'\A'
  def regexp_absolute_end( self ): 
    return r'\Z'

  def set_regexp( self, starts_regexp, starts_delimited_by_regexp, optionally_starts_regexp, ends_regexp, optionally_ends_regexp  ):
    if None == starts_regexp:
      raise Exception('Must have a starting regexp')

    if starts_delimited_by_regexp:
      starts_regexp += '(?=(?:' + starts_regexp + ')*' + starts_delimited_by_regexp + ')'
    
    if optionally_starts_regexp:
      starts_regexp += optionally_starts_regexp
    
    regexp = starts_regexp
    self.save_regexp( starts_regexp )

    optionally_ends_regexp = optionally_ends_regexp or ''

    # Set ends_regexp == '' for lines that need the (.*?) but have no end regexp.
    if None != ends_regexp:        
      regexp = starts_regexp + '(.*?)' + ends_regexp
      
      # Save the ending regexp so we can escape it later
      if len(ends_regexp) > 0:
        ends_regexp += optionally_ends_regexp
      self.save_regexp( ends_regexp )
    
    regexp += optionally_ends_regexp
    
    self.regexp = re.compile( 
      self.regexp_absolute_start() + 
      regexp + 
      self.regexp_absolute_end(), 
      re.MULTILINE
    )
    
    self.regexps = {
      'starts': starts_regexp,
      'starts_delimited_by': starts_delimited_by_regexp,
      'ends': ends_regexp,
      'optionally_ends': optionally_ends_regexp
    }

  def is_inline( self ):
    return False
  
  def match( self, lines ):
    self.implemented_by_subclass
    
  def emit( self, lines, parent, context ):
    self.implemented_by_subclass

  def start_tag( self ):
    return "<" + self.tag + ">" if self.tag else ''
  
  def end_tag( self ):
    return "</" + self.tag + ">" if self.tag else ''
  
  def next_matching_child( self, lines ):
    for child in self.children:      
      # Skip children who only transform to syntax (i.e. not to xhtml)
      if child.definition.get('direction') == 'syntax':
        continue
      
      match = child.match( lines )
      if match:
        return child
  
  def save_regexp( self, regexp ):
    if None != regexp and len(regexp) > 0:
      regexp = re.compile(regexp)
      if not regexp.match(''):
        self.sheet.line_regexps.append( regexp ) 
  
  def store( self, context, text ):
    context['store'].append( text )
    return "\0" + str(len(context['store'])-1)

  def must_preserve_whitespace( self ):
    return self.definition.get('whitespace') == 'preserve'