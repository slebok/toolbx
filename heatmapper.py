#!/Users/grammarware/opt/anaconda3/envs/py11/bin/python3
import glob, os

OUTPUT = ''

def process_item(text, ts, in_list):
	if text.find('<T') > -1:
		for x in text.split('<T')[1:]:
			ts.add(x[:2])
	while text.find('<T') > -1:
		parts = text.split('<T')
		parts[1] = '>'.join(parts[1].split('>')[1:])
		text = parts[0] + '<span class="box">' + '<T'.join(parts[1:])
	while text.find('</T') > -1:
		parts = text.split('</T')
		n = parts[1].split('>')[0]
		parts[1] = '>'.join(parts[1].split('>')[1:])
		text = parts[0] + f'</span><sup><span class="Tx"><a href="#T{n}">T{n}</a></span></sup>' + '</T'.join(parts[1:])
	in_list.append(f'<li>{text}</li>\n')

table = []

with open('../cfpbok/SLEBoK.csv', 'r', encoding='utf-8') as csv:
	for line in csv.readlines():
		table.append(line.split(';'))

print(f'CSV with {len(table)} rows and {len(table[-1])} columns found.')

htable = [[f'H<strong><a href="#sle{x}">SLE {x}</a></strong>'] for x in table[1][:]]
htable[0][0] = ''
ts = []

t = 0
for row in table:
	if not row[0].startswith('T'):
		continue
	t += 1
	htable[0].append('H<a href="#{0}"><abbr title="{1}">{0}</abbr></a>'.format(row[0][:3], row[0]))
	ts.append('H<dt><a name="{0}"></a>{0}</dt><dd>{1}</dd>'.format(row[0][:3], row[0][4:]))
	for i in range(1,len(row)):
		if i < len(htable):
			mark = f'<a name="T{t}Y{i+2007}"></a>'
			if row[i].strip():
				htable[i].append(f'Y{mark}<abbr title="{row[i].strip()}">&nbsp;</abbr>')
			else:
				htable[i].append(f'N{mark}')

print(f'Found {t} topics and {i} conferences')
topic_counter = [[0]*i for k in range(0,t)]

OUTPUT = '''<?xml version="1.0" encoding="UTF-8"?>
<!doctype html><html lang="en">
	<head>
		<meta charset="UTF-8" />
		<meta name="viewport" content="initial-scale=1.0"/>
		<title>SLEBoK</title>
		<style>
			td.yes {background-color: darkgreen; color: white;}
			dt {font-weight: bold;}
			dt,dd {display: inline;}
			dd::after {content: "\A"; white-space: pre;}
			.box {text-decoration: underline;}
			span.Tx a {color: green; font-weight: bold;}
		</style>
	</head>
	<body>
'''
# part 1
OUTPUT += '<h1>Topic Table</h1>'
OUTPUT += '<table>'
first_row = True
for row in htable:
	OUTPUT += '<tr>\n'
	first_col = True
	for cell in row:
		call_filled = not cell or cell[0] != 'N'
		if cell:
			cell = cell[1:]
		if call_filled:
			if first_row or first_col:
				OUTPUT += f'<td>{cell}</td>'
			else:
				OUTPUT += f'<td class="yes">{cell}</td>'
		else:
			OUTPUT += f'<td>{cell}</td>'
		first_col = False
	OUTPUT += '\n</tr>'
	first_row = False
OUTPUT += '</table>'
# part 2
OUTPUT += '<h1>Topic List</h1>'
OUTPUT += '<dl>'+ '\n'.join([t[1:] for t in ts]) + '</dl>'
# part 3
# OUTPUT += '<h1>Calls for Papers</h1>'
for dsl in sorted(glob.glob("../cfpbok/*.cfp")):
	year = dsl.split('/')[-1].split('.')[0]
	OUTPUT += f'<h1><a name="sle{year}"></a>SLE {year}</h1>\n'
	OUTPUT += f'<a name="sle{year}topics"></a><a name="sle{year}dblptopics"></a>\n'
	OUTPUT += f'<h2>Call for Papers<a name="sle{year}src"></a></h2>\n'
	in_list = []
	double = False
	ts = set()
	with open(dsl, 'r', encoding='utf-8') as dslf:
		for line in dslf.readlines():
			line = line.strip()
			if not line:
				continue
			if line.startswith('http'):
				OUTPUT = OUTPUT.replace(f'<a name="sle{year}src"></a>', f' (<a href="{line}">source</a>)')
			elif line.startswith('- '):
				if double:
					in_list.append('</ul>\n')
					double = False
				process_item(line[2:], ts, in_list)
			elif line.startswith('-- '):
				if not double:
					in_list.append('<ul>\n')
					double = True
				process_item(line[3:], ts, in_list)
		if double:
			in_list.append('</ul>\n')
		if ts:
			topics = '<h4>Topics requested: '
			for x in sorted(ts):
				topics += f'<span class="Tx"><a href="#T{x}">T{x}</a></span>&nbsp;'
			topics += '</h4>'
			OUTPUT = OUTPUT.replace(f'<a name="sle{year}topics"></a>', topics)
		if in_list:
			OUTPUT += '<ul>\n'
			OUTPUT += '\n'.join(in_list)
			OUTPUT += '</ul>\n'
	dblp = f"../cfpbok/{year}.dblp"
	if os.path.exists(dblp):
		with open(dblp, 'r', encoding='utf-8') as dblpf:
			OUTPUT += f'<h2><a name="sle{year}dblp"></a>List of Papers<a name="sle{year}dblpsrc"></a></h2>'
			ts = set()
			in_list = doing_ts = False
			for line in dblpf.readlines():
				if not line.strip():
					continue
				if line.startswith('https://dblp.org'):
					OUTPUT = OUTPUT.replace(f'<a name="sle{year}dblpsrc"></a>', f' (<a href="{line}">source</a>)')
				elif line.startswith('https://doi.org/'):
					if not in_list:
						OUTPUT += '<ul>\n'
						in_list = True
					elif doing_ts:
						OUTPUT += '</li></ul></li>\n'
						doing_ts = False
					url = line[:line.find(' ')]
					title = line[line.find(' '):].strip()
					OUTPUT += f'<li><em><a href="{url}">{title}</a></em><ul><li>\n'
				else:
					t = line.strip()[:3]
					e = line[line.find(':')+1:].strip()
					OUTPUT += f'<span class="Tx"><a href="#{t}" title="{e}">{t}</a></span>&nbsp;\n'
					ts.add(t)
					# print(t)
					topic_counter[int(t[1:])-1][int(year)-2008] += 1
					doing_ts = True
			if in_list:
				OUTPUT += '</li></ul></li></ul>\n'
			if ts:
				topics = '<h4>Topics received: '
				for x in sorted(ts):
					topics += f'<span class="Tx"><a href="#{x}">{x}</a></span>&nbsp;'
				topics += '</h4>'
				OUTPUT = OUTPUT.replace(f'<a name="sle{year}dblptopics"></a>', topics)
			OUTPUT += '</ul>\n'

for i in range(0, len(topic_counter)):
	for j in range(0, len(topic_counter[i])):
		if topic_counter[i][j] == 0:
			continue
		mark = f'<a name="T{i+1}Y{j+2008}"></a>'
		OUTPUT = OUTPUT.replace(mark, str(topic_counter[i][j]))

OUTPUT += '</body></html>'

with open('test.html', 'w', encoding='utf-8') as html:
	html.write(OUTPUT)
