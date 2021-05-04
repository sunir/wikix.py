import re
from wikix import Wikix
from wikix.WikixSheets import WikixSheets
from wikix.Intermap import Intermap

def get_page_id(href):
  md = re.search(r'^/wiki/(\S+?)(#.*)?$', href)
  if md:
    return md.group(1)

def does_page_exist(page_id):
  return page_id == 'TextFormattingRules'

meatball = Wikix(WikixSheets(Intermap()).meatball(), get_page_id, does_page_exist)
bibwiki = Wikix(WikixSheets(Intermap()).default(), get_page_id, does_page_exist)

if False:
	print meatball.transform_syntax("TextFormattingRules")
	print meatball.transform_syntax("SampleUndefinedPage")
	print meatball.transform_syntax("TextFormattingRules#anchor")
	print meatball.transform_syntax("Wiki")
	print meatball.transform_syntax("WikiC")
	print meatball.transform_syntax("http://www.usemod.com/cgi-bin/mb.pl?TextFormattingRules#anchor")
	print meatball.transform_syntax("[http://www.usemod.com/cgi-bin/mb.pl?TextFormattingRules#anchor anchor]")
	print meatball.transform_syntax("UseModWiki\"\"s")
	print meatball.transform_syntax("[UseMod:TextFormattingRules text formatting rules]")
	print meatball.transform_syntax("<b>bold</b>")
	print meatball.transform_syntax("<i>italic</i>")
	print meatball.transform_syntax("&lt;")
	print meatball.transform_syntax("<b>bold</b> cut off")
	print meatball.transform_syntax("<i>italic</i> cut off")
	print meatball.transform_syntax("<pre>\nSample <b>bold</b>, <i>italic</i>, and <b><i>bold+italic</i></b>.\n</pre>")
	print meatball.transform_syntax("Sample <b>bold</b>, <i>italic</i>, and <b><i>bold+italic</i></b>.")
	print meatball.transform_syntax("[#N888_7_2_1]")
	print meatball.transform_syntax("http://usemod.com/wiki.gif")
	print meatball.transform_syntax("ISBN 0-471-25311-1")
	print meatball.transform_syntax("""   This is the starting-spaces version of
   preformatted text.  Note that links like
   UseModWiki still work and '''bolding''' works.""")

	print meatball.transform_syntax("[UseMod:TextFormattingRules text formatting rules]")

print meatball.transform_syntax("""
===== Translations =====
* TextFormattingRulesSpanish : Spanish / espanol
* ReglesDeMiseEnPageDesTextes : LangueFrancaise
-----
Simple editing is one of the major benefits of using a wiki.  Users can edit pages without knowing HTML, and still use many formatting features of HTML.  Most wikis define a set of formatting rules to convert plain text into HTML.  Some wikis (like this one) also allow some HTML "tags", like <nowiki><b>, <i>, and <pre></nowiki> within a page.  (Some wikis use raw HTML instead of special formatting rules.)

CategoryTextMarkup

== Overview ==
The following text is an overview of the text formatting rules in effect on this wiki, MeatballWiki.  The [UseMod:TextFormattingRules text formatting rules] for other UseMod wikis may differ.

* Raw HTML is disabled
* Basic Text Formatting
* <b>Bold</b> and <i>Italic</i> Text
* Creating links
** Wiki links
** URL links
** <nowiki>InterWiki</nowiki> links
** Bracketed Links
** Inline images
** ISBN links
** Avoiding auto-links
* Making lists
** bullet lists
## numbered lists
** definition lists
* indenting block quote texts
* Preformatted Text
* Miscellaneous rules

See the TextFormattingExamples for examples without all the explanatory text. To try these rules for yourself, please feel free to edit the SandBox page. <i>To see how any page is formatted, just follow the link "Edit text of this page" at the bottom of the page.</i>  The "Preview" button on the editing page may also be helpful for finding formatting errors before saving.

====== The text on this page is PrimarilyPublicDomain ======

----
== Basic Text Formatting: ==

Most text does not require any special changes for wiki form.  A few basic rules are:
* Do not indent paragraphs with spaces.  (Indenting may cause your text to appear in a monospaced font.)
* Leave a single blank line between paragraphs.
* To create a horizontal line, type 4 or more minus/dash/hyphen (-) characters.
* There is no need to encode HTML characters like <, >, or &.
* HTML-encoded characters like &amp;lt; will not be translated.
* raw HTML is disabled, so don't bother.

----
== Raw HTML is disabled ==

Note that MeatballWiki does not allow raw html in the pages.  The following code will therefore not produce the expected result:

<nowiki>
<nowiki><html><a href="http://www.gnu.org/">gnu</a></html></nowiki>
</nowiki>

Result:

<nowiki><html><a href="http://www.gnu.org/">gnu</a></html></nowiki>

There are some exceptions to this ''no html'' rule detailed below.
----
== Bold and Italic Text: ==

To mark text as <b>bold</b> or <i>italic</i>, you can use the HTML <nowiki><b> and <i></nowiki> tags.  For example:

<pre>
Sample <b>bold</b>, <i>italic</i>, and <b><i>bold+italic</i></b>.
</pre>

looks like:

Sample <b>bold</b>, <i>italic</i>, and <b><i>bold+italic</i></b>.

Note that UseModWiki (like most Wikis) processes pages line-by-line, so if you want three bold lines of text, you will need to use three separate <nowiki><b>...</b></nowiki> tags.  Also note that unclosed or unmatched tags are not removed from the page.

UseModWiki also implements the old "quote style" of text formatting, which is used on several wikis.  Briefly:

<pre>
''Two single quotes are italics'',
'''three single quotes are bold''',
'''''five single quotes are bold and italic.'''''
</pre>

looks like:

''Two single quotes are italics'',
'''three single quotes are bold''',
'''''five single quotes are bold and italic.'''''

The "quote style" formatting is often confusing, especially when multiple bold and italic sections are mixed on a line.  It may eventually be removed from UseModWiki.

----

== Wiki links ==

You can link to a page by removing the spaces between two or more words, and starting each word with a capital letter. For instance, WikiName and TextFormattingExamples are samples of page links.

Non-existing pages, like SampleUndefinedPage, will be displayed with a question-mark for a link. The question mark link indicates the page doesn't exist yet -- follow the link to create and edit the page.  [The sample page used here is a special example page -- you <i>can't</i> define it.]

----
== URL links ==

Write the URL: <nowiki>http://www.usemod.com/cgi-bin/mb.pl?SandBox</nowiki>

Result: http://www.usemod.com/cgi-bin/mb.pl?SandBox

In nearly all cases trailing punctuation is ignored, so you can safely make links like http://www.usemod.com/, without the trailing comma being part of the link.

If the URL itself is long and ugly, you could use a bracketed link.

----
== Bracketed Links ==

Just enclose a URL with square brackets.



The URL will be replaced with a number.  Note that is often considered bad style to replace the name of something (book, author, paper, web site) with the reference in square brackets.  
;Deprecated Example: ''You can read more about this in [1]''.  

If you can't read it out loud, don't write it.  Use the active voice, instead.  
;Example: ''If you are interested in Free Software, check the Philosophy section on the GNU site [1].''

'''Custom Text and Punctuation Links'''

Just follow the URL inside the  square brackets with the text you want to act as the link, like this: <nowiki>[http://www.yahoo.com/ Yahoo Search Engine]</nowiki>






----

== Targeted Links ==

[#N888_7_2_1]
To place a link anchor in a page use [#anchor]"<nowiki>[#anchor]</nowiki>" (without the quotation marks) which can be referred to with any of the linking methods, per the examples below.  You can not use the minus or hypen character (i.e. "-") in the anchor name, e.g. "<nowiki>[#N888_7_2_1]</nowiki>" works ok, while "<nowiki>[#N888-7-2-1]</nowiki>" does not, evidenced non-escaped here->[#N888-7-2-1].

* Wiki link: TextFormattingRules#anchor
* URL link: http://www.usemod.com/cgi-bin/mb.pl?TextFormattingRules#anchor
* Bracketed link:  [http://www.usemod.com/cgi-bin/mb.pl?TextFormattingRules#anchor anchor]
----
== Inline images: ==

Write the URL to the image: <nowiki>http://www.usemod.com/wiki.gif</nowiki>

Result:

http://www.usemod.com/wiki.gif

These file types are recognized: gif, jpg, png, bmp and jpeg

----
== <nowiki>InterWiki</nowiki> links ==

Check the InterMap (http://usemod.com/intermap.txt).  All the prefixes on the intermap can be used to link to pages on other wikis.
Just write the prefix, a colon, and the name of the page on the other wiki like this: <nowiki>UseMod:InterWiki</nowiki>

* What is the license for the InterMap? Can it be used in a GPLed project?

Result: UseMod:InterWiki

----
== ISBN links ==

Just write the ISBN Number, like this:
<nowiki>ISBN 0-471-25311-1</nowiki>

Result: ISBN 0-471-25311-1

----
== Avoiding links ==

If you want to avoid linking, enclose the text with nowiki tags, like this: <nowiki><nowiki>InterWiki</nowiki></nowiki>

Result: <nowiki>InterWiki</nowiki>

You can separate links from adjacent text with spaces or the special "" (two double-quotes) delimiter, like this: <nowiki>UseModWiki""s</nowiki>

Result: UseModWiki""s

The "" delimiter is <i>not</i> displayed -- it is useful for cases like plural forms of page links (such as UseModWiki""s).

----
== Lists: ==

'''Simple lists''':
<pre>
* Text for a bulleted list item.
* Text for another bulleted list item.
* Text for a third bulleted list item.
** Text for second-level list.
*** Text for third level, etc.
</pre>

...which looks like:
* Text for a bulleted list item.
* Text for another bulleted list item.

* Text for a third bulleted list item.
** Text for second-level list.
*** Text for third level, etc.

'''Numbered lists''':
<pre>
# Text for a numbered list item.
# Text for another numbered list item.
# Text for a third numbered list item.
## Text for second-level list.
### Text for third level, etc.
</pre>

...which looks like:
# Text for a numbered list item.
# Text for another numbered list item.
# Text for a third numbered list item.
## Text for second-level list.
### Text for third level, etc.

'''Definition lists'''

Terms with indented definitions: [without a blank line between term and definition]
<pre>
;Term One:Definition for One (indented)
;Term Two:Definition for Two (indented)
;Term Three:Definition for Three (indented)
;;Term (indented):Definition (indented two levels)
;;;Term (indented twice):Definition (indented to third level)
</pre>

...which looks like:
;Term One:Definition for One (indented)
;Term Two:Definition for Two (indented)
;Term Three:Definition for Three (indented)
;;Term (indented):Definition (indented two levels)
;;;Term (indented twice):Definition (indented to third level)

----
== Indented Text: ==

Simple indented text:
<pre>
: Paragraph to be indented (quote-block)
:: Paragraph indented more
::: Paragraph indented to third level
</pre>

...which looks like:
: Paragraph to be indented (quote-block)
:: Paragraph indented more
::: Paragraph indented to third level

----
== Preformatted Text ==

Individual lines can be displayed as preformatted (fixed-width or "typewriter"-font) text by placing one or more spaces at the start of the line.  Other wiki formatting (like links) will be applied to this kind of preformatted text.

<nowiki>Alternatively, multi-line sections can be marked as pre-formatted text with all other formatting suppressed by surrounding the text section with lines starting with <pre> (to start pre-formatted text),  and </pre> (to end preformatted text).  The <pre> and </pre> tags are not displayed.  Wiki links and other formatting is not done within a <pre> formatted section.  (If you want wiki formatting, use spaces at the start of the line instead of the <pre> and </pre> tags.)</nowiki>

For instance:

<pre>
Pre-formatted section here.  No other link
   or format processing
is done on pre-formatted sections.
For instance, UseModWiki is not a link here, and '''this is not bold'''.
</pre>

and:
   This is the starting-spaces version of
   preformatted text.  Note that links like
   UseModWiki still work and '''bolding''' works.

----
----
== Miscellaneous rules: ==

* A line which ends in a backslash character (\) will be joined with the next line before most formatting rules are applied.  This can be useful for breaking up long sections of text in line-sensitive sections (like lists or indented text).
* Most of the formatting rules are order-independent.  On rare occasions the order of processing may be important.  The rules are processed in the following order: raw HTML sections, HTML quoting, nowiki tags, backslash line joining, preformatted sections, paragraphs, lists and indented text, horizontal lines, italic/bold text, URLs, and finally ordinary WikiName links.  [No longer fully accurate for 0.88, needs updating.]

""")