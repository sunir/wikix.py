from .Rule import Rule

class Root(Rule):
  def emit_syntax( self, inner ):
    """Root: join all block-level content directly (blocks add their own newlines)."""
    return inner