"""


require 'nokogiri'

class Nokogiri::XML::Node
  def data
    return self.text
  end
end

module Wikix
  class Sheet
    def transform_xhtml( xhtml )
      xhtml = Nokogiri::HTML(xhtml.gsub(/&nbsp;/,' ').gsub(/\r\n?/,"\n"))
      body = xhtml.search('body')
      if( body.length > 0 )
        xhtml = body[0]
      end
      return self.root.transform_xhtml(xhtml)[0].join('').gsub(/\r\n?/,"\n").sub(/\n+\z/,'') # .gsub(/\n\n+/,"\n\n") TODO: This breaks elements that preserve whitespace
    end
  end

  class Rule
    # The basic algorithm is to transform the inner children first, and then wrap 
    # it with syntax from this node
    # We return a pair = [array of emitted syntax, cost of this transformation]
    def transform_xhtml( xhtml )      
      transformation = transform_xhtml_children( xhtml )
      transformation[0] = self.emit_syntax( transformation[0] )
      return transformation
    end
    
    def transform_xhtml_children( xhtml )
      # If it's a leaf text node, just return it
      if( xhtml.cdata? || xhtml.text? )
        data = xhtml.data
        return [ [self.sheet.escape_inline_syntax(data)], 0 ]
      end

      # Combine the output from all the children
      result = [ [], 0 ]
      for i in 0..(xhtml.children.length-1)
        xhtml_child = xhtml.children[i]
        transformation = self.transform_xhtml_child( xhtml_child )
        result[0] = result[0].concat( transformation[0] )
        result[1] += result[1]        
      end
      return result
    end

    def transform_xhtml_child( xhtml_child )    
      tag_children = []
      if( nil != xhtml_child.name )
        tag_children = self.find_children_by_tag( xhtml_child.name )
      end
      
      transformations = []  
      for i in 0..(tag_children.length-1)
        rule = tag_children[i]
        transformation = rule.transform_xhtml(xhtml_child)
        if( transformation )
          transformations.push( self.adjust_transformation_for_rule(transformation,rule) )
        end
      end
     
      # If there are no matches, then we flatten the node to text
      if( 0 == transformations.length )
        transformation = self.transform_xhtml_children( xhtml_child )
        
        # Every time we flatten a node, it adds one to the cost
        transformation[1] += 1
        return transformation
      end
      
      # Pick the transformation with the lowest cost
      return transformations.sort { |a,b| a[1] <=> b[1] }.first
    end
    
    def adjust_transformation_for_rule(transformation, rule)
      return transformation
    end

    def find_children_by_tag( tag )
      result = []
      for i in 0..(self.children.length-1)
        child = self.children[i]
        found = []
        
        # Skip children who only transform to xhtml (i.e. not to syntax)
        if( child.definition['direction'] == 'xhtml' )
          next;
        end
        
        # If this child doesn't have a tag, check its children
        if( nil == child.tag )
          found = child.find_children_by_tag(tag)
        
        # If this child represents the given tag, grab it
        elsif( child.has_tag(tag) )
          found = [child]      
        end
        
        result = result.concat( found )
      end
      return result
    end
    
    def has_tag( tag )
      return tag == self.tag
    end

    def start_syntax
      start = definition['starts']
      if( nil == start && definition['equals'].instance_of?(String) )
        start = definition['equals']
      end
      start = start || ''
      return start.minimal_regexp
    end

    def end_syntax
      return (definition['ends'] || '').minimal_regexp
    end

    def emit_syntax( inner )      
      return [self.start_syntax].concat( inner ).concat( [self.end_syntax] )
    end
  end

  class Root
    def adjust_transformation_for_rule(transformation, rule)
      if( rule.respond_to?(:escape_line_syntax) )
        transformation[0] = [rule.escape_line_syntax( transformation[0].join('') )]
      end
      transformation[0].push("\n")
      return transformation
    end
  end

  class Multiline
    def emit_syntax( inner )
      # TODO: this can't be right for pres.
      inner_syntax = inner.join('').sub(/\n*\z/,'').sub(/\A\n*/,'').gsub(/\n+/,"\n")

      if @regexps[:starts_delimited_by]        
        inner_syntax = inner_syntax.gsub( /^(?!#{@regexps[:start]})/, definition['startsDelimitedBy'].minimal_regexp )
      end
      return [ inner_syntax.gsub( /^/, self.start_syntax ), "\n" ]
    end
  end

  class Line
    def emit_syntax( inner )
      result = super
      result.push( "\n" )
      return result
    end
  end

  class Cell
    def emit_syntax( inner )
      result = super
      result.push("\n")
      return result
    end
    
    def adjust_transformation_for_rule( transformation, rule )
      if( !rule.is_inline )
        transformation[0].unshift( "\n" )
      end
      return transformation
    end        
  end

  class Paragraph
    def emit_syntax( inner )
      result = super
      result.push( "\n" )
      return result
    end
    
    def escape_line_syntax( text )
      return self.sheet.escape_line_syntax( text )
    end
  end

  class Link    
    def has_tag( tag )
      return 'a' == tag || (nil != self.definition['link']['image'] && 'img' == tag)
    end

    def get_href( node )
      # Nokogiri does not translate HTML character entities, so do from_xs ourselves
      if( 'img' == node.name )
        return node['src'].from_xs
      elsif( 'a' == node.name )
        return (node['href'] || '').from_xs
      else
        raise "Unknown link type: #{node.name}"
      end
    end

    def get_link_text( node )
      if( 'img' == node.name )
        return node['alt'] || ''
      elsif( 'a' == node.name )
        if( nil == node.children[0] )
          return ''
        end
        return node.children[0].data
      else
        raise "Unknown link type: #{node.name}"
      end
    end

    def match_substitutions( substitutions, pattern, text )
      map = []
      regexp = pattern.escape_regexp.gsub(/@\w+/, '.+?').gsub( /\\\$(\d)/ ) { |m|
        map.push( $1.to_i )
        '(.+?)'
      }
      regexp = Regexp.new( '\A' + regexp + '\z' )

      match_data = text.match(regexp)
      if( match_data )
        match_data = match_data.to_a
        match_data.shift # Burn $0, which is the whole matched string
        while( match_data.length > 0 )
          substitutions[map.shift] = match_data.shift
        end
        return true
      end
      
      return false
    end

    def get_substitutions( xhtml )
      # Get link segments
      href = get_href( xhtml )
      text = get_link_text( xhtml )
      
      # Get substitutions. If either match fails, this link doesn't match.
      substitutions = []
      
      if( !match_substitutions( substitutions, self.definition['link']['href'], href ) )
        return
      end
      
      # Decode textual URI fragments
      for i in 1..(substitutions.length-1)
        if( nil != substitutions[i] && @uri_encode_map[i] )
          substitutions[i] = substitutions[i].decode_uri          
        end
      end
      
      text_pattern = self.definition['link']['text']
      if( 'img' == xhtml.name )
        text_pattern = self.definition['link']['image']
      end
      
      if( !match_substitutions( substitutions, text_pattern, text ) )
        return
      end
      
      return substitutions
    end

    def get_substitutable_link_pattern
      pattern = self.definition['link']['pattern']
      if( !pattern.instance_of?(String) && pattern['regexp'] )
        pattern = pattern['regexp']
      end
        
      # Transform pattern
      counter = 0
      # TODO slug
      pattern = pattern.gsub( / ( )*/, '\1' ).gsub( /(url|text|word|\(.*?\))/ ) { |m| 
        counter = counter + 1; 
        '$' + counter.to_s; 
      }
      
      return pattern
    end

    # Compute the cost of this match. The cost is the total length of the substitutions we found.
    # The idea is that the tighter the match, the better the link rule that represents this link
    def compute_cost( substitutions )
      cost = 0
      for i in (1..substitutions.length-1)
        if( substitutions[i] )
          cost += substitutions[i].length
        end
      end
      
      return cost.to_f
    end

    def transform_xhtml( xhtml )
      result = nil      
      # Get all the $0, $1, $2s back from the xhtml
      if( nil == (substitutions = get_substitutions(xhtml)) )
        return
      end
      
      # If we emitted $0 somewhere, use that, as that is exactly the link text
      if( substitutions[0] )
        result = [substitutions[0]]
        
      # Otherwise, recompose the link text
      else
        pattern = get_substitutable_link_pattern
        result = [pattern.format_with_array(substitutions)]
      end

      # Only return successfully if the result is something this rule would match
      if( (match_data = self.match(result)) && (match_data.begin(0) == 0) )
        cost = compute_cost(substitutions)
        cost += result.first.length.to_f / xhtml.to_s.length
        return [result, cost]
      end
    end
  end
end
"""