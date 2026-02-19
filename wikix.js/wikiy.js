String.prototype._wikix_match = String.prototype.match;
String.prototype.extend( {
  escape_punctuation: function() {
    return this.replace( /([^\w\d\s])/g, "\\$1" );
  },
  
  escape_regexp: function() {
    return this.replace( /([\(\)\:\?\*\-\{\}\|\[\]])/g, "\\$1" );
  },
  
  to_uri: function() {
    return escape(this);
  },

  from_uri: function() {
    return unescape(this);
  },
  
  to_xs: function() {
    return this.replace( /&/g, '&amp;' ).replace( /</g, '&lt;' ).replace( />/g, '&gt;' ).replace( /"/g, '&quot;' );
  },

  from_xs: function() {
    return this.replace( /&apos;/g, "'" ).replace( /&quot;/g, '"' ).replace( /&gt;/g, '>' ).replace( /&lt;/g, '<' ).replace( /&amp;/g, '&' );
  },

  format_with_array: function( array ) {
    return this.replace( /\$(\d+)/g, function( m, index ) { 
      return array[parseInt(index)] || ''
    })
  },

  minimal_regexp: function() {
    return this.replace( /(.)\+/g, "$1" )
  },

  unchomp: function() {
    return this.match( /\n$/ ) ? this : this + "\n"
  },
  
  strip: function() {
    return this.replace( /^\s*/, '' ).replace( /\s*$/, '' )
  },

  // Make Javascript MatchData similar to Ruby MatchData
  match: function( regexp ) {
    var result = this._wikix_match( regexp );
    if( result )
      result.regexp = regexp;
    return result;
  }
} );

// Make Javascript MatchData similar to Ruby MatchData
Array.prototype.extend( {
  pos: function() { 
    if( this.position )
      return this.position;
    return this.position = this.regexp ? this.input.search(this.regexp) : -1;
  },
  
  pre_match: function() {
    if( !this.regexp )
      return '';
    var pos = this.pos();
    return this.input.substring( 0, pos );
  },
  
  post_match: function() {
    if( !this.regexp )
      return '';
    var pos = this.pos();
    return this.input.substring( pos + this[0].length );
  },
  
  map: function(f) {
    result = [];
    for( var i = 0; i < this.length; i++ ) {
      result.push(f(this[i]))
    }
    return result;
  }
} );

var Wikix = function( sheet ) {
  return Wikix.compile( sheet );
}
Wikix.patterns = {};
Wikix.patterns.url_character = "[A-Za-z0-9;/?:@&=+$,_.!~*'()%#|\-]";
Wikix.patterns.url_protocols = "http|https|ftp|news|mailto|telnet|gopher";
Wikix.patterns.url = "((?:" + Wikix.patterns.url_protocols + "):" + Wikix.patterns.url_character + "+)";
Wikix.patterns.image = /^[^\?]+.(bmp|jpg|jpeg|gif|png)(\?|$)/i;

Wikix.compile = function( json ) {
  var Compiler = {
    compile_sheet: function( json ) {
      sheet = new Wikix.Sheet;
    
      json.each( function(name) { 
        var definition = json[name];
        if( rule = Compiler.compile_rule(name, definition) ) {
          sheet.add(rule);
          Compiler.compile_regexp( rule, definition );
        }
      } );
      if( !sheet.root() ) {
        throw "No rule named 'root'";
      }
      
      this.compile_children( sheet );
      
      return sheet;
    },
    
    compile_rule: function( name, definition ) {
      scope = {
        multiline: Wikix.Multiline,
        line: Wikix.Line,
        paragraph: Wikix.Paragraph,
        inline: Wikix.Inline,
        link: Wikix.Link,
        block: Wikix.Block,
        cell: Wikix.Cell,
        root: Wikix.Root,
      }[definition['scope']]

      if( !scope ) {
        scope = Wikix.Rule;
      }

      return new scope( name, definition )
    },
    
    compile_regexp: function( rule, definition ) {
      var starts_regexp, ends_regexp, optionally_ends_regexp
      
      if( undefined != definition['equals'] ) {
        starts_regexp = this.compile_pattern( definition['equals'] );
      }
      else if( undefined != definition['link'] ) {
        link_pattern = this.compile_pattern( definition['link']['pattern'] );
        link_pattern = rule.compile_link_pattern( link_pattern );
        starts_regexp = link_pattern;      
      }        
      else {
        starts_regexp = this.compile_pattern( definition['starts'] );
        ends_regexp = '';
      }
            
      if( undefined != definition['ends'] ) {
        ends_regexp = this.compile_pattern( definition['ends'] );
      }
      else if( undefined != definition['until'] ) {
        ends_regexp = "(?=$|" + this.compile_pattern(definition['until']) + ")";
      }
      
      if( undefined != definition['optionallyEnds'] ) {
        optionally_ends_regexp = "(?:" + this.compile_pattern( definition['optionallyEnds'] ) + ")?";
      }

      rule.set_regexp( starts_regexp, ends_regexp, optionally_ends_regexp );
    },
    
    compile_pattern: function( pattern ) {
      pattern = pattern || '';
      if( pattern.regexp ) {
        return pattern.regexp;
      }
      return pattern.escape_regexp().to_xs();
    },

    compile_children: function( sheet ) {
      sheet.rules.each( function(name) {
        var rule = sheet.rules[name];
        rule.add_children( rule.definition['children'] );
      } );
    }
  };
  
  return Compiler.compile_sheet( json );
};

Wikix.Sheet = Class.create( function() {
  function normalize( text ) {
    // Normalize new lines
    text = text.replace( /\r\n/g, "\n" );
    text = text.replace( /\r/g, "\n" );
    
    // Join lines with trailing backslash (\)
    text = text.replace( /\s*\\\s*(\n|$)/g, ' ' );

    // Escape character entities
    text = text.to_xs()
    
    return text;
  }

  return {
    initialize: function() {
      this.preserve_whitespace = 0;
      this.rules = {};
      this.line_regexps = [];
      this.inline_regexps = [];
    },
    
    transform_syntax: function( text ) {
      text = normalize( text );
      lines = text.split( "\n" );
      return this.root().transform_syntax( lines ).join( '' );
    },
    
    add: function( rule ) {
      this.rules[rule.name] = rule;
      rule.sheet = this;
    },
    
    root: function() {
      return this.rules['root'];
    }
  };
}() );

Wikix.Rule = Class.create( function() {
  return {
    initialize: function( name, definition ) {
      this.name = name;
      this.definition = definition;
      this.tag = definition['tag'];
      this.children = [];      
      this.preserve_whitespace = (definition['whitespace'] == 'preserve');
    },
    
    add_child: function( child ) {
      this.children.push( child );
    },
    
    add_children: function( children ) {
      children = children || [];
      for( var i = 0; i < children.length; i++ ) {
        var name = children[i];
        var child = this.sheet.rules[name];
        if( !child )
          throw "Unknown child " + name;
        else if( Wikix.Rule == child.constructor )
          this.add_children( child.definition['children'] );
        else
          this.add_child( child );
      }
    },
    
    transform_syntax: function( lines ) {
      var output = [];
      if( this.preserve_whitespace ) {
        this.sheet.preserve_whitespace += 1;
      }
      
      while( lines.length > 0 ) {
        // Skip useless blank lines
        if( !this.is_inline() && !lines[0].match(/\S/) ) {        
          line = lines.shift()
          if( this.sheet.preserve_whitespace > 0 ) {
            output.push( line );
          }
          continue;
        }

        child = this.next_matching_child( lines );
        if( !child ) {
          output = output.concat( lines );
          break;
        }
        
        emitted = child.emit( lines, this );
        output = output.concat( emitted );
      }

      if( this.preserve_whitespace ) {
        this.sheet.preserve_whitespace -= 1;
      }

      return (0 == output.length) ? lines : output;
    },

    // regexp_start is a regular expression fragment that matches everything upto but not
    // including the inner fragment (which will be matched by child rules). regexp_end
    // is a regular expression that follows the inner fragment.
    //
    // They are split in two to allow for regular expressions that may begin on one line
    // and end on another, and thus require two regular expressions.
    set_regexp: function( starts_regexp, ends_regexp, optionally_ends_regexp ) {
      var regexp = starts_regexp;
      this.save_regexp( starts_regexp )
      
      optionally_ends_regexp = optionally_ends_regexp || '';

      // Set ends_regexp == '' for lines that need the (.*?) but have no end regexp.
      if( undefined != ends_regexp ) {
        regexp = starts_regexp + '((.|\n)*?)' + ends_regexp;
        
        // Save the ending regexp so we can escape it later
        if( ends_regexp.length > 0 ) {
          ends_regexp += optionally_ends_regexp;
        }
        this.save_regexp( ends_regexp )
      }
      
      regexp += optionally_ends_regexp;
      
      regexp = 
        this.constructor.classApply( 'regexp_absolute_start' ) 
        + regexp 
        + this.constructor.classApply( 'regexp_absolute_end' );
        
      this.regexp = new RegExp( regexp, '' );
    },
    
    /* PROTECTED */
    is_inline: function() { 
      return false; 
    },
      
    match: function( lines ) { 
      throw "implemented by subclass"; 
    },
    
    emit: function( lines, parent ) { 
      throw "implemented by subclass"; 
    },

    start_tag: function() {
      return this.tag ? "<" + this.tag + ">" : '' 
    },
    
    end_tag: function() { 
      return this.tag ? "</" + this.tag + ">" : '' 
    },
    
    next_matching_child: function( lines ) {
      var best_match = { index: lines[0].length };
      var best_child;
      for( var i = 0; i < this.children.length; i++ ) {
        var child = this.children[i];
        var match = child.match( lines );
        if( !match ) {
          continue;
        }
        
        if(
          // if this match is earlier than the previous best match, and therefore should be parsed first
          match.index < best_match.index || (     
          
            // This match is at the same location as our current best match,
            match.index == best_match.index && 
            
            // but spans a greater amount of text, and therefore is a parent element of our current best match
            match[0].length > best_match[0].length 
          )
        ) {
          // For block, multiline, line, paragraph really this is the first matching child
          // since all of these elements match the whole line.
          //
          // Inline elements may leave behind transformations that collide with other inline
          // elements, and therefore we have to parse them on a first come, first serve basis
          if( !child.is_inline() ) {
            return child;
          }
        
          best_match = match;
          best_child = child;
        }
      }
      return best_child;
    },
    
    save_regexp: function( regexp ) {
      if( undefined != regexp && regexp.length > 0 ) {
        this.sheet.line_regexps.push( regexp ) 
      }
    }
  }
}() )

Wikix.Rule.regexp_absolute_start = function() { return '^'; }
Wikix.Rule.regexp_absolute_end = function() { return '$'; }

Wikix.Multiline = Class.create( Wikix.Rule, function() {
  return {
    match: function( lines ) {
      return lines[0].match( this.regexp );
    },
    
    emit: function( lines, parent ) {
      body = [];
      
      while( (lines.length > 0) && (match_data = lines[0].match(this.regexp)) ) {
        line = match_data[1];
        if( this.preserve_whitespace || this.sheet.preserve_whitespace > 0 ) {
          line = line.unchomp();
        }
        
        body.push( line );
        lines.shift();
      }      
      return [this.start_tag()].concat( this.transform_syntax(body) ).concat( [this.end_tag()] );
    }
  }
}() );

Wikix.Line = Class.create( Wikix.Rule, function() {
  return {
    match: function( lines ) {
      return this.cache = lines[0].match( this.regexp );
    },
    
    emit: function( lines, parent ) {
      lines.shift();
      return [this.start_tag()].concat( this.transform_syntax([this.cache[1] || '']) ).concat( [this.end_tag()] );
    }
  }
}() );

Wikix.Paragraph = Class.create( Wikix.Rule, function() {
  return {    
    match: function( lines ) {
      return lines[0].match( this.regexp );
    },
    
    emit: function( lines, parent ) {
      // Grab everything until the next blank line
      body = [];
      while( (lines.length > 0) && lines[0].match(/\S/) && this === parent.next_matching_child(lines) ) {
        body.push( lines.shift() )
      }
      
      join_character = ' '
      if( this.sheet.preserve_whitespace > 0 || this.preserve_whitespace ) {
        join_character = ''
      }
      
      return [this.start_tag()].concat( this.transform_syntax([body.join(join_character)]) ).concat( [this.end_tag()] )
    },
    
    // Paragraphs always match
    set_regexp: function( regexp_start, regexp_end ) {
      this.regexp = new RegExp('');
    }
  }
}() );

// Root: identity wrapper — no tag, just processes block children
Wikix.Root = Class.create( Wikix.Rule, function() {
  return {
    match: function( lines ) { return lines[0].match( this.regexp ); },
    emit: function( lines, parent ) {
      return this.transform_syntax( lines );
    }
  }
}() );

// Block: fenced block with explicit starts/ends lines (e.g. <code>...</code>)
Wikix.Block = Class.create( Wikix.Rule, function() {
  return {
    match: function( lines ) {
      return this.cache = lines[0].match( this.regexp );
    },
    emit: function( lines, parent ) {
      lines.shift(); // consume starts line
      var body = [];
      var ends_re = new RegExp( '^' + this.definition['ends'].escape_regexp().to_xs() );
      while( lines.length > 0 && !lines[0].match( ends_re ) ) {
        body.push( lines.shift() );
      }
      if( lines.length > 0 ) lines.shift(); // consume ends line
      return [this.start_tag()].concat( this.transform_syntax(body) ).concat( [this.end_tag()] );
    }
  }
}() );

// Cell: single list item — matches the leading * or # prefix
Wikix.Cell = Class.create( Wikix.Rule, function() {
  return {
    match: function( lines ) {
      return this.cache = lines[0].match( this.regexp );
    },
    emit: function( lines, parent ) {
      lines.shift();
      return [this.start_tag()].concat( this.transform_syntax([this.cache[1] || '']) ).concat( [this.end_tag()] );
    }
  }
}() );

Wikix.Inline = Class.create( Wikix.Rule, function() {
  return {
    is_inline: function() { 
      return true; 
    },
    
    match: function( lines ) {
      return this.cache = lines[0].match( this.regexp );
    },
    
    emit: function( lines, parent ) {
      lines[0] = this.cache.post_match();
      
      if( undefined != this.definition['emit'] ) {
        return [ this.cache.pre_match(), this.definition['emit'] ];
      }
      
      return [this.cache.pre_match(), this.start_tag()].concat( this.transform_syntax([this.cache[1] || '']) ).concat( [this.end_tag()] );
    },
    
    save_regexp: function( regexp ) {
      if( regexp && regexp.length > 0 ) {
        this.sheet.inline_regexps.push( regexp ) ;
      }
    }
  }
}() );

Wikix.Inline.regexp_absolute_start = function() { return ''; }
Wikix.Inline.regexp_absolute_end = function() { return ''; }

Wikix.Link = Class.create( Wikix.Inline, function() {
  return {
    initialize: function( name, definition ) {
      Wikix.Inline.prototype.initialize.apply( this, [name, definition] );
      this.tag = 'a';
    },
  
    emit: function( lines, parent ) {
      lines[0] = this.cache.post_match();
      
      // Duplicate the match array because we are going to manipulate it in place
      var captures = this.cache.toArray();      

      // Strip trailing punctuation if and only if we are given a link pattern
      var trailing_punctuation = undefined;
      if( undefined != this.definition['link']['pattern'] && String == this.definition['link']['pattern'].constructor && this.definition['link']['pattern'].match(/url$/) ) {
        var regexp = /([^\w\/]?)$/;
        if( captures[captures.length-1].match(regexp) ) {
          trailing_punctuation = RegExp.$1;
          captures[captures.length-1] = captures[captures.length-1].replace( regexp, '' );        
        }
      }

      uri_captures = []
      for( var i = 0; i < captures.length; i++ ) {
        uri_captures[i] = captures[i];
        if( this.uri_encode_map[i] ) {
          uri_captures[i] = uri_captures[i].from_xs().to_uri();
        }
      }      
      var href = this.definition['link']['href'].format_with_array( uri_captures ).to_xs();
      
      text_captures = captures;
      if( 0 == this.sheet.preserve_whitespace ) {
        text_captures = captures.map( function(s) { return s.strip() } )
      }
      var text = this.definition['link']['text'].format_with_array( text_captures );

      var result;
      if( undefined != this.definition['link']['image'] && href.match(Wikix.patterns['image']) ) {
        var alt = '';
        if( '' != this.definition['link']['image'] ) {
          alt = " alt='" + this.definition['link']['image'].format_with_array( captures ) + "'";
        }
        result = "<img src='" + href + "' class='" + this.name + "'" + alt + "/>"        
      }
      else {
        result = "<a href='" + href + "' class='" + this.name + "'>" + text + "</a>";
      }
      
      return [ this.cache.pre_match(), result, trailing_punctuation || '' ]
    },
    
    compile_link_pattern: function( pattern ) {
      var that = this;
      pattern = pattern.replace( /(\\ )+/g, '\s+' );
      
      // Build a map of which captures match to URLs or texts so we know
      // which captures to URI encode
      this.uri_encode_map = [ true ]  // first map entry corresponds to $0
      pattern = pattern.replace( /(url|text)/g, function(m) {
        if( 'url' == m ) {
          that.uri_encode_map.push( false );
          return Wikix.patterns['url'];
        }
        else { // if( 'text' == m ) {
          that.uri_encode_map.push( true );
          return '(.+?)' ;
        }
      })
      return pattern;
    },
    
    save_regexp: function( regexp ) {
    }    
  }
}() );