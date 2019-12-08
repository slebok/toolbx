#!/c/Users/vadim/AppData/Local/Programs/Python/Python37-32/python

import sys, os, glob
import railroader

lang2stmt = {} # L -> S
lang2srcs = {} # L -> text
host2stmt = {} # (H)S -> L.S
stmt2desc = {} # L.S -> D
stmt2fmts = {} # L.S -> BNF
stmt2host = {} # L.S -> (H)S
set_of_used = set() # L.S

gen_tpl1 = '''<?xml version="1.0" encoding="UTF-8"?>
<path css="../www" img="../www"/>
<html doctype>
	<head viewport title="===TITLE===">
	<body>
		<header/>
		<link href="{3}" rel="stylesheet" type="text/css" />
		<img src="{4}" style="width:200px;height:200px;" class="flr" />
		<h1><span class="ff lang"><a href="index.html">{0}</a></span>: ===SUBTITLE===</h1>
		<hr/>
		<h2>Statements:</h2>
		'''
lang_tpl1 = gen_tpl1.replace('===TITLE===', '{0}: the {2} origins').replace('===SUBTITLE===', 'The <span class="ff lang"><a href="{2}.html">{1}</a></span> Origins')
indx_tpl1 = gen_tpl1.replace('===TITLE===', '{0}').replace('===SUBTITLE===', 'The Language Reference')
stmt_tpl1 = gen_tpl1.replace('===TITLE===', '{0}: {1}').replace('===SUBTITLE===', '<span class="ff used"><a href="{2}.html">{1}</a></span>').\
			split('<hr/>')[0] + '{5}'
lang_tpl2 = indx_tpl2 = stmt_tpl5 = '<span class="ff used"><a href="{2}.html" title="{1}">{0}</a></span> '
stmt_tpl2 = '<hr/><h2>Format:</h2>'
stmt_tpl3 = '<h2>Origins:</h2>'
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

def dump_index(f, host, css, logo):
	print('[LDR] dump_index({0}, {1}, {2}, {3})'.format(f.name, host, css, logo))
	f.write(indx_tpl1.format(host, 'ERROR', 'ERROR', css, logo))
	for stmt in sorted(lang2stmt[host]):
		f.write(indx_tpl2.format(stmt, get_desc(host, stmt), name2filename(stmt)))
	f.write('\n<h2>Origins:</h2>')
	for lang in sorted(lang2stmt.keys()):
		if host == lang:
			continue
		f.write(indx_tpl3.format(lang, name2filename(lang)))
	f.write(indx_tpl5.format(host))

def dump_statement(f, host, stmt, css, logo):
	print('[LDR] dump_statement({0}, {1}, {2}, {3}, {4})'.format(f.name, host, stmt, css, logo))
	f.write(stmt_tpl1.format(host, stmt, name2filename(stmt), css, logo, get_desc(host, stmt)))
	f.write(stmt_tpl2)
	fmt = get_fmt(host, stmt)
	if fmt:
		print(fmt)
		if fmt[2][0] == 'size':
			sizes = fmt[2][1].split('x')
			f.write(railroader.svg_head.format(' width="{0}px" height="{1}px"'.format(sizes[0], sizes[1])))
			fmt = fmt[0:1] + fmt[3:]
		else:
			f.write(railroader.svg_head.format(''))
		f.write(railroader.make_diag(fmt, 30))
		f.write(railroader.svg_end)
	if stmt in host2stmt:
		f.write(stmt_tpl3)
		by_lang = {}
		for s in host2stmt[stmt]:
			a,b = s.split('.')
			if a not in by_lang:
				by_lang[a] = set()
			by_lang[a].add(b)
		for k in sorted(by_lang.keys()):
			f.write(stmt_tpl4.format(k, name2filename(k)))
			for s in sorted(by_lang[k]):
				f.write(stmt_tpl5.format(s, get_desc(k, s), name2filename(k)))
			f.write('<br/>')
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
	if key in stmt2desc:
		return stmt2desc[key]
	else:
		return ''

def get_fmt(lang, stmt):
	key = combine(lang, stmt)
	if key in stmt2fmts:
		fmt = stmt2fmts[key]
		bnf = []
		bnf.append(('begin',))
		for w in fmt.split():
			f = fmt2rrd(w)
			bnf.append(f)
		bnf.append(('end',))
		return widen(flatten(bnf))
	else:
		return ()

cache = []
caching = False

def fmt2rrd(w):
	global caching, cache
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
	if w[0] == '"' and w[-1] == '"':
		return [('term', w[1:-1])]
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
	r = []
	last_skip = True
	for x in xs:
		if not last_skip:
			r.append(('skip',))
		r.append(x)
		last_skip = x[0] == 'skip'
	return r

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

# statement CLIST.ATTN became SIGNAL
with open(sys.argv[1], 'r', encoding='utf-8') as ldr:
	for line in ldr.readlines():
		if not line.strip():
			continue
		words = line.strip().split()
		if words[0].startswith('//'):
			continue
		if words[0] == 'summary:':
			stmt2desc[combine(lang, stmt)] = line[8:].strip()
		elif words[0] == 'syntax:':
			stmt2fmts[combine(lang, stmt)] = line[8:].strip()
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
	dump_index(index, host, css, logo)
