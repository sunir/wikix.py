import re
import json
from String import String
from Sheet import Sheet
from Root import Root
from Multiline import Multiline
from Line import Line
from Block import Block
from Paragraph import Paragraph
from Inline import Inline
from Link import Link
from Rule import Rule
from Cell import Cell

class Compiler(object):  
  def compile( self, json_string ):
    sheet_json = json.loads( json_string )
    return self.compile_sheet( sheet_json )
    
  def compile_sheet( self, sheet_json ):
    sheet = Sheet()
    for name in sheet_json:
      definition = sheet_json[name]
      rule = self.compile_rule(name, definition)
      if rule:
        sheet.add(rule)
        self.compile_regexp( rule, definition )
    if not sheet.root:
      raise Exception("No rule scoped 'root'")
    self.compile_children( sheet )
    return sheet
    
  def compile_rule( self, name, definition ):
    scope = {
      'root': Root,
      'multiline': Multiline,
      'line': Line,
      'cell': Cell,
      'block': Block,
      'paragraph': Paragraph,
      'inline': Inline,
      'link': Link,
    }.get(definition.get('scope'))
    
    if not scope:
      scope = Rule
    return scope( name, definition )
    
  def compile_regexp( self, rule, definition ):
    starts_regexp = starts_delimited_by_regexp = optionally_starts_regexp = ends_regexp = optionally_ends_regexp = None
    
    if None != definition.get('equals'):
      starts_regexp = self.compile_pattern( definition['equals'] )
      
    elif None != definition.get('link'):
      link_pattern = self.compile_pattern( definition['link']['pattern'], definition.get('tight', definition['link'].get('tight')) )
      link_pattern = rule.compile_link_pattern( link_pattern )
      starts_regexp = link_pattern
      
    else:
      starts_regexp = self.compile_pattern( definition.get('starts'), definition.get('tight',False) )
      ends_regexp = ''
      
      if definition.get('startsDelimitedBy'):
        starts_delimited_by_regexp = self.compile_pattern( definition['startsDelimitedBy'] )

    if None != definition.get('ends'):
      ends_regexp = self.compile_pattern( definition['ends'] )
    
    elif None != definition.get('until'):
      ends_regexp = "(?=$|" + self.compile_pattern( definition['until'] ) + ")";
    
    if None != definition.get('optionallyStarts'):
      optionally_starts_regexp = "(?:" + self.compile_pattern( definition['optionallyStarts'] ) + ")?"
      
    if None != definition.get('optionallyEnds'):
      optionally_ends_regexp = "(?:" + self.compile_pattern( definition['optionallyEnds'] ) + ")?"

    rule.set_regexp( starts_regexp, starts_delimited_by_regexp, optionally_starts_regexp, ends_regexp, optionally_ends_regexp )
  
  def compile_pattern( self, pattern, tightly = False ):
    pattern = pattern or ''
    if isinstance(pattern, dict) and pattern.get('regexp'):
      return pattern['regexp']
    pattern_segments = [pattern]
    
    # TODO What does tight mean?
    stopper = ''
    if tightly:
      pattern_segments = filter(bool, re.split(r'(\s*[^\s\w]+)', pattern))
      chars = list(set(pattern_segments[0]))
      if 1==len(chars):
        stopper = '(?!' + String(chars[0]).to_xs().escape_regexp() + ')'
      
    pattern_segments = map( lambda s: String(s).escape_regexp().to_xs(), pattern_segments )
    pattern_segments = [pattern_segments[0]] + [stopper] + pattern_segments[1:]
    
    return ''.join(pattern_segments)
  
  def compile_children( self, sheet ):      
    for rule in sheet.rules.values():
      rule.add_children( rule.definition.get('children') )  

#~ Compiler rules
#~ * Only paragraphs and lines can contain inline_styles 
#~ * Children are listed in descending order of priority
#~ * Multilines can only have starts, not equals, ends, or optionallyEnds
#~ * Blocks MUST have starts AND ends; never equals or optionallyEnds
#~ * Compiler generates regexy things for starts and ends
#~ * links require href and text
#~ * equals cannot have children
#~ * links cannot have children