import os.path
import re
import json

class Intermap(object):
  def __init__(self, intermap=None, intermap_text=None, intermap_filename='lib/intermap.txt'):
    if intermap_filename and os.path.exists(intermap_filename) and os.path.isfile(intermap_filename):
      with open(intermap_filename, 'rt') as file:
        intermap_text = file.read()
      
    if intermap_text:
      self.intermap_json = self._intermap_text_to_json(intermap_text)

  def json(self):
    return self.intermap_json

  def _intermap_text_to_json(self, intermap_text):
    names = []
    result = []
    cells = re.split(r'\s+', intermap_text)
    while len(cells) >= 2:
      name = cells[0]
      url = cells[1]
      if '"' in name or '"' in url:
        raise Exception("Cannot include double quote (\") in Intermap file.")
      cells = cells[2:]
      names.append("intermap__" + name + "_bracketed")
      names.append("intermap__" + name)
      result.append(
        """
        "intermap__%s": {
          "scope": "link",
          "link": {
            "pattern": "%s:word",
            "href": "%s$1",
            "text": "%s:$1"
          }
        },

        "intermap__%s_bracketed": {
          "scope": "link",
          "link": {
            "pattern": "[ %s:word text ]",
            "href": "%s$1",
            "text": "[$2]",
            "image": "$2",
            "tight": true
          }
        },
        """ % (name, name, url, name, name, name, url)
      )
    
    result.append(
      """
      "intermap": {
        "children": %s
      }
      """ % (json.dumps(names))
    )
    intermap_json = "\n".join(result)
    return intermap_json