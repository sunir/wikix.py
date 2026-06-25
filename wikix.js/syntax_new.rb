# TODO: test Multiline.startsDelimitedBy
# test fails: roundtrip "<ul><li><strong>f</strong>f</li></ul>"

module Wikix
  @@intermap = 'intermap: {}'
  if File.exists?('lib/intermap.txt')
    file = File.open('lib/intermap.txt','r')
    intermap_txt = file.read
    file.close
    
    names = []
    json = []
    intermap_txt.split(/\s+/).each_slice(2) { |name, url|
      names.push( name )
      json.push( <<-EOF )
        '#{name}': {
          scope: 'link',
          link: {
            pattern: '#{name}:word',
            href: '#{url}$1',
            text: '#{name}:$1'
          }
        },
      EOF
    }
    
    json.push( <<-EOF )
      intermap: {
        children: [#{names.collect(&:inspect).join(',')}]
      }
    EOF

    @@intermap = json.join("\n")
  end

  @@json_sheets = {
    :default => <<-JSON,
      {
        root: {
          scope: 'root',
          children: [ 
            'hr', 'lists', 'blockquote', 'monospace', 'table', 
            'headers',
            'p'
          ]
        },

        lists: {
          children: [ 'ul', 'ol' ]
        },

        ul: {
          scope: 'multiline',
          tag: 'ul',
          starts: '-',
          children: ['li']
        },

        ol: {
          scope: 'multiline',
          tag: 'ol',      
          starts: '#',
          children: ['li']
        },
          
        li: {
          scope: 'cell',
          tag: 'li',
          children: ['lists', 'inline_styles']
        },

        blockquote: {
          scope: 'multiline',
          tag: 'blockquote',
          starts: '>',
          children: [ 'blockquote', 'p' ]
        },

        monospace: {
          scope: 'multiline',
          tag: 'pre',
          starts: ' ',
          whitespace: 'preserve',
          children: [ 'monospace_line' ]
        },
        
        monospace_line: {
          scope: 'line',
          children: ['inline_styles']
        },

        table: {
          scope: 'multiline',
          tag: 'table',
          starts: '||',    
          children: ['tr']
        },
        
        tr: {
          scope: 'line',
          tag: 'tr',
          children: ['td']
        },
        
        td: {
          scope: 'inline',
          tag: 'td',
          ends: '||',    
          children: ['inline_styles']
        },

        headers: {
          children: [ 'h6', 'h5', 'h4', 'h3', 'h2' ]
        },

        h2: {
          scope: 'line',
          starts: "==",
          optionallyEnds: "=+",
          tag: 'h2',
          
          children: ['inline_styles']
        },

        h3: {
          scope: 'line',
          starts: "===",
          optionallyEnds: "=+",
          tag: 'h3',
          
          children: ['inline_styles']
        },

        h4: {
          scope: 'line',
          starts: "====",
          optionallyEnds: "=+",
          tag: 'h4',
          
          children: ['inline_styles']
        },

        h5: {
          scope: 'line',
          starts: "=====",
          optionallyEnds: "=+",
          tag: 'h5',
          
          children: ['inline_styles']
        },

        h6: {
          scope: 'line',
          starts: "======+",
          optionallyEnds: "=+",
          tag: 'h6',
          
          children: ['inline_styles']
        },

        hr: {
          scope: 'line',
          equals: "----",
          optionallyEnds: "-+",
          tag: 'hr'
        },
        
        p: {
          scope: 'paragraph',
          tag: 'p',    
          children: ['inline_styles']
        },  

        inline_styles: {
         children: [ 'escape', 'links', 'strong', 'b', 'em', 'i', 'br' ]
        },
        
        escape: {
          children: ['escape_syntax', 'escape_syntax']
        },

        escape_escape_syntax: {
          scope: 'inline',
          equals: '```',
          emit: '`'
        },

        escape_syntax: {
          scope: 'inline',
          starts: '`',
          ends: '`'
        },
        
        br: {
          scope: 'inline',
          equals: '\n',
          tag: 'br',
          direction: 'syntax'
        },

        strong: {
          scope: 'inline',
          starts: "*",
          ends: "*",
          tag: 'strong',
          
          children: ['inline_styles']
        },

        em: {
          scope: 'inline',
          starts: "_",
          ends: "_",
          tag: 'em',
          
          children: ['inline_styles']
        },

        b: {
          scope: 'inline',
          starts: "*",
          ends: "*",
          tag: 'b',
          direction: 'syntax',
          
          children: ['inline_styles']
        },

        i: {
          scope: 'inline',
          starts: "_",
          ends: "_",
          tag: 'i',
          direction: 'syntax',
          
          children: ['inline_styles']
        },

        links: {
          children: [ 'empty_descriptive_link', 'descriptive_link', 'url', 'page' ]
        },

        empty_descriptive_link: {
          scope: 'link',
          link: {
            pattern: '[[ url ]]',
            href: '$1',
            text: '$1'
          }
        },

        descriptive_link: {
          scope: 'link',
          link: {
            pattern: '[[ url  text ]]',
            href: '$1', 
            text: '$2',
            image: '$2'
          }
        },

        url: {
          scope: 'link',
          link: {
            pattern: 'url',
            href: '$1',
            text: '$1',
            image: ''
          }
        },
        
        page: {
          scope: 'link',
          link: {
            pattern: '[[ text ]]',
            href: '/group/@space/page/view/$1',
            page_missing: 'no-such-page',
            text: '$1'
          }
        }
      }
    JSON
  
    :meatball => <<-JSON,
      {
        root: {
          scope: 'root',
          children: [ 
            'code','pre',
            'toc',
            'hr', 'lists', 'blockquote', 'monospace', 'table', 
            'headers',
            'p'
          ]
        },

        code: {
          scope: 'block',
          starts: '<code>',
          ends: '</code>',
          whitespace: 'preserve',
          tag: 'code',
          children: ['code_line']
        },
        
        pre: {
          scope: 'block',
          starts: '<pre>',
          ends: '</pre>',
          whitespace: 'preserve',
          tag: 'code',
          children: ['code_line']
        },
        
        toc: {
          scope: 'line',
          equals: '<toc>'
        },
        
        code_line: {
          scope: 'line',
          children: ['escape']
        },

        hr: {
          scope: 'line',
          equals: "----",
          optionallyEnds: "-+",
          tag: 'hr'
        },

        lists: {
          children: [ 'ul', 'ol', 'dl' ]
        },

        ul: {
          scope: 'multiline',
          tag: 'ul',
          starts: '*',
          children: ['li']
        },

        ol: {
          scope: 'multiline',
          tag: 'ol',      
          starts: '#',
          children: ['li']
        },
        
        dl: {
          scope: 'multiline',
          tag: 'dl',
          starts: ';',
          children: ['lists','dd','dt']
        },
        
        dt: {
          scope: 'inline',
          tag: 'dt',
          until: ':',
          children: ['inline_styles']
        },
        
        dd: {
          scope: 'line',
          tag: 'dd',
          starts: ':',
          children: ['inline_styles']
        },

        li: {
          scope: 'cell',    
          tag: 'li',
          children: ['lists', 'inline_styles']
        },

        blockquote: {
          scope: 'multiline',
          tag: 'blockquote',
          starts: ':',
          children: [ 'blockquote', 'p' ]
        },

        monospace: {
          scope: 'multiline',
          tag: 'pre',
          starts: ' ',
          whitespace: 'preserve',
          children: ['monospace_line']
        },
        
        monospace_line: {
          scope: 'paragraph',
          children: ['inline_styles']
        },

        table: {
          scope: 'multiline',
          tag: 'table',
          starts: '||',    
          children: ['tr']
        },
        
        tr: {
          scope: 'line',
          tag: 'tr',
          children: ['td']
        },
        
        td: {
          scope: 'inline',
          tag: 'td',
          ends: '||',
          children: ['inline_styles']
        },

        headers: {
          children: [ 'h6', 'h5', 'h4', 'h3', 'h2' ]
        },

        h2: {
          scope: 'line',
          starts: "==",
          optionallyStarts: " +#",
          optionallyEnds: "=+",
          tag: 'h2',
          
          children: ['inline_styles']
        },

        h3: {
          scope: 'line',
          starts: "===",
          optionallyStarts: " +#",
          optionallyEnds: "=+",
          tag: 'h3',
          
          children: ['inline_styles']
        },

        h4: {
          scope: 'line',
          starts: "====",
          optionallyStarts: " +#",
          optionallyEnds: "=+",
          tag: 'h4',
          
          children: ['inline_styles']
        },

        h5: {
          scope: 'line',
          starts: "=====",
          optionallyStarts: " +#",
          optionallyEnds: "=+",
          tag: 'h5',
          
          children: ['inline_styles']
        },

        h6: {
          scope: 'line',
          starts: "======+",
          optionallyStarts: " +#",
          optionallyEnds: "=+",
          tag: 'h6',
          
          children: ['inline_styles']
        },
        
        p: {
          scope: 'paragraph',
          tag: 'p',    
          children: ['inline_styles']
        },  

        inline_styles: {
          children: [ 'escape', 'nowiki_inline', 'links', 'strong', 'b', 'em', 'i' ]
        },

        escape: {
          children: ['escape_syntax', 'escape_syntax']
        },

        escape_escape_syntax: {
          scope: 'inline',
          equals: '```',
          emit: '`'
        },

        escape_syntax: {
          scope: 'inline',
          starts: '`',
          ends: '`'
        },
        
        nowiki_inline: {
          scope: 'inline',
          starts: '<nowiki>',
          ends: '</nowiki>'
        },
        
        strong: {
          scope: 'inline',
          starts: "'''",
          ends: "'''",
          tight: true,
          tag: 'strong',
          
          children: ['inline_styles']
        },

        em: {
          scope: 'inline',
          starts: "''",
          ends: "''",
          tag: 'em',
          
          children: ['inline_styles']
        },

        b: {
          scope: 'inline',
          starts: "'''",
          ends: "'''",
          tag: 'b',
          direction: 'syntax',
          
          children: ['inline_styles']
        },

        i: {
          scope: 'inline',
          starts: "''",
          ends: "''",
          tag: 'i',
          direction: 'syntax',
          
          children: ['inline_styles']
        },

        links: {
          children: [ 'empty_descriptive_link', 'descriptive_link', 'url', 'page', 'intermap', 'camelcase' ]
        },
        
        #{@@intermap},

        empty_descriptive_link: {
          scope: 'link',
          link: {
            pattern: "[ url ]",
            tight: true,
            href: '$1',
            text: '$1'
          }
        },

        descriptive_link: {
          scope: 'link',
          link: {
            pattern: "[ url  text ]",
            tight: true,
            href: '$1', 
            text: '$2',
            image: '$2'
          }
        },

        url: {
          scope: 'link',
          link: {
            pattern: 'url',
            href: '$1',
            text: '$1',
            image: ''
          }
        },
        
        page: {
          scope: 'link',
          link: {
            pattern: "[[ text ]]",
            tight: true,
            href: '/group/@space/page/view/$1',
            page_missing: 'no-such-page',
            text: '$1'
          }
        },
        
        camelcase: {
          scope: 'link',
          link: {
            pattern: {
              regexp: '(\\b[[:upper:]]+[[:lower:]]+[[:upper:]][[:alpha:]]*\\b)'
            },
            href: '/group/@space/page/view/$0',
            page_missing: 'no-such-page',
            text: '$1'
          }
        }
      }
    JSON
  }
end

class String
  def escape_punctuation
    return self.gsub( /([^\w\d\s])/ ) { |m| "\\" + m }
  end

  def unescape_punctuation
    return self.gsub( /\\(\\?)/, '\1' )
  end

  def escape_regexp
    return Regexp.escape(self).gsub( /\\\+/, '+' )
  end

  def escape_variable_interpolations
    return self.gsub( /([\$\@])/, '\1\\' )
  end

  def unescape_variable_interpolations
    return self.gsub( /([\$\@])\\/, '\1' )
  end

  def encode_uri
    return self.gsub( /([^a-zA-Z0-9\!\@\$\*\(\)\-\_\,\.])/ ) { |m| sprintf( "%%%02x", m[0] ) }
  end

  # TODO: I'm not sure this is all that safe. What about UTF8 attacks?
  def decode_uri
    return self.gsub( /\+/, ' ' ).gsub( /\%([a-fA-F0-9]{2})/ ) { |m| $1.hex.chr }
  end

  # Existing to_xs does not escape quotes (') or doublequotes (")
  def to_xs
    return self.gsub( /&/, '&amp;' ).gsub( /</, '&lt;' ).gsub( />/, '&gt;' ).gsub( /"/, '&quot;' ).gsub( /'/, '&#039;' );
  end

  def from_xs
    return self.gsub( /&apos;|&#039;/, "'" ).gsub( /&quot;/, '"' ).gsub( /&gt;/, '>' ).gsub( /&lt;/, '<' ).gsub( /&amp;/, '&' );
  end

  def format_with_array( array )
    return self.gsub( /\$(\d+)/ ) { |m|
      array[$1.to_i].escape_variable_interpolations || ''
    }
  end
  
  def format_with_hash( hash )
    return self.gsub( /\@(\w+)/ ) { |m|
      hash[$1].escape_variable_interpolations || ''  
    }    
  end

  def minimal_regexp
    return self.gsub( /(.)\+/, '\1' )
  end

  def unchomp
    return self =~ /\n\z/m ? self : self + "\n"
  end  
end

module Wikix
  @@patterns = {}
  @@patterns[:url_character] = "[A-Za-z0-9;/?:@&=+$,_.!~*'()%#|\\-]"
  @@patterns[:url_protocols] = "http|https|ftp|news|mailto|telnet|gopher"
  @@patterns[:url] = "((?:" + @@patterns[:url_protocols] + "):" + @@patterns[:url_character] + "+)"
  @@patterns[:image] = /\A[^\?]+.(bmp|jpg|jpeg|gif|png)(\?|$)/i
  def self.patterns; @@patterns; end

  module Compiler
    def self.compile( json )
      json = ::ActiveSupport::JSON.decode( json )
      return compile_sheet( json )
    end
    
  private
    def self.compile_sheet( json )
      sheet = Sheet.new
    
      json.each { |name, definition|
      
        if rule = compile_rule(name, definition)
          sheet.add(rule)
          compile_regexp( rule, definition )
        end
      }
      if( !sheet.root )
        raise "No rule scoped 'root'"
      end
      
      compile_children( sheet )
      
      return sheet
    end
    
    def self.compile_rule( name, definition )
      scope = {
        'root' => Wikix::Root,
        'multiline' => Wikix::Multiline,
        'line' => Wikix::Line,
        'cell' => Wikix::Cell,
        'block' => Wikix::Block,
        'paragraph' => Wikix::Paragraph,
        'inline' => Wikix::Inline,
        'link' => Wikix::Link,
      }[definition['scope']]
      
      if( !scope )
        scope = Wikix::Rule
      end
      
      return scope.new( name, definition )
    end
    
    def self.compile_regexp( rule, definition )
      starts_regexp = starts_delimited_by = ends_regexp = optionally_ends_regexp = nil
      
      if( nil != definition['equals'] )
        starts_regexp = compile_pattern( definition['equals'] )
        
      elsif( nil != definition['link'] )
        link_pattern = compile_pattern( definition['link']['pattern'], definition['tight'] || definition['link']['tight'] )
        link_pattern = rule.compile_link_pattern( link_pattern )
        starts_regexp = link_pattern
        
      else
        starts_regexp = compile_pattern( definition['starts'], definition['tight'] )
        ends_regexp = ''
        
        if definition['startsDelimitedBy']
          starts_delimited_by_regexp = compile_pattern( definition['startsDelimitedBy'] )          
        end
      end
            
      if( nil != definition['ends'] )
        ends_regexp = compile_pattern( definition['ends'] )
      
      elsif( nil != definition['until'] )
        ends_regexp = "(?=$|" + compile_pattern( definition['until'] ) + ")";
      end
      
      if( nil != definition['optionallyStarts'] )
        optionally_starts_regexp = "(?:" + compile_pattern( definition['optionallyStarts'] ) + ")?"
      end
        
      if( nil != definition['optionallyEnds'] )
        optionally_ends_regexp = "(?:" + compile_pattern( definition['optionallyEnds'] ) + ")?"
      end

      rule.set_regexp( starts_regexp, starts_delimited_by_regexp, optionally_starts_regexp, ends_regexp, optionally_ends_regexp )
    end
    
    def self.compile_pattern( pattern, tightly = false )
      pattern = pattern || ''
      if( pattern.kind_of?(Hash) && pattern.has_key?('regexp') )
        return pattern['regexp']
      end
      
      pattern_segments = [pattern]
      
      stopper = ''
      if tightly
        pattern_segments = pattern.split(/(\s*[^\s\w]+)/).reject(&:empty?)
        chars = pattern_segments.first.chars.to_a.uniq
        stopper = '(?!' + chars[0].to_xs.escape_regexp + ')' if 1 == chars.length
      end
        
      pattern_segments = pattern_segments.collect { |s| s.escape_regexp.to_xs }.insert( 1, stopper )
      
      return pattern_segments.join('')
    end
    
    def self.compile_children( sheet )      
      sheet.rules.each { |name, rule|
      
        rule.add_children( rule.definition['children'] )
      }      
    end    
  end

  class Sheet
    attr_accessor :preserve_whitespace, :rules
    attr_reader :line_regexps, :inline_regexps, :root
    
    def initialize
      @preserve_whitespace = 0
      @rules = {}
      @line_regexps = []
      @inline_regexps = []
    end
    
    def transform_syntax( text, context )
      context = {} unless context
      context['store'] = [] unless context['store']
      
      text = normalize( text )      
      lines = text.split( "\n" )
      return restore( context, root.transform_syntax( lines, context ) ).join( '' )
    end
        
    def add( rule )
      @rules[rule.name] = rule
      rule.sheet = self
      
      if Wikix::Root == rule.class
        @root = rule
      end
    end
        
    def escape_inline_syntax( text )
      unless @escape_inline_syntax      
        @escape_inline_syntax = Regexp.new(
          self.inline_regexps.
          uniq.
          map {|r| "(#{r})" }.
          join('|').
          from_xs
        )
      end
      
      return text.gsub( @escape_inline_syntax ) { |m| "`" + m + "`" }
    end    

    def escape_line_syntax( text )
      unless @escape_line_syntax
        @escape_line_syntax = Regexp.new( 
          '^(' + 
          self.line_regexps.
          uniq.
          map {|r| "(#{r})" }.
          join('|').
          from_xs + 
          ')'
        )
      end
      return text.sub( @escape_line_syntax ) { |m| "`" + m + "`" }
    end
    
  private
    def normalize( text )
      # Normalize new lines
      text.gsub!( /\r\n/, "\n" )
      text.gsub!( /\r/, "\n" )
      
      # Join lines with trailing backslash (\)
      text.gsub!( /\s*\\\s*(\n|$)/, ' ' )  
            
      # Escape character entities
      text = text.to_xs
      
      return text
    end
    
    def restore( context, lines )
      lines.each { |line|
        while line.gsub!( /\0(\d+)/ ) {
          context['store'][$1.to_i]
        }
        end
      }
    end
  end

  class Rule
    attr_accessor :sheet
    attr_reader :name, :definition, :tag, :children, :regexp
    
    def initialize( name, definition )
      @name = name
      @definition = definition
      @tag = definition['tag']
      @children = []
    end
    
    def add_child( child )
      @children.push( child )
    end
    
    def add_children( children )
      children = children || []
      for i in 0..(children.length-1)
        name = children[i]
        child = self.sheet.rules[name]
        if( !child )
            raise "Unknown child " + name
        elsif Rule == child.class 
          self.add_children( child.definition['children'] )          
        else
          self.add_child( child )
        end        
      end
    end

    def transform_syntax( lines, context )
      output = []
      if( preserve_whitespace )
        self.sheet.preserve_whitespace += 1
      end
      
      while( lines.length > 0 )
        # Skip useless blank lines
        if( !self.is_inline && !lines[0].match(/\S/) )
          line = lines.shift()
          if( self.sheet.preserve_whitespace > 0 )
            output.push( line )
          end
          next
        end

        child = next_matching_child( lines )
        if( !child )
          output = output.concat( lines )
          break
        end        

        emitted = child.emit( lines, self, context )
        output = output.concat( emitted )
      end
   
      if( preserve_whitespace )
        self.sheet.preserve_whitespace -= 1
      end
      
      return (0 == output.length) ? lines : output
    end

    # regexp_start is a regular expression fragment that matches everything upto but not
    # including the inner fragment (which will be matched by child rules). regexp_end
    # is a regular expression that follows the inner fragment.
    #
    # They are split in two to allow for regular expressions that may begin on one line
    # and end on another, and thus require two regular expressions.
    def self.regexp_absolute_start; '\A'; end
    def self.regexp_absolute_end; '\z'; end
    def set_regexp( starts_regexp, starts_delimited_by_regexp, optionally_starts_regexp, ends_regexp, optionally_ends_regexp )
      if !starts_regexp
        raise 'Must have a starting regexp'
      end      

      if starts_delimited_by_regexp
        starts_regexp += '(?=(?:' + starts_regexp + ')*' + starts_delimited_by_regexp + ')'
      end
      
      if optionally_starts_regexp
        starts_regexp += optionally_starts_regexp
      end
      
      regexp = starts_regexp
      save_regexp( starts_regexp )

      optionally_ends_regexp = optionally_ends_regexp || ''
 
      # Set ends_regexp == '' for lines that need the (.*?) but have no end regexp.
      if( nil != ends_regexp )        
        regexp = starts_regexp + '(.*?)' + ends_regexp
        
        # Save the ending regexp so we can escape it later
        if( ends_regexp.length > 0 )
          ends_regexp += optionally_ends_regexp
        end        
        save_regexp( ends_regexp )
      end
      
      regexp += optionally_ends_regexp
      
      @regexp = Regexp.new( 
        self.class.regexp_absolute_start + 
        regexp + 
        self.class.regexp_absolute_end, 
        Regexp::MULTILINE
      )
      
      @regexps = {
        :starts => starts_regexp,
        :starts_delimited_by => starts_delimited_by_regexp,
        :ends => ends_regexp,
        :optionally_ends => optionally_ends_regexp
      }
    end

    def is_inline
      return false
    end
    
  protected
    def match( lines )
      implemented_by_subclass
    end
      
    def emit( lines, parent, context )
      implemented_by_subclass
    end

    def start_tag
      return self.tag ? "<" + self.tag + ">" : ''
    end
    
    def end_tag
      return self.tag ? "</" + self.tag + ">" : ''
    end
    
    def next_matching_child( lines )
      for i in 0..(children.length-1)
        child = children[i]
        
        # Skip children who only transform to syntax (i.e. not to xhtml)
        if( child.definition['direction'] == 'syntax' )
          next
        end
        
        match = child.match( lines )
        if match          
          return child
        end
      end
      return
    end
    
    def save_regexp( regexp )      
      if( nil != regexp && regexp.length > 0 && !''.match(regexp) )
        self.sheet.line_regexps.push( regexp ) 
      end
    end
    
    def store( context, text )
      context['store'].push( text )
      return "\0#{(context['store'].length-1).to_s}"
    end

  private
    def preserve_whitespace
      return self.definition['whitespace'] == 'preserve'
    end
  end
  
  class Root < Rule
  end

  class Multiline < Rule
    def match( lines )
      return lines[0].match( @regexp )
    end
    
    def emit( lines, parent, context )
      body = []
      
      while( (lines.length > 0) && (match_data = lines[0].match(@regexp)) )
        line = match_data[1]
        if( preserve_whitespace || self.sheet.preserve_whitespace > 0 )          
          line = line.unchomp
        end
        
        if @regexps[:starts_delimited_by]
          line = line.sub(/^#{@regexps[:starts_delimited_by]}/,'')
        end
        
        body.push( line )
        lines.shift        
      end

      return [ self.start_tag ] + self.transform_syntax( body, context ) + [ self.end_tag ]
    end    
  end

  class Line < Rule
    def match( lines )
      return @cache = lines[0].match( @regexp )
    end
    
    def emit( lines, parent, context )
      lines.shift
      return [self.start_tag].concat( self.transform_syntax([@cache[1] || ''], context) ).concat( [self.end_tag] )
    end  
  end

  class Cell < Rule
    def match( lines )
      if !@block_children
        @block_children = Regexp.new( 
          '^(' + 
            self.children.
            reject(&:is_inline).
            collect(&:regexp).
            uniq.
            join('|') +
          ')',
          Regexp::MULTILINE
        )
      end
      
      if lines.empty?
        return
      end

      @cache = [ lines.shift ]
      while !lines.empty? && lines.first.match( @block_children )         
        @cache.push(lines.shift)
      end

      return @cache
    end
    
    def emit( lines, parent, context )
      cdata = ''
      if !@cache.first.match( @block_children )
        cdata = @cache.shift        
      end      
      return [self.start_tag].
        concat( self.transform_syntax([cdata], context) ).
        concat( self.transform_syntax(@cache, context) ).
        concat( [self.end_tag] )
    end  
  end
  
  class Block < Rule
    def match( lines )
      if !@start_regexp
        @starts_regexp = Regexp.new('^' + @regexps[:starts] + '$')
        @ends_regexp = Regexp.new('^' + @regexps[:ends] + '$')
      end
      @cache = []
      if lines[0].match(@starts_regexp)
        lines[1..-1].each { |line|
          if line.match(@ends_regexp)
            return @cache
          end          
          @cache.push( line )
        }
      end
      return @cache = nil
    end
    
    def emit( lines, parent, context )
      lines.slice!(0..@cache.length+2)
      
      if( preserve_whitespace || self.sheet.preserve_whitespace > 0 )          
        @cache = @cache.map { |line| line.unchomp }
      end
      
      return [self.start_tag + "\n"].concat( self.transform_syntax(@cache, context) ).concat( [self.end_tag] )
    end
  end
  
  class Paragraph < Rule
    # Paragraphs always match
    def match( lines )
      return lines[0].match( @regexp )
    end
    
    def emit( lines, parent, context )
      # Grab everything until the next blank line
      body = []      
      while( (lines.length > 0) && lines[0].match(/\S/) && self === parent.next_matching_child(lines) )
        body.push( lines.shift )
      end

      join_character = ' '
      if( self.sheet.preserve_whitespace > 0 || preserve_whitespace )
        join_character = ''
      end

      return [self.start_tag].concat( self.transform_syntax([body.join(join_character)], context) ).concat( [self.end_tag] )
    end
    
    # Paragraphs always match
    def set_regexp( *regexps )
      @regexp = //
    end
  end

  class Inline < Rule
    def is_inline
      return true
    end
    
    def match( lines )
      return @cache = lines[0].match( @regexp )
    end
    
    # Contract: Inline does not consume the line, but merely transforms it into the
    # storage, so other inline elements can continue to consume the line. 
    def emit( lines, parent, context )
      pre_match = @cache.pre_match
      post_match = @cache.post_match
      
      xhtml = inner_emit( lines, parent, context )      
      result = [pre_match, self.store(context, xhtml), post_match]
      
      # An exception to the contract! Prevent looping by actually consuming the front part of the line. 
      if pre_match.empty?        
        lines[0] = post_match
        result.pop
        return result
      end
        
      lines[0] = result.join('')
      return []
    end
    
    def inner_emit( lines, parent, context )
      if( nil != self.definition['emit'] )
        captures = @cache.to_a.map { |capture| capture.to_xs }        
        return self.definition['emit'].format_with_array(captures)
      end
      
      return ([self.start_tag] + self.transform_syntax([@cache[1] || ''],context) + [self.end_tag]).join('')
    end
    
    def emit_syntax( inner )
      start_spaces = []
      end_spaces = []
      inner = inner.join('')
      inner.sub!( /^\s*/ ) { |m| start_spaces = [m]; '' }
      inner.sub!( /\s*$/ ) { |m| end_spaces = [m]; '' }
      return start_spaces.concat( super([inner]) ).concat( end_spaces )
    end
    
    def self.regexp_absolute_start; ''; end
    def self.regexp_absolute_end; ''; end
    
    def save_regexp( regexp )
      if( regexp && regexp.length > 0 && !''.match(regexp) )
        self.sheet.inline_regexps.push( regexp ) 
      end
    end    
  end
  
  class Link < Inline
    def initialize( name, definition )
      super( name, definition )
      @tag = 'a'
      
      # Strip trailing punctuation if and only if we are given a link pattern
      # and the URL is the last thing      
      @strip_trailing_punctuation = 
        nil != definition['link']['pattern'] && 
        definition['link']['pattern'].instance_of?(String) && 
        definition['link']['pattern'].match(/url$/)
    end
      
    def match( lines )
      @cache = super( lines )
      
      # If the 'text' part of a link is devoid of significant characters,
      # this is not a match. e.g. [[ ! ]] is not a match, but [[ a! ]] is.
      captures = @cache.to_a
      for i in 0..(captures.length-1)
        if( @uri_encode_map[i] )
          return if captures[i].canonicalize.empty?
        end
      end
      
      return @cache
    end
    
    def inner_emit( lines, parent, context )      
      # Duplicate the match array because we are going to manipulate it in place
      captures = @cache.to_a
      if( 0 == self.sheet.preserve_whitespace )
        captures = captures.map { |s| s.strip() }
      end
      
      trailing_punctuation = nil
      if( @strip_trailing_punctuation )
        regexp = /([^\w\/]?)\z/
        captures[-1].sub!( regexp, '' )
        if Regexp.last_match
          trailing_punctuation = Regexp.last_match[0] 
        end
      end      

      uri_captures = []
      for i in 0..(captures.length-1)
        uri_captures[i] = captures[i]
        if( @uri_encode_map[i] )
          uri_captures[i] = uri_captures[i].from_xs.encode_uri.gsub(/\./,'%2e')
        end
      end

      href = definition['link']['href'].format_with_array( uri_captures ).format_with_hash( context ).unescape_variable_interpolations
      text = definition['link']['text'].format_with_array( captures ).format_with_hash( context ).unescape_variable_interpolations
      
      klass = self.name
      if( nil != definition['link']['page_missing'] && !Wikix.page_exists( href, context ) )
        klass = klass + ' ' + definition['link']['page_missing']
      end
      
      result = nil
      if( nil != definition['link']['image'] && href.match(Wikix.patterns[:image]) )
        alt = ''
        if( '' != definition['link']['image'] )
          alt = " alt='" + definition['link']['image'].format_with_array( captures ) + "'"
        end
        result = "<img src='" + href + "' class='" + klass + "'" + alt + "/>"
        
      else
        result = "<a href='" + href + "' class='" + klass + "'>" + text + "</a>";
      end
      return result + (trailing_punctuation || '')
    end

    def compile_link_pattern( pattern )
      
      pattern = pattern.gsub( /\\ \\ /, '\\s+' ).gsub( /\\ /, '\\s*' )
      
      # If the start of the link pattern is the same character
      # then we need to ensure the match is tight with some regexp magic
      pattern =~ /^\s*([^\w\s]+)\s*/
      
      # Build a map of which captures match to URLs or texts so we know
      # which captures to URI encode
      @uri_encode_map = [ true ]  # first map entry corresponds to $0
      pattern = pattern.gsub( /(url|text|word)/ ) { |m|
        if( 'url' == m ) 
          @uri_encode_map.push( false )
          Wikix.patterns[:url]
        
        elsif( 'text' == m )
          @uri_encode_map.push( true )
          '(\S.*?)'

        elsif( 'word' == m )
          @uri_encode_map.push( true )
          '(\S+)' 
          
        end
      }
      return pattern
    end
    
    def save_regexp( regexp )
    end
  end
end

#~ Compiler rules
#~ * Only paragraphs and lines can contain inline_styles 
#~ * Children are listed in descending order of priority
#~ * Multilines can only have starts, not equals, ends, or optionallyEnds
#~ * Blocks MUST have starts AND ends; never equals or optionallyEnds
#~ * Compiler generates regexy things for starts and ends
#~ * links require href and text
#~ * equals cannot have children
#~ * links cannot have children

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

module Wikix
  @@sheets = @@json_sheets.inject({}) { |hash, sheet| hash[sheet.first] = Compiler.compile( sheet.last ); hash }
  def self.sheet( space = :default )
    return @@sheets[space.to_sym] || @@sheets[:default]
  end
  
  def self.transform_syntax( text, space, link_collector = {} )
    return self.sheet(space).transform_syntax( text, { 'space' => space, 'links' => link_collector } )
  end

  def self.transform_xhtml( xhtml, space = :default )    
    return self.sheet(space).transform_xhtml( xhtml )
  end

  def self.page_exists( href, context )
    params = ActionController::Routing::Routes.recognize_path( href )
    context['links'][params[:id]] = 1
    return Page.exists?( :space => params[:space], :id => params[:id] )
  end
end