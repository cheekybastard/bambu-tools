from pyquery import PyQuery
from html2text import HTML2Text
from markdown import markdown as md

UNCLEAN_TAGS = (
	'audio', 'video', 'iframe', 'object', 'form', 'input', 'select', 'textarea', 'script', 'style'
)

UNCLEAN_ATTRS = (
	'onafterprint', 'onbeforeprint', 'onbeforeunloa', 'onerro', 'onhaschange', 'onload', 'onmessageNew',
	'onoffline', 'ononline', 'onpagehide', 'onpageshow', 'onpopstate', 'onredo', 'onresize', 'onstorage', 'onundo',
	'onunload'
)

def sanitise(text, markdown = False):
	if markdown:
		text = md(text)
	
	dom = PyQuery(text)
	
	for a in dom.find('a[href^="javascript:"]'):
		a = PyQuery(a)
		a.replaceWith(a.text())
	
	for obj in UNCLEAN_TAGS:
		dom.find(obj).remove()
	
	for attr in UNCLEAN_ATTRS:
		dom.find('[%s]' % attr).removeAttr(attr)
	
	text = dom.outerHtml()
	if markdown:
		dom = HTML2Text()
		text = dom.handle(text)
	
	return text