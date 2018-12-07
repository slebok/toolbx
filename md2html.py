#!/c/Users/vadim/AppData/Local/Programs/Python/Python35/python
# -*- coding: utf-8 -*-

import mistune

renderer = mistune.Renderer(use_xhtml=True)
markdown = mistune.Markdown(renderer=renderer)

def md2dsl(ifile, ofile):
	purename = ifile.split('stories')[-1]
	if purename.startswith('\\') or purename.startswith('/'):
		purename = purename[1:]
	with open(ifile, 'r', encoding='utf-8') as myinput:
		data = myinput.read()
		title = data.split('\n')[0].strip()
		while title.startswith('#'):
			title = title[1:]
		with open(ofile, 'w', encoding='utf-8') as myoutput:
			myoutput.write('''<?xml version="1.0" encoding="UTF-8"?>
<path css="../www" img="../www"/>
<html doctype>
	<head viewport title="SLEBOK: Software Language Engineering Body of Knowledge - {}">
	<body>
		<div style="text-align:center;"><a href="http://slebok.github.io">Software Language Engineering Body of Knowledge</a></div>
		<hr/>
		<div class="flr edit">
			<a href="https://github.com/slebok/slebok/edit/master/stories/{}">Edit @ the SLEBoK repo</a>
		</div>'''.format(title, purename))
			myoutput.write(expand_extensions(markdown(data)))
			myoutput.write('''
		<div class="last">
			<br/><hr/>
			Story generated from <a href="https://github.com/slebok/slebok/blob/master/stories/{}">{}</a>.<br/>
			The website is maintained by <a href="http://grammarware.github.io/">Dr. Vadim Zaytsev</a> a.k.a. @<a href="http://grammarware.net/">grammarware</a>.
			Last updated: #LASTMOD#.
			<valid/>
		</div>
	</body>
</html>'''.format(purename, purename))
	return title.strip()

def expand_extensions(txt):
	txt = txt.replace('$_', '<sub>').replace('_$', '</sub>')
	txt = txt.replace('$~', '<span class="over">').replace('~$', '</span>')
	txt = txt.replace('--&gt;', '→').replace('&lt;--', '←')
	txt = txt.replace('$$', '$')
	return txt