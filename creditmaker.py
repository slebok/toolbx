#!/c/Users/vadim/AppData/Local/Programs/Python/Python35/python
# -*- coding: utf-8 -*-

import os

table = \
{\
	'%27': '’',
	'%C3%89': 'É',
	'%C3%A8': 'è',
	'%C3%AD': 'í',
	'%C3%B6': 'ö',
	'%C4%9B': 'ě',
	'%C5%82': 'ł',
	'%C5%AF': 'ů',
	'%E2%80%93': '–',
	'_': ' ',
}

def unpuzzle(code):
	llink = lname = ''
	if code.find('|||') > -1:
		llink, lname = code.split('|||')
	elif code.startswith('http'):
		llink = code
		lname = code.split('/')[-1].split('#')[-1]
		if code.find('dblp.org') > -1:
			names = lname.split(':')
			names.reverse()
			lname = ' '.join(names)
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
	with open('credit/index.dsl', 'w', encoding='utf-8') as myoutput:
		myoutput.write('''<?xml version="1.0" encoding="UTF-8"?>
<path css="../www" img="../www"/>
<html doctype>
	<head viewport title="SLEBoK - Credit Where Credit's Due">
	<body>
		<div style="text-align:center;"><a href="http://slebok.github.io">Software Language Engineering Body of Knowledge</a></div>
		<hr/>
		<table class="border">''')
		lines = [line.strip() for line in myinput.readlines()]
		lno = 0
		olines = {}
		while lno < len(lines):
			bareterm = unpuzzle(lines[lno])
			term = linkify(bareterm)
			bareterm = bareterm[0]
			lno += 1
			credit = []
			while lno < len(lines) and lines[lno]:
				credit.append(linkify(unpuzzle(lines[lno])))
				lno += 1
			credit = '<br/>'.join(credit)
			olines[bareterm] = '<tr><td>{}</td><td>{}</td></tr>'.format(term, credit)
			lno += 1
		for line in sorted(olines.keys()):
			myoutput.write(olines[line] + '\n')
		myoutput.write('''
		</table>
		<div class="last">
			<br/><hr/>
			The page is generated from <a href="https://github.com/slebok/toolkit/blob/master/credit.txt">@slebok/toolkit/credit.txt</a>.<br/>
			The website is maintained by <a href="http://grammarware.github.io/">Dr. Vadim Zaytsev</a> a.k.a. @<a href="http://grammarware.net/">grammarware</a>.
			Last updated: #LASTMOD#.
			<valid/>
		</div>
	</body>
</html>''')
