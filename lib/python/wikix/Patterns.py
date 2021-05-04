import re
class Patterns(object):
  patterns = {}
  patterns['url_character'] = "[A-Za-z0-9;/?:@&=+$,_.!~*'()%#|\\-]"
  patterns['url_protocols'] = "http|https|ftp|news|mailto|telnet|gopher"
  patterns['url'] = "((?:" + patterns['url_protocols'] + "):" + patterns['url_character'] + "+)"
  patterns['image'] = re.compile(r'\A[^\?]+.(bmp|jpg|jpeg|gif|png)(\?|$)', re.I)
