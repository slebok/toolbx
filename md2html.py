#!/usr/bin/python3
# -*- coding: utf-8 -*-

import mistune, os

renderer = mistune.Renderer(use_xhtml=True)
markdown = mistune.Markdown(renderer=renderer)

def md2dsl(ifile, ofile, folder):
	slebokroot, purename = ifile.split(folder)
	purename = cleanup_name(purename)
	with open(ifile, 'r', encoding='utf-8') as myinput:
		data = myinput.read()
		title = data.split('\n')[0].strip()
		data = expand_before(data, slebokroot)
		while title.startswith('#'):
			title = title[1:]
		with open(ofile, 'w', encoding='utf-8') as myoutput:
			myoutput.write('''<?xml version="1.0" encoding="UTF-8"?>
<path css="../www" img="../www"/>
<html doctype>
	<head viewport title="SLEBoK: Software Language Engineering Body of Knowledge - {}">
	<body>
		<div style="text-align:center;"><a href="http://slebok.github.io">Software Language Engineering Body of Knowledge</a>: <strong><a href="index.html">{}</a></strong></div>
		<hr/>
		<div class="flr edit">
			<a href="https://github.com/slebok/slebok/edit/master/{}/{}">Edit @ the SLEBoK repo</a>
		</div>'''.format(title, folder, folder, purename))
			myoutput.write(expand_after(markdown(data), slebokroot))
			myoutput.write('''
		<div class="last">
			<br/><hr/>
			The page is generated from <a href="https://github.com/slebok/slebok/blob/master/{}/{}">{}</a>.<br/>
			The website is maintained by <a href="http://grammarware.github.io/">Dr. Vadim Zaytsev</a> a.k.a. @<a href="http://grammarware.net/">grammarware</a>.
			Last updated: #LASTMOD#.
			<valid/>
		</div>
	</body>
</html>'''.format(folder, purename, purename))
	return title.strip()

def expand_before(txt, slebokroot):
	# $[Guy Steele](bibtex:person/Guy L Steele Jr)$
	txtsliced = txt.split('$[')
	if len(txtsliced) > 1:
		txt = txtsliced[0]
		for part in txtsliced[1:]:
			before_dollar = part.split('$')[0]
			after_dollar = part[len(before_dollar) + 1:]
			if before_dollar.endswith(')') and before_dollar.find('](') > -1:
				linktext = before_dollar.split('](')[0]
				target = normalise_link(before_dollar.split('](')[-1].split(')')[0])
				txt += '[{}]({})'.format(linktext, target) + after_dollar
			elif before_dollar.endswith(']'):
				linktext = normalise_text(before_dollar[:-1])
				target = normalise_link(before_dollar[:-1])
				txt += '[{}]({})'.format(linktext, target) + after_dollar
			else:
				# not slebokode anyway
				txt += '$[' + part
	# terms/tools/... linking
	txt = link_terms_tools_etc(txt, slebokroot)
	return txt

def expand_after(txt, slebokroot):
	txt = identify_local_links(txt)
	txt = colour_code(txt)
	txt = slebokode_mark(txt)
	return txt

def normalise_link(link):
	if link.startswith('bibtex:'):
		arg = link[7:]
		return 'http://bibtex.github.io/' + arg + '.html'
	# ...
	return link

# Clean up links like 'bibtex:person/Guy_L_Steele_Jr'
def normalise_text(link):
	return link.split('/')[-1].split(':')[-1].replace('_', ' ')

# Colour up local (= SLEBoK-friendly) links
def identify_local_links(txt):
	# implicitly local links
	bylink = txt.split('href="')
	txt = bylink[0]
	for link in bylink[1:]:
		if link.startswith('http://') or link.startswith('https://') or link.startswith('ftp://'):
			txt += 'href="' + link
		else:
			txt += 'class="local" href="' + link
	# explicit links to SLEBoK projects
	for http in 'http', 'https':
		for friend in 'bibtex.github.io', 'slebok.github.io':
			link = 'href="{}://{}'.format(http, friend)
			txt = txt.replace('<a ' + link, '<a class="local" ' + link)
	return txt

# Simple SLEBoK-specific markdown extensions
def slebokode_mark(txt):
	txt = txt.replace('$/', '<em>').replace('/$', '</em>')
	txt = txt.replace('$*', '<strong>').replace('*$', '</strong>')
	txt = txt.replace('$_', '<sub>').replace('_$', '</sub>')
	txt = txt.replace('$~', '<span class="over">').replace('~$', '</span>')
	txt = txt.replace('--&gt;', '→').replace('&lt;--', '←')
	txt = txt.replace('|-&gt;', ':→') # TODO: mapsto!
	txt = txt.replace('$$', '$')
	return txt

def link_terms_tools_etc(txt, slebokroot):
	print('SLEBoK ROOT is ' + slebokroot)
	parts = txt.split('$@')
	if len(parts) == 1:
		return txt
	txt = parts[0]
	for part in parts[1:]:
		first = part.split('@')[0]
		rest = part[len(first) + 1:]
		if rest.startswith('$'):
			# just $@...@$
			second = first
			rest = rest[1:]
		else:
			second = rest.split('$')[0]
			rest = rest[len(second) + 1:]
		if os.path.exists(os.path.join(slebokroot, 'terms/' + second + '.md')):
			txt += '[{}](../terms/{}.md)'.format(first, second) + rest
		elif os.path.exists(os.path.join(slebokroot, 'tools/' + second + '.md')):
			txt += '[{}](../tools/{}.md)'.format(first, second) + rest
		else:
			txt += '<span class="miss">{}</span>'.format(first) + rest
	return txt

def cleanup_name(name):
	if name.startswith('\\') or name.startswith('/'):
		name = name[1:]
	if name.endswith('\\') or name.endswith('/'):
		name = name[:-1]
	return name

def colour_code(txt):
	CCL = '<code class="lang-'
	parts = txt.split(CCL)
	if len(parts) == 1:
		return txt
	txt = parts[0]
	for part in parts[1:]:
		language = part.split('"')[0]
		proc = determine_language(language)
		if proc is None:
			txt += CCL + part
			continue
		rest = part[len(language) + 2:]
		code = rest.split('</code>')[0]
		rest = rest[len(code):]
		done = []
		for line in code.split('\n'):
			done.append(proc(line))
		txt += CCL + language + '">' + '\n'.join(done) + rest
	return txt

def determine_language(language):
	if language == 'prolog':
		return colour_prolog
	return None

def colour_prolog(line):
	# comments
	pos = line.find('%')
	if pos > -1:
		line = line[:pos] + '<span class="code-cmt">' + line[pos:] + '</span>'
	# define, cut, etc
	for kw in '!', ':-':
		line = line.replace(kw, '<span class="code-kw">' + kw + '</span>')
	return line
