#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

table = \
{\
	'%27': '’',
	'%C3%89': 'É',
	'%C3%A8': 'è',
	'%C3%AD': 'í',
	'%C3%B6': 'ö',
	'%C3%B8': 'ø',
	'%C3%BC': 'ü',
	'%C4%9B': 'ě',
	'%C5%82': 'ł',
	'%C5%AF': 'ů',
	'%E2%80%93': '–',
	'_': ' ',
}

def last(s):
	return s.strip().split(' ')[-1]

def unpuzzle(code):
	llink = lname = ''
	if code.find('|||') > -1:
		llink, lname = code.split('|||')
	elif code.startswith('http'):
		llink = code
		lname = code.split('/')[-1].split('#')[-1]
		if code.find('dblp.org') > -1:
			names = []
			for name in lname.replace('=', '.').replace(':', '_').split('_'):
				if not name.isdigit():
					names.append(name)
			lname = ' '.join(names[1:]) + ' ' + names[0]
	else:
		lname = code
	if lname.endswith(')'):
		lname = lname.split('(')[0]
	for k in table.keys():
		lname = lname.replace(k, table[k])
	return lname, llink

def linkify(nl):
	n, l = nl
	if l:
		return '<a href="{}">{}</a>'.format(l, n)
	else:
		return n


with open('../toolkit/credit.txt', 'r', encoding='utf-8') as myinput:
	with open('credit/index.dsl', 'w', encoding='utf-8') as bything:
		with open('credit/index-name.dsl', 'w', encoding='utf-8') as byname:
			header = '''<?xml version="1.0" encoding="UTF-8"?>
<path css="../www" img="../www"/>
<html doctype>
	<head viewport title="SLEBoK - Credit Where Credit's Due">
	<body>
		<div style="text-align:center;"><a href="http://slebok.github.io">Software Language Engineering Body of Knowledge</a></div>
		<hr/>
		<h1>Credit</h1>
		<p>
			<a href="http://slebok.github.io/credit/">Credit</a> is a project to collect <em>named</em>
			theorems, notations, languages, algorithms, etc, in software (language) engineering with
			attributions to the people after which they were named.
		</p>
		<h2>
			Full list:
			<a href="index.html">sorted by contribution</a> •
			<a href="index-name.html">sorted by name</a>
		</h2>
		<table class="border">'''
			bything.write(header)
			byname.write(header)
			lines = [line.strip() for line in myinput.readlines()]
			lno = 0
			links = {}
			map1 = {}
			map2 = {}
			while lno < len(lines):
				bareterm = unpuzzle(lines[lno])
				links[bareterm[0]] = linkify(bareterm)
				bareterm = bareterm[0]
				lno += 1
				credit = []
				while lno < len(lines) and lines[lno]:
					credit.append(unpuzzle(lines[lno]))
					lno += 1
				if bareterm not in map1.keys():
					map1[bareterm] = []
				for c in credit:
					links[c[0]] = linkify(c)
					map1[bareterm].append(c[0])
					if c[0] not in map2.keys():
						map2[c[0]] = []
					map2[c[0]].append(bareterm)
				# creditstr = '<br/>'.join(map(linkify, credit))
				# olines1[bareterm] = '<tr><td>{}</td><td>{}</td></tr>'.format(term, creditstr)
				lno += 1
			for key in sorted(map1.keys()):
				col2 = '<br/>'.join(map(lambda k: links[k], map1[key]))
				oline = '<tr><td>{}</td><td>{}</td></tr>\n'.format(links[key], col2)
				bything.write(oline)
			for key in sorted(map2.keys(), key = last):
				col2 = '<br/>'.join(map(lambda k: links[k], map2[key]))
				oline = '<tr><td>{}</td><td>{}</td></tr>\n'.format(links[key], col2)
				byname.write(oline)
			footer = '''
		</table>
		<div class="last">
			<br/><hr/>
			The page is generated from <a href="https://github.com/slebok/toolbx/blob/master/credit.txt">@slebok/toolbx/credit.txt</a>.<br/>
			The website is maintained by <a href="http://grammarware.github.io/">Dr. Vadim Zaytsev</a> a.k.a. @<a href="http://grammarware.net/">grammarware</a>.
			Last updated: #LASTMOD#.
			<valid/>
		</div>
	</body>
</html>'''
			bything.write(footer)
			byname.write(footer)
