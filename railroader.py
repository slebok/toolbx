#!/c/Users/vadim/AppData/Local/Programs/Python/Python37-32/python

HOR_STEP = 20
saved = {}

svg_head = '''
<svg xmlns="http://www.w3.org/2000/svg"{0}>
	<defs>
		<style type="text/css">
			@namespace "http://www.w3.org/2000/svg";
			svg {{background-color: white;}}
			path {{fill: none; stroke: black;}}
			polygon {{fill: black; stroke: black;}}
			text {{font-size:16px;fill:black;font-weight:bold;font-family:monospace;}}
			text.i {{font-style:italic;}}
		</style>
	</defs>'''
svg_end = '\n</svg>\n'

def len_text_in_px(s):
	return int(len(s)*9) + int(len(s) / 10)*10

def len_seq_in_px(xs):
	global HOR_STEP
	cx = 0
	for x in xs:
		if x[0] == 'skip':
			cx += HOR_STEP
		elif x[0] == 'term' or x[0] == 'nt':
			cx += len_text_in_px(x[1])
	return cx

def make_triangle(x, y, right=False, left=False, down=False, up=False):
	# x is 33 vertical
	# y is 9
	if left or right:
		mod = 8 if left else -8
		return '<polygon points="{0} {2} {1} {3} {1} {4}"/>'.format(x, x+mod, y, y-4, y+4)
	elif down or up:
		mod = 8 if up else -8
		return '<polygon points="{0} {3} {1} {4} {2} {4}"/>'.format(x, x-4, x+4, y, y+mod)

def make_loop(x, y, height, dx):
	r = '<path d="M {0} {1} v -{2} h -{3} v {2}"/>'.format(x, y, height, dx)
	r += make_triangle(x-dx, y-1, down=True)
	return r

def make_step_down(x, y, height, dx):
	r = '<path d="M {0} {1} v {2} h {3}"/>'.format(x, y, height, dx)
	return r

def make_step_back_up(x, y, height, dx):
	r = '<path d="M {0} {1} h {3} v -{2}"/>'.format(x, y, height, dx)
	r += make_triangle(x+dx, y-height+1, up=True)
	return r

def make_line(x, y, dx=None, dy=None):
	d = ' '
	if dx:
		d += 'h {0} '.format(dx)
	if dy:
		d += 'v {0} '.format(dy)
	return '<path d="M {0} {1} {2}"/>'.format(x, y, d.strip())

def make_text(x, y, txt, nt=False):
	# print('[{0}]: [{1}]'.format(txt,len_text_in_px(txt) % 20))
	if len_text_in_px(txt) % 20 != 0 and len_text_in_px(txt) % 20 < 10:
		txt = '&nbsp;' + txt
	s = ' class="i"' if nt else ''
	return '<text{3} x="{0}" y="{1}">{2}</text>'.format(x, y+4, txt, s)

def make_diag(dspec, y, x=HOR_STEP):
	global HOR_STEP, saved
	res = []
	res.append('\n<!-- {0} -->\n'.format(dspec))
	for d in dspec:
		if type(d) == type([]):
			for r in make_diag(d, y):
				res.append(r)
		elif d[0] == 'cr':
			x = HOR_STEP
			y += int(HOR_STEP*d[1])
		elif d[0] == 'size':
			a,b,c = d[1].split(':')
			if c:
				y += int(HOR_STEP/2) * int(c)
		elif d[0] == 'save':
			saved[d[1]] = (x,y)
		elif d[0] == 'load':
			if d[1] in saved:
				x, y = saved[d[1]]
			else:
				print('[LOAD] Cannot load location #' + d[1])
		elif d[0] == 'begin':
			x += 8
			res.append(make_triangle(x, y, right=True))
			x += 8
			res.append(make_triangle(x, y, right=True))
		elif d[0] == 'end':
			x += 8
			res.append(make_triangle(x, y, right=True))
			res.append(make_triangle(x, y, left=True))
			x += 8
		elif d[0] == 'skip':
			L = d[1] if len(d) > 1 else 1
			res.append(make_line(x, y, dx=HOR_STEP*L))
			x += HOR_STEP*L
		elif d[0] == 'term':
			# x += 4;
			res.append(make_text(x, y, d[1].replace('_', ' ')))
			if len(d) > 2:
				x += d[2] * HOR_STEP
			else:
				x += len_text_in_px(d[1])
		elif d[0] == 'nt':
			# x += 4;
			res.append(make_text(x, y, d[1], nt=True))
			if len(d) > 2:
				x += d[2] * HOR_STEP
			else:
				x += len_text_in_px(d[1])
		elif d[0] == 'uploop':
			res.append(make_loop(x, y, HOR_STEP, dx=d[1]*HOR_STEP))
		elif d[0] == 'optional':
			length = len_seq_in_px(d[1]) + 2*HOR_STEP
			res.append(make_line(x, y, dx=length))
			res.append(make_step_down(x, y, HOR_STEP, HOR_STEP))
			res.append(make_diag(d[1], y + HOR_STEP, x=x+HOR_STEP))
			res.append(make_step_back_up(x+length-HOR_STEP, y+HOR_STEP, HOR_STEP, HOR_STEP))
			x += length
		elif d[0] == 'downbranch':
			if len(d) > 1:
				dy = d[1] * HOR_STEP
			else:
				dy = HOR_STEP
			# print('[!] {0}'.format(d[1]))
			# length = len_seq_in_px(d[1]) + 4*HOR_STEP
			# res.append(make_line(x, y, dx=length))
			res.append(make_step_down(x, y, dy, HOR_STEP))
			# res.append(make_diag(d[1], y + 2*HOR_STEP, x=x+2*HOR_STEP))
			# res.append(make_step_back_up(x+length-2*HOR_STEP, y+2*HOR_STEP, 2*HOR_STEP, 2*HOR_STEP))
			# res.append(make_loop(x+length-HOR_STEP, y+2*HOR_STEP, HOR_STEP, dx=length-2*HOR_STEP))
			x += HOR_STEP
			y += dy
		elif d[0] == 'backbranch':
			if len(d) > 1:
				dy = d[1] * HOR_STEP
			else:
				dy = HOR_STEP
			res.append(make_step_back_up(x, y, dy, HOR_STEP))
			x -= HOR_STEP
			y -= dy
		else:
			print('[?] ' + d[0])
	return ''.join(res)
# ('begin')
# ('skip')
# ('term', NAME)
# ('uploop', 'actual text', 'length')
# ('end')

# TESTER
if False:
	with open('test.html', 'w', encoding='utf-8') as html:
		html.write('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"><html version="-//W3C//DTD XHTML 1.1//EN" xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/1999/xhtml http://www.w3.org/MarkUp/SCHEMA/xhtml11.xsd"><head/><body>')
		html.write('<svg xmlns="http://www.w3.org/2000/svg"><defs><style type="text/css">@namespace "http://www.w3.org/2000/svg"; path {fill: none; stroke: black;} polygon {fill: black; stroke: black;} svg {background-color: white;} text {font-size:12px;fill:black;font-weight:bold;font-family:monospace;} text.i {font-style:italic;}</style></defs>')
		html.write(make_diag([\
			('begin',),\
			('skip',),\
			('term', 'ACCEPT'),\
			('skip', 2),\
			('nt', 'Identifier'),\
			('skip', ),\
			('uploop', '', 'Identifier'),\
			('skip', ),\
			('end',),\
			], 30))
		html.write(make_diag([\
			('begin',),\
			('skip',),\
			('term', 'A'),\
			('skip',),\
			('end',),\
			], 50))
		html.write(make_diag([\
			('begin',),\
			('skip',),\
			('term', 'Aqwertyuiopasdfghjklzxcvbnm'),\
			('skip',),\
			('end',),\
			], 70))
		# html.write('<polygon points="9 33 1 29 1 37"/>')
		# html.write(make_triangle(33    , 9, right=True))
		# html.write(make_triangle(33 + 8, 9, right=True))
		# html.write(make_text(55, 9, 'ACCEPT'))
		# html.write(make_text(100, 9, 'Identifier', nt=True))
		# html.write(make_triangle(200   , 9, right=True))
		# html.write(make_triangle(200   , 9, left=True))
		# html.write(make_triangle(110   , 9, up=True))
		# html.write(make_triangle(120   , 9, down=True))
		# html.write(make_line(33, 9, dx=20))
		# html.write(make_triangle(30,20, right=True))
		html.write('</body></html>')
