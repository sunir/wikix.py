from Compiler import Compiler

class Wikix(object):
  def __init__(self, wikix_sheet_json, get_page_id, does_page_exist):
    self.sheet_json = wikix_sheet_json
    self.sheet = Compiler().compile( self.sheet_json )
    self.get_page_id = get_page_id
    self.does_page_exist = does_page_exist

  def transform_syntax( self, text, link_collector = dict() ):
    return self.sheet.transform_syntax( text, { 
      'links': link_collector,
      'page_exists': lambda href,context: self.page_exists(href,context)
    } )

  def transform_xhtml( self, xhtml ):
    return self.sheet.transform_xhtml( xhtml )

  def page_exists( self, href, context ):
    page_id = self.get_page_id(href)
    context['links'][page_id] = 1
    return self.does_page_exist( page_id )