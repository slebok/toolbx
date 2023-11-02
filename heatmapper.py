#!/Users/grammarware/opt/anaconda3/envs/py11/bin/python3
import glob

# T02: Static Semantics;;;;;;;;;Static semantics (e.g., design rules, well-formedness constraints);Static semantics (e.g., design rules, well-formedness constraints);Static semantics (e.g., design rules, well-formedness constraints);Static semantics (e.g., design rules, well-formedness constraints);Static semantics (e.g. design rules, well-formedness constraints);Static semantics (e.g. design rules, well-formedness constraints);Static semantics (e.g. design rules, well-formedness constraints);Static semantics (e.g., design rules, well-formedness constraints)

table = []

with open('../cfpbok/SLEBoK.csv', 'r', encoding='utf-8') as csv:
	for line in csv.readlines():
		table.append(line.split(';'))

print(f'CSV with {len(table)} rows and {len(table[-1])} found.')

htable = [[f'<strong><a href="#sle{x}">SLE {x}</a></strong>'] for x in table[1][:]]
htable[0][0] = ''
ts = []

t = 0
for row in table:
	if not row[0].startswith('T'):
		continue
	t += 1
	htable[0].append('<a href="#{0}"><abbr title="{1}">{0}</abbr></a>'.format(row[0][:3], row[0]))
	ts.append('<dt><a name="{0}"></a>{0}</dt><dd>{1}</dd>'.format(row[0][:3], row[0][4:]))
	for i in range(1,len(row)):
		if i < len(htable):
			if row[i].strip():
				htable[i].append(f'<abbr title="{row[i].strip()}">&nbsp;</abbr>')
			else:
				htable[i].append('')

with open('test.html', 'w', encoding='utf-8') as html:
	html.write('''<?xml version="1.0" encoding="UTF-8"?>
<!doctype html><html lang="en">
	<head>
		<meta charset="UTF-8" />
		<meta name="viewport" content="initial-scale=1.0"/>
		<title>SLEBoK</title>
		<style>
			td.yes {background-color: darkgreen;}
			dt {font-weight: bold;}
			dt,dd {display: inline;}
			dd::after {content: "\A"; white-space: pre;}
			.box {text-decoration: underline;}
			span.Tx a {color: green; font-weight: bold;}
		</style>
	</head>
	<body>''')
	# part 1
	html.write('<h1>Topic Table</h1>')
	html.write('<table>')
	first_row = True
	for row in htable:
		html.write('<tr>\n')
		first_col = True
		for cell in row:
			if cell:
				if first_row or first_col:
					html.write(f'<td>{cell}</td>')
				else:
					html.write(f'<td class="yes">{cell}</td>')
			else:
				html.write('<td></td>')
			first_col = False
		html.write('\n</tr>')
		first_row = False
	html.write('</table>')
	# part 2
	html.write('<h1>Topic List</h1>')
	html.write('<dl>'+ '\n'.join(ts) + '</dl><br/>')
	# part 3
	html.write('<h1>Calls for Papers</h1>')
	for dsl in sorted(glob.glob("../cfpbok/*.cfp")):
		year = dsl.split('/')[-1].split('.')[0]
		html.write(f'<h2><a name="sle{year}"></a>SLE {year} Topics</h2>')
		in_list = False
		with open(dsl, 'r', encoding='utf-8') as dslf:
			for line in dslf.readlines():
				line = line.strip()
				if not line:
					continue
				if line.startswith('http'):
					html.write('<h6><a href="{line}">Source</a></h6>\n')
				elif line.startswith('- '):
					if not in_list:
						in_list = True
						html.write('<ul>')
					text = line[2:]
					while text.find('<T') > -1:
						parts = text.split('<T')
						parts[1] = '>'.join(parts[1].split('>')[1:])
						text = parts[0] + '<span class="box">' + '<T'.join(parts[1:])
					while text.find('</T') > -1:
						parts = text.split('</T')
						n = parts[1].split('>')[0]
						parts[1] = '>'.join(parts[1].split('>')[1:])
						text = parts[0] + f'</span><sup><span class="Tx"><a href="#T{n}">T{n}</a></span></sup>' + '</T'.join(parts[1:])
					html.write(f'<li>{text}</li>\n')
			if in_list:
				html.write('</ul>\n')


	html.write('</body></html>')