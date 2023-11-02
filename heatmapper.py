#!/Users/grammarware/opt/anaconda3/envs/py11/bin/python3

# T02: Static Semantics;;;;;;;;;Static semantics (e.g., design rules, well-formedness constraints);Static semantics (e.g., design rules, well-formedness constraints);Static semantics (e.g., design rules, well-formedness constraints);Static semantics (e.g., design rules, well-formedness constraints);Static semantics (e.g. design rules, well-formedness constraints);Static semantics (e.g. design rules, well-formedness constraints);Static semantics (e.g. design rules, well-formedness constraints);Static semantics (e.g., design rules, well-formedness constraints)

table = []

with open('../cfpbok/SLEBoK.csv', 'r', encoding='utf-8') as csv:
	for line in csv.readlines():
		table.append(line.split(';'))

print(f'CSV with {len(table)} rows and {len(table[-1])} found.')

htable = [[f'<strong>SLE {x}</strong>'] for x in table[1][:]]
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
			td.yes {background-color: red;}
			dt {font-weight: bold;}
			dt,dd {display: inline;}
			dd::after {content: "\A"; white-space: pre;}
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
	html.write('</body></html>')