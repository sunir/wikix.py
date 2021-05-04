import json

class WikixSheets(object):
  def __init__(self, intermap=None):
    self.intermap = intermap

  def default(self): 
    return """
      {
        "root": {
          "scope": "root",
          "children": [ 
            "hr", "lists", "blockquote", "monospace", "table", 
            "headers",
            "p"
          ]
        },

        "lists": {
          "children": [ "ul", "ol" ]
        },

        "ul": {
          "scope": "multiline",
          "tag": "ul",
          "starts": "-",
          "children": ["li"]
        },

        "ol": {
          "scope": "multiline",
          "tag": "ol",      
          "starts": "#",
          "children": ["li"]
        },
          
        "li": {
          "scope": "cell",
          "tag": "li",
          "children": ["lists", "inline_styles"]
        },

        "blockquote": {
          "scope": "multiline",
          "tag": "blockquote",
          "starts": ">",
          "children": [ "blockquote", "p" ]
        },

        "monospace": {
          "scope": "multiline",
          "tag": "pre",
          "starts": " ",
          "whitespace": "preserve",
          "children": [ "monospace_line" ]
        },
        
        "monospace_line": {
          "scope": "line",
          "children": ["inline_styles"]
        },

        "table": {
          "scope": "multiline",
          "tag": "table",
          "starts": "||",    
          "children": ["tr"]
        },
        
        "tr": {
          "scope": "line",
          "tag": "tr",
          "children": ["td"]
        },
        
        "td": {
          "scope": "inline",
          "tag": "td",
          "ends": "||",    
          "children": ["inline_styles"]
        },

        "headers": {
          "children": [ "h6", "h5", "h4", "h3", "h2" ]
        },

        "h2": {
          "scope": "line",
          "starts": "==",
          "optionallyEnds": "=+",
          "tag": "h2",
          
          "children": ["inline_styles"]
        },

        "h3": {
          "scope": "line",
          "starts": "===",
          "optionallyEnds": "=+",
          "tag": "h3",
          
          "children": ["inline_styles"]
        },

        "h4": {
          "scope": "line",
          "starts": "====",
          "optionallyEnds": "=+",
          "tag": "h4",
          
          "children": ["inline_styles"]
        },

        "h5": {
          "scope": "line",
          "starts": "=====",
          "optionallyEnds": "=+",
          "tag": "h5",
          
          "children": ["inline_styles"]
        },

        "h6": {
          "scope": "line",
          "starts": "======+",
          "optionallyEnds": "=+",
          "tag": "h6",
          
          "children": ["inline_styles"]
        },

        "hr": {
          "scope": "line",
          "equals": "----",
          "optionallyEnds": "-+",
          "tag": "hr"
        },
        
        "p": {
          "scope": "paragraph",
          "tag": "p",    
          "children": ["inline_styles"]
        },  

        "inline_styles": {
         "children": [ "escape", "links", "strong", "b", "em", "i", "br" ]
        },
        
        "escape": {
          "children": ["escape_escape_syntax", "escape_syntax"]
        },

        "escape_escape_syntax": {
          "scope": "inline",
          "equals": "```",
          "emit": "`"
        },

        "escape_syntax": {
          "scope": "inline",
          "starts": "`",
          "ends": "`"
        },
        
        "br": {
          "scope": "inline",
          "equals": "\\n",
          "tag": "br",
          "direction": "syntax"
        },

        "strong": {
          "scope": "inline",
          "starts": "*",
          "ends": "*",
          "tag": "strong",
          
          "children": ["inline_styles"]
        },

        "em": {
          "scope": "inline",
          "starts": "_",
          "ends": "_",
          "tag": "em",
          
          "children": ["inline_styles"]
        },

        "b": {
          "scope": "inline",
          "starts": "*",
          "ends": "*",
          "tag": "b",
          "direction": "syntax",
          
          "children": ["inline_styles"]
        },

        "i": {
          "scope": "inline",
          "starts": "_",
          "ends": "_",
          "tag": "i",
          "direction": "syntax",
          
          "children": ["inline_styles"]
        },

        "links": {
          "children": [ "empty_descriptive_link", "descriptive_link", "url", "page" ]
        },

        "empty_descriptive_link": {
          "scope": "link",
          "link": {
            "pattern": "[[ url ]]",
            "href": "$1",
            "text": "$1"
          }
        },

        "descriptive_link": {
          "scope": "link",
          "link": {
            "pattern": "[[ url  text ]]",
            "href": "$1", 
            "text": "$2",
            "image": "$2"
          }
        },

        "url": {
          "scope": "link",
          "link": {
            "pattern": "url",
            "href": "$1",
            "text": "$1",
            "image": ""
          }
        },
        
        "page": {
          "scope": "link",
          "link": {
            "pattern": "[[ text ]]",
            "href": "/group/\\\@space/page/view/$1",
            "page_missing": "no-such-page",
            "text": "$1"
          }
        }
      }
    """

  def meatball(self):
    return """
      {
        "root": {
          "scope": "root",
          "children": [ 
            "code","pre",
            "toc",
            "hr", "lists", "blockquote", "monospace", "table", 
            "headers",
            "p"
          ]
        },

        "code": {
          "scope": "block",
          "starts": "<code>",
          "ends": "</code>",
          "whitespace": "preserve",
          "tag": "code",
          "children": ["code_line"]
        },
        
        "pre": {
          "scope": "block",
          "starts": "<pre>",
          "ends": "</pre>",
          "whitespace": "preserve",
          "tag": "pre",
          "children": ["code_line"]
        },
        
        "toc": {
          "scope": "line",
          "equals": "<toc>"
        },
        
        "code_line": {
          "scope": "line",
          "children": ["escape"]
        },

        "hr": {
          "scope": "line",
          "equals": "----",
          "optionallyEnds": "-+",
          "tag": "hr"
        },

        "lists": {
          "children": [ "ul", "ol", "dl" ]
        },

        "ul": {
          "scope": "multiline",
          "tag": "ul",
          "starts": "*",
          "children": ["li"]
        },

        "ol": {
          "scope": "multiline",
          "tag": "ol",      
          "starts": "#",
          "children": ["li"]
        },
        
        "dl": {
          "scope": "multiline",
          "tag": "dl",
          "starts": ";",
          "children": ["lists","dd","dt"]
        },
        
        "dt": {
          "scope": "inline",
          "tag": "dt",
          "until": ":",
          "children": ["inline_styles"]
        },
        
        "dd": {
          "scope": "line",
          "tag": "dd",
          "starts": ":",
          "children": ["inline_styles"]
        },

        "li": {
          "scope": "cell",    
          "tag": "li",
          "children": ["lists", "inline_styles"]
        },

        "blockquote": {
          "scope": "multiline",
          "tag": "blockquote",
          "starts": ":",
          "children": [ "blockquote", "p" ]
        },

        "monospace": {
          "scope": "multiline",
          "tag": "pre",
          "starts": " ",
          "whitespace": "preserve",
          "children": ["monospace_line"]
        },
        
        "monospace_line": {
          "scope": "paragraph",
          "children": ["inline_styles"]
        },

        "table": {
          "scope": "multiline",
          "tag": "table",
          "starts": "||",    
          "children": ["tr"]
        },
        
        "tr": {
          "scope": "line",
          "tag": "tr",
          "children": ["td"]
        },
        
        "td": {
          "scope": "inline",
          "tag": "td",
          "ends": "||",
          "children": ["inline_styles"]
        },

        "headers": {
          "children": [ "h6", "h5", "h4", "h3", "h2" ]
        },

        "h2": {
          "scope": "line",
          "starts": "==",
          "optionallyStarts": " +#",
          "optionallyEnds": "=+",
          "tag": "h2",
          
          "children": ["inline_styles"]
        },

        "h3": {
          "scope": "line",
          "starts": "===",
          "optionallyStarts": " +#",
          "optionallyEnds": "=+",
          "tag": "h3",
          
          "children": ["inline_styles"]
        },

        "h4": {
          "scope": "line",
          "starts": "====",
          "optionallyStarts": " +#",
          "optionallyEnds": "=+",
          "tag": "h4",
          
          "children": ["inline_styles"]
        },

        "h5": {
          "scope": "line",
          "starts": "=====",
          "optionallyStarts": " +#",
          "optionallyEnds": "=+",
          "tag": "h5",
          
          "children": ["inline_styles"]
        },

        "h6": {
          "scope": "line",
          "starts": "======+",
          "optionallyStarts": " +#",
          "optionallyEnds": "=+",
          "tag": "h6",
          
          "children": ["inline_styles"]
        },
        
        "p": {
          "scope": "paragraph",
          "tag": "p",    
          "children": ["inline_styles"]
        },  

        "inline_styles": {
          "children": [ "escape", "nowiki_inline", "links", "strong", "b", "bold", "em", "i", "italic" ]
        },

        "escape": {
          "children": ["escape_syntax", "escape_syntax"]
        },

        "escape_escape_syntax": {
          "scope": "inline",
          "equals": "```",
          "emit": "`"
        },

        "escape_syntax": {
          "scope": "inline",
          "starts": "`",
          "ends": "`"
        },
        
        "nowiki_inline": {
          "scope": "inline",
          "starts": "<nowiki>",
          "ends": "</nowiki>"
        },
        
        "strong": {
          "scope": "inline",
          "starts": "'''",
          "ends": "'''",
          "tight": true,
          "tag": "strong",
          
          "children": ["inline_styles"]
        },

        "bold": {
          "scope": "inline",
          "starts": "'''",
          "ends": "'''",
          "tag": "b",
          "direction": "syntax",
          
          "children": ["inline_styles"]
        },

        "b": {
          "scope": "inline",
          "starts": "<b>",
          "ends": "</b>",
          "tag": "b",
          
          "children": ["inline_styles"]
        },

        "em": {
          "scope": "inline",
          "starts": "''",
          "ends": "''",
          "tag": "em",
          
          "children": ["inline_styles"]
        },

        "italic": {
          "scope": "inline",
          "starts": "''",
          "ends": "''",
          "tag": "i",
          "direction": "syntax",
          
          "children": ["inline_styles"]
        },

        "i": {
          "scope": "inline",
          "starts": "<i>",
          "ends": "</i>",
          "tag": "i",
          
          "children": ["inline_styles"]
        },

        "links": {
          "children": [ "empty_descriptive_link", "descriptive_link", "url", "page", "intermap", "camelcase", "anchor" ]
        },
        
        %s,

        "empty_descriptive_link": {
          "scope": "link",
          "link": {
            "pattern": "[ url ]",
            "tight": true,
            "href": "$1",
            "text": "$1"
          }
        },

        "descriptive_link": {
          "scope": "link",
          "link": {
            "pattern": "[ url text ]",
            "tight": true,
            "href": "$1", 
            "text": "[$2]",
            "image": "$2"
          }
        },

        "url": {
          "scope": "link",
          "link": {
            "pattern": "url",
            "href": "$1",
            "text": "$1",
            "image": ""
          }
        },
        
        "page": {
          "scope": "link",
          "link": {
            "pattern": "[[ text ]]",
            "tight": true,
            "href": "/wiki/$1",
            "page_missing": "no-such-page",
            "text": "$1"
          }
        },
        
        "camelcase": {
          "scope": "link",
          "link": {
            "pattern": {
              "regexp": "(\\\\b[A-Z]+[a-z]+[A-Z][A-Za-z]+(?:\\\#\\\\w+)?\\\\b)(\\\&quot;\\\&quot;(\\\\w+))?"
            },
            "href": "/wiki/$1",
            "page_missing": "no-such-page",
            "text": "$1",
            "after": "$3"
          }
        },

        "anchor": {
          "scope": "link",
          "link": {
            "pattern": "[#slug]",
            "name": "$1"
          }
        }
      }
    """ % self.intermap.json()
