#!/c/Users/vadim/AppData/Local/Programs/Python/Python37-32/python

import sys, os, glob

lang2stmt = {} # L -> S
lang2srcs = {} # L -> text
host2stmt = {} # (H)S -> L.S
stmt2desc = {} # L.S -> D
set_of_used = set() # L.S

lang_tpl1 = '''<?xml version="1.0" encoding="UTF-8"?>
<path css="../www" img="../www"/>
<html doctype>
	<head viewport title="BabyCOBOL: the CLIST origins">
	<body>
		<header/>
		<link href="{2}" rel="stylesheet" type="text/css" />
		<img src="{3}" style="width:200px;height:200px;" class="flr" />
		<h1><a href="index.html">{0}</a>: The {1} Origins</h1>
		<hr/>
		<h2>Statements:</h2>
		'''
lang_tpl2 = '<span class="stmt{2}"><a href="{1}.html" title="{3}">{0}</a></span> '
lang_tpl3 = '''
		<h2>Sources:</h2>
		<ul>
			<li>{0}</li>
		</ul>'''
lang_tpl4 = '''
		<hr/>
		<div class="last">
			{0} is a project by <a href="http://grammarware.github.io/">Dr. Vadim Zaytsev</a> a.k.a. @<a href="http://grammarware.net/">grammarware</a>.
			Page last updated in #LASTMOD#.
			<valid/>
		</div>
	</body>
</html>'''

def dump_language(f, host, lang, css, logo, stmts):
	print('[LDR] dump_language({0}, {1})'.format(f.name, stmts))
	f.write(lang_tpl1.format(host, lang, css, logo))
	for stmt in sorted(stmts):
		f.write(lang_tpl2.format(stmt, lang2filename(stmt), ' used' if if_used(lang, stmt) else '', get_desc(lang, stmt)))
	if lang in lang2srcs:
		f.write(lang_tpl3.format(lang2srcs[lang]))
	f.write(lang_tpl4.format(host))

def combine(lang, stmt):
	return '{0}.{1}'.format(lang, stmt)

def get_desc(lang, stmt):
	key = combine(lang, stmt)
	if key in stmt2desc:
		return stmt2desc[key]
	else:
		return ''

def add_used(lang, stmt):
	key = combine(lang, stmt)
	set_of_used.add(key)

def if_used(lang, stmt):
	key = combine(lang, stmt)
	return key in set_of_used

def break_up(w1, w3):
	essence = w1.split('.')
	if len(essence) == 2:
		return essence[0].replace('_', ' '), essence[1].replace('_', ' ')
	elif len(essence) == 1:
		# default statement name
		return essence[0].replace('_', ' '), w3.replace('_', ' ')
	else:
		print('[LDR] Unexpected: ' + line)
		return '', ''

def lang2filename(lang):
	return lang.lower().replace(' ', '').replace('_', '')

# statement CLIST.ATTN became SIGNAL
with open(sys.argv[1], 'r', encoding='utf-8') as ldr:
	for line in ldr.readlines():
		if not line.strip():
			continue
		words = line.strip().split()
		if words[0] == 'summary:':
			stmt2desc[combine(lang, stmt)] = line[8:].strip()
		elif words[0] == 'statement':
			if len(words) == 4:
				if words[2] != 'became':
					print('[LDR] Unexpected: ' + line)
					continue
				lang, stmt = break_up(words[1], words[3])
				if lang not in lang2stmt:
					lang2stmt[lang] = set()
				lang2stmt[lang].add(stmt)
				if stmt not in host2stmt:
					host2stmt[stmt] = set()
				add_used(lang, stmt)
			elif len(words) == 2:
				lang, stmt = break_up(words[1], '')
				if lang not in lang2stmt:
					lang2stmt[lang] = set()
				lang2stmt[lang].add(stmt)
			else:
				print('[LDR] Unexpected: ' + line)
		elif words[1] == 'is':
			if words[0] == 'this':
				host = words[2]
			elif words[0] == 'CSS':
				css = words[2]
			elif words[0] == 'logo':
				logo = words[2]
			else:
				print('[LDR] Unexpected: ' + line)
		elif words[0] == 'source' and words[2] == 'is':
			lang2srcs[words[1]] = line[line.index(' is ')+3:].strip()
		else:
			print('[LDR] Unexpected: ' + line)
# languages
for lang in lang2stmt.keys():
	print('[LDR] lang2stmt[{0}]'.format(lang))
	with open(sys.argv[2] + lang2filename(lang) + '.dsl', 'w', encoding='utf-8') as langfile:
		dump_language(langfile, host, lang, css, logo, lang2stmt[lang])
# all statements
for stmt in host2stmt.keys():
	pass

# host language file


