#!/usr/bin/python3

import sys, os, glob
import railroader

stmt2thing = {} # thing -> L.S -> D/BNF/...

lang2stmt = {} # L -> S
lang2srcs = {} # L -> text
host2stmt = {} # (H)S -> L.S
stmt2host = {} # L.S -> (H)S
set_of_used = set() # L.S

def h2_of(s, hr=False):
	return '\n' + ('<hr/>' if hr else '') + '<h2>' + s + '</h2>\n'

gen_tpl1 = '''<?xml version="1.0" encoding="UTF-8"?>
<path css="../www" img="../www"/>
<html doctype>
	<head viewport title="===TITLE===">
	<body>
		<header/>
		<link href="{3}" rel="stylesheet" type="text/css" />
		<img src="{4}" style="width:200px;height:200px;" class="flr" />
		<h1><span class="ff lang"><a href="index.html">{0}</a></span>: ===SUBTITLE===</h1>
		===TEXT===<hr/>
		<h2>Features:</h2>
		'''
lang_tpl1 = gen_tpl1.\
			replace('===TITLE===', '{0}: the {2} origins').\
			replace('===SUBTITLE===', 'The <span class="ff lang"><a href="{2}.html">{1}</a></span> Origins').\
			replace('===TEXT===', '')
indx_tpl1 = gen_tpl1.\
			replace('===TITLE===', '{0}').\
			replace('===SUBTITLE===', 'The Language Reference').\
			replace('===TEXT===', '{1}')
stmt_tpl1 = gen_tpl1.\
			replace('===TITLE===', '{0}: {1}').\
			replace('===TEXT===', '').\
			replace('===SUBTITLE===', '<span class="ff used"><a href="{2}.html">{1}</a></span>').\
			split('<hr/>')[0] + '{5}'
lang_tpl2 = indx_tpl2 = stmt_tpl5 = '<span class="ff used"><a href="{2}.html" title="{1}">{0}</a></span> '
lang_tpl3 = '<span class="ff" title="{1}">{0}</span> '
indx_tpl3 = stmt_tpl4 = '<span class="ff lang"><a href="{1}.html">{0}</a></span>&nbsp;&nbsp;&nbsp;'
lang_tpl4 = '''
		<h2>Sources:</h2>
		<ul>
			<li>{0}</li>
		</ul>'''
lang_tpl5 = indx_tpl5 = '''
		<hr/>
		<div class="last">
			{0} is a project by <a href="http://grammarware.github.io/">Dr. Vadim Zaytsev</a> a.k.a. @<a href="http://grammarware.net/">grammarware</a>.
			Page last updated in #LASTMOD#.
			<valid/>
		</div>
	</body>
</html>'''

def dump_index(f, host, css, logo, welcome, pubs):
	print('[LDR] dump_index({0}, {1}, {2}, {3})'.format(f.name, host, css, logo))
	f.write(indx_tpl1.format(host, welcome, 'ERROR', css, logo))
	for stmt in sorted(lang2stmt[host]):
		f.write(indx_tpl2.format(stmt, get_desc(host, stmt), name2filename(stmt)))
	f.write(h2_of('Origins'))
	for lang in sorted(lang2stmt.keys()):
		if host == lang:
			continue
		f.write(indx_tpl3.format(lang, name2filename(lang)))
	f.write(h2_of('Mentions'))
	f.write('<ul>')
	for p in pubs:
		f.write('<li>' + p + '</li>\n')
	f.write('</ul>')
	f.write(indx_tpl5.format(host))

def dump_statement(f, host, stmt, css, logo):
	print('[LDR] dump_statement({0}, {1}, {2}, {3}, {4})'.format(f.name, host, stmt, css, logo))
	f.write(stmt_tpl1.format(host, stmt, name2filename(stmt), css, logo, get_desc(host, stmt)))
	f.write(h2_of('Format', hr=True))
	fmt = get_fmt(host, stmt)
	if fmt:
		# print(fmt)
		if fmt[0][0] == 'size':
			sizes = [0,0]
			sizes[0] = int(fmt[0][1][:-1]) * railroader.HOR_STEP
			if fmt[0][1][-1] == '.':
				sizes[1] = 3 * railroader.HOR_STEP
			elif fmt[0][1][-1] == ':':
				sizes[1] = 4 * railroader.HOR_STEP
			elif fmt[0][1][-1] == ',':
				sizes[1] = 5 * railroader.HOR_STEP
			elif fmt[0][1][-1] == '\\':
				sizes[1] = 6 * railroader.HOR_STEP
			elif fmt[0][1][-1] == '⇓':
				sizes[1] = 10 * railroader.HOR_STEP
			else:
				print('[ERR] unrecognised format: ' + fmt[0][1][-1])
			f.write(railroader.svg_head.format(' width="{0}px" height="{1}px"'.format(sizes[0], sizes[1])))
			# fmt = fmt[1:]
		else:
			f.write(railroader.svg_head.format(''))
		f.write(railroader.make_diag(fmt, 30))
		f.write(railroader.svg_end)
	for metakey in stmt2thing:
		if metakey in ('format', 'summary'):
			continue
		if combine(host, stmt) in stmt2thing[metakey]:
			f.write(h2_of(metakey[0].upper() + metakey[1:]))
			f.write(stmt2thing[metakey][combine(host, stmt)])
	key = stmt.replace(' ', '_')
	if key in host2stmt:
		f.write(h2_of('Origins'))
		by_lang = {}
		# print('$$$')
		# print(host2stmt)
		for s in host2stmt[key]:
			a,b = s.split('.')
			if a not in by_lang:
				by_lang[a] = set()
			by_lang[a].add(b)
		for k in sorted(by_lang.keys()):
			f.write(stmt_tpl4.format(k, name2filename(k)))
			for s in sorted(by_lang[k]):
				f.write(stmt_tpl5.format(s, get_desc(k, s), name2filename(k)))
			f.write('<br/>')
	else:
		print('[WARN] Statement {0} not found in the host language!'.format(stmt))
	f.write(indx_tpl5.format(host))

def dump_language(f, host, lang, css, logo):
	print('[LDR] dump_language({0}, {1}, {2}, {3}, {4})'.format(f.name, host, lang, css, logo))
	f.write(lang_tpl1.format(host, lang, name2filename(lang), css, logo))
	for stmt in sorted(lang2stmt[lang]):
		if if_used(lang, stmt):
			target = combine(lang, stmt)
			if target in stmt2host:
				target = stmt2host[target]
			else:
				target = stmt
				print('[LDR] Does not work for {0} in {1}'.format(stmt, stmt2host.keys()))
			f.write(lang_tpl2.format(stmt, get_desc(lang, stmt), name2filename(target)))
		else:
			f.write(lang_tpl3.format(stmt, get_desc(lang, stmt)))
	if lang in lang2srcs:
		f.write(lang_tpl4.format(lang2srcs[lang]))
	f.write(lang_tpl5.format(host))

def combine(lang, stmt):
	return '{0}.{1}'.format(lang, stmt)

def get_desc(lang, stmt):
	key = combine(lang, stmt)
	if key in stmt2thing['summary']:
		return stmt2thing['summary'][key]
	else:
		return ''

def get_fmt(lang, stmt):
	key = combine(lang, stmt)
	if key in stmt2thing['format']:
		fmt = stmt2thing['format'][key]
		bnf = []
		for w in fmt.split():
			if w[0] == '@':
				return () # ignore old style
			f = fmt2rrd(w)
			bnf.append(f)
		return widen(flatten(bnf))
	else:
		return ()

cache = []
caching = False

def fmt2rrd(w):
	global caching, cache
	if w == '>>':
		return [('begin',)]
	elif w == '><':
		return [('end',)]
	elif w[0] == '-':
		if len(w) == 1:
			return [('skip',)]
		else:
			return [('skip', int(w[1:]))]
	elif w[0] == '#':
		return [('save', w[1:])]
	elif w[0] == '&':
		return [('load', w[1:])]
	elif w[0] == '\\':
		if len(w) == 1:
			return [('downbranch',)]
		else:
			return [('downbranch', int(w[1:]))]
	elif w[0] == '/':
		if len(w) == 1:
			return [('backbranch',)]
		else:
			return [('backbranch', int(w[1:]))]
	elif w[0] == '"' and w[-1] == '"':
		width = railroader.len_text_in_px(w[1:-1])
		while width % 20 != 0:
			width += 1
		return [('term', w[1:-1], int(width/20))]
	elif w[0] == '^':
		return [('uploop', int(w[1:]))]
	elif w[0] == '$':
		return [('cr', int(w[1:]))]
	elif w[0] == '[' and w[-1] == ']':
		return [('size', w[1:-1])]
	else:
		width = railroader.len_text_in_px(w)
		while width % 20 != 0:
			width += 1
		return [('nt', w, int(width/20))]


	if w[0] == '@':
		return [('size', w[1:])]
	if caching:
		if w == ')?':
			caching = False
			return [('optional', widen(flatten([fmt2rrd(x) for x in cache])))]
		if w == ')*':
			caching = False
			return [('downloop', widen(flatten([fmt2rrd(x) for x in cache])))]
		if w == ')+':
			caching = False
			r = flatten([fmt2rrd(x) for x in cache])
			r.append(('uploop', railroader.len_seq_in_px(r)))
			r.insert(0, ('skip',))
			return r
		cache.append(w)
		return []
	if w == '(':
		caching = True
		cache = []
		return []
	if w[-1] == '+':
		return [('skip',), fmt2rrd(w[:-1]), ('uploop', railroader.len_text_in_px(w[:-1])), ('skip' ,)]
	return [('nt', w)]

def flatten(xs):
	r = []
	for x in xs:
		if type(x) == type([]):
			for y in flatten(x):
				r.append(y)
		else:
			r.append(x)
	return r

def widen(xs):
	return xs

def add_used(lang, stmt, hoststmt):
	key = combine(lang, stmt)
	set_of_used.add(key)
	if hoststmt not in host2stmt:
		host2stmt[hoststmt] = set()
	host2stmt[hoststmt].add(key)
	stmt2host[key] = hoststmt

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

def name2filename(lang):
	return lang.lower().replace(' ', '').replace('_', '').replace('/', '')

pubs = []
# statement CLIST.ATTN became SIGNAL
with open(sys.argv[1], 'r', encoding='utf-8') as ldr:
	lines = ldr.readlines()
	cx = -1
	while cx+1 < len(lines):
		cx += 1
		line = lines[cx]
		if not line.strip():
			continue
		words = line.strip().split()
		if words[0].startswith('//'):
			continue
		if words[0].startswith('@@'):
			fn = os.path.join(os.path.dirname(sys.argv[1]), line.strip()[2:])
			with open(fn, 'r', encoding='utf-8') as ldr2:
				lines[cx+2:cx+2] = ldr2.readlines()
				print('imported LDR {0} to {1}'.format(fn,str(len(lines))))
			continue
		if words[0][-1] == ':':
			thing = words[0][:-1]
			if thing not in stmt2thing:
				stmt2thing[thing] = {}
			content = line[len(thing)+2:].strip()
			if content == '<ul>':
				cx += 1
				line = lines[cx].strip()
				while line != '</ul>':
					if line.startswith('* '):
						line = line[2:]
					if not (line.startswith('<!--') or (line.startswith('<li>') and line.startswith('<li>'))):
						line = '<li>' + line + '</li>'
					content += line
					cx += 1
					line = lines[cx].strip()
				content += line
			stmt2thing[thing][combine(lang, stmt)] = content
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
				add_used(lang, stmt, words[3])
			elif len(words) == 2:
				lang, stmt = break_up(words[1], '')
				if lang not in lang2stmt:
					lang2stmt[lang] = set()
				lang2stmt[lang].add(stmt)
			else:
				print('[LDR] Unexpected: ' + line)
		elif len(words)>1 and (words[1] == 'is' or words[1] == 'was'):
			if words[0] == 'this':
				host = words[2]
			elif words[0] == 'CSS':
				css = words[2]
			elif words[0] == 'logo':
				logo = words[2]
			elif words[0] == 'welcome':
				welcome = line.strip()[11:]
			else:
				print('[LDR] Unexpected: ' + line)
		elif words[0] == 'seen' and words[1] == 'at':
			pubs.append(line.strip()[8:])
		elif words[0] == 'source' and words[2] == 'is':
			lang2srcs[words[1]] = line[line.index(' is ')+3:].strip()
		else:
			print('[LDR] Unexpected: ' + line)
# languages
for lang in lang2stmt.keys():
	if host == lang:
		continue
	print('[LDR] lang2stmt[{0}]'.format(lang))
	with open(sys.argv[2] + name2filename(lang) + '.dsl', 'w', encoding='utf-8') as langfile:
		dump_language(langfile, host, lang, css, logo)
# all statements
for stmt in lang2stmt[host]:
	print('[LDR] host2stmt[{0}]'.format(stmt))
	with open(sys.argv[2] + name2filename(stmt) + '.dsl', 'w', encoding='utf-8') as stmtfile:
		dump_statement(stmtfile, host, stmt, css, logo)
# host language file
with open(sys.argv[2] + 'index.dsl', 'w', encoding='utf-8') as index:
	dump_index(index, host, css, logo, welcome, pubs)
