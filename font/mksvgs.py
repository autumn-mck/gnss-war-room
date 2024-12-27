#!/usr/bin/env python3
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <phk@FreeBSD.org> wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.   Poul-Henning Kamp
# ----------------------------------------------------------------------------
#
# This file produces a .SVG table of the HP1345A character rom

import hp1345_font

def polylines(fo, ind, fn, ch, x = 0, y = 0, shadow = False):
	if shadow != False:
		x0,y0 = x,y
		for i in fn.vectors(ch):
			dx,dy = i[0]
			fo.write((' ' * ind) + '<polyline points="')
			fo.write(" %d,%d" % (x, y))
			fo.write(" %d,%d" % (x + dx, y + dy))
			fo.write('" %s />\n' % shadow)
			for dx,dy in i:
				x += dx
				y += dy
		x,y = x0,y0

	for i in fn.vectors(ch):
		if len(i) == 1:
			dx,dy = i[0]
			x += dx
			y += dy
		else:
			fo.write((' ' * ind) + '<polyline points="')
			for dx,dy in i:
				x += dx
				y += dy
				fo.write(" %d,%d" % (x, y))
			fo.write('" />\n')
	return x,y

def grid(fo, ind, x0, y0, x1, y1, markers):
	# Make a list of grid lines and sort them by marker
	# to avoid lighter lines overlapping darker lines.

	l = []
	for x in range(x0, x1 + 1):
		m = ''
		for a,b in markers:
			if x % a == 0:
				m = b
		l.append((a, m, x, y0, x, y1))
	for y in range(y0, y1 + 1):
		m = ''
		for a,b in markers:
			if y % a == 0:
				m = b
		l.append((a, m, x0, y, x1, y))

	l.sort()

	fmt = ' ' * ind + '<polyline points="%d,%d %d,%d" %s />\n'

	for a,b,x0,y0,x1,y1 in l:
		fo.write(fmt % (x0, y0, x1, y1, b))

def mk_svg(fn, font, s, scale = 10, offset = 1, border = 5):

	ss = bytearray(s)


	bbox,x1,y1 = None,0,0
	for ch in ss:
		bbox, x1, y1 = font.bbox(ch, bbox=bbox, x=x1, y=y1)

	wid = scale * (offset + 2 * border + bbox[2] - bbox[0])
	ht = scale * (offset + 2 * border + bbox[3] - bbox[1])

	fo = open(fn, "w")
	fo.write('<?xml version="1.0" standalone="no"?>\n')
	fo.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n')
	fo.write(' "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
	fo.write('<svg version="1.1"\n')
	fo.write(' width="%d" height="%d"\n' % (wid + 1, ht + 1))
	fo.write(' xmlns="http://www.w3.org/2000/svg">\n')
	fo.write('  <g stroke-linecap="round" stroke-linejoin="round" ')
	fo.write('fill="none"')
	fo.write(' transform="matrix(%d,0,0,%d,%d,%d)" ' % (
		scale, -scale,
		scale * (border + offset - bbox[0]),
		scale * (border + offset + bbox[3])))
	fo.write('>\n')

	fo.write('	<g stroke-width=".2" stroke="#cccccc">\n')
	grid(fo, 6,
		bbox[0] - border, bbox[1] - border,
		bbox[2] + border, bbox[3] + border,
		(
		( 1, ''),
		( 5, 'stroke="#aaaaaa"'),
		(10, 'stroke="#888888"'),
		)
	)
	fo.write('	</g>\n')

	fo.write('	<g stroke-width=".8" stroke="#000000">\n')
	x,y = 0,0
	for ch in ss:
		x,y = polylines(fo, 6, font, ch, x=x, y=y,
			shadow='stroke-width=".4" stroke="#99eeee"')
	fo.write('	</g>\n')
	fo.write('	<circle cx="%d" cy="%d" r=".7" fill="green" />\n' % (0,0))
	fo.write('	<circle cx="%d" cy="%d" r=".3" fill="red" />\n' % (x, y))
	fo.write('</g></svg>\n')
	fo.close()
	return True,wid,ht

if __name__ == "__main__":
	f = hp1345_font.font()
	mk_svg("fig_wg.svg", f, "HP1345A (and WarGames)".encode('ascii'),
		scale=2, border=4, offset=0)
	f2 = hp1345_font.font("01347-80001.bin".encode('ascii'))
	f2.v[0x2e] = f.v[0x2c]
	mk_svg("fig_commas.svg", f2, ",.".encode('ascii'), border=5, offset=0)

	for ch in range(256):
		v = f.vectors(ch)
		if len(v) == 1:
			continue
		mk_svg("_wargames_%02x.svg" % ch, f, [ch,],
			scale=10, border=5, offset=5)

	grid = 40
	wid = 17 * grid
	ht = 17 * grid
	fo = open("fig_table.svg", "w")
	fo.write('<?xml version="1.0" standalone="no"?>\n')
	fo.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n')
	fo.write(' "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
	fo.write('<svg version="1.1"\n')
	fo.write(' width="%d" height="%d"\n' % (wid + 1, ht + 1))
	fo.write(' xmlns="http://www.w3.org/2000/svg"')
	fo.write(' xmlns:xlink="http://www.w3.org/1999/xlink"')
	fo.write('>\n')
	fo.write('  <g stroke-linecap="round" stroke-linejoin="round" ')
	fo.write('fill="none"')
	fo.write(' transform="matrix(1,0,0,-1,0,%d)" ' % (ht - 1))
	fo.write('>\n')

	fo.write('	<g stroke="#000000">\n')
	for i in range(0,16):
		b = bytearray("-%x".encode('ascii') % i)
		x = 5
		y = (15-i) * grid + 10
		x,y = polylines(fo, 6, f, b[0], x=x, y=y )
		x,y = polylines(fo, 6, f, b[1], x=x, y=y )
		x = (i+1) * grid + 5
		y = 16 * grid + 10
		x,y = polylines(fo, 6, f, b[1], x=x, y=y )
		x,y = polylines(fo, 6, f, b[0], x=x, y=y )
	fo.write('	</g>\n')

	def box(x,y,c):
		fo.write('\t<rect x="%d" y="%d"' % (x,y))
		fo.write(' width="%d" height="%d"' % (grid, grid))
		fo.write(' style="fill:%s;stroke:#999999"/>\n' % c)

	for cx in range(16):
		for cy in range(16):
			x = (cx + 1) * grid
			y = cy * grid
			ch = cx * 16 + (15 - cy)
			v = f.vectors(ch)
			if len(v) == 0:
				box(x,y, "#eeeeee")
				continue
			bb,x1,y1 = f.bbox(ch)
			bb[0] -= 2
			bb[1] -= 2
			bb[2] += 2
			bb[3] += 2
			fo.write('\t<a xlink:href="_wargames_%02x.svg">\n' % ch)
			box(x,y, "#ffffff")
			fo.write('\t<g stroke="#000000"')
			scx = (grid - 0.) / (bb[2] - bb[0])
			scy = (grid - 0.) / (bb[3] - bb[1])
			sc = min(scx, scy, 1.8)
			fo.write(' transform="matrix(%.2f,0,0,%.2f,%d,%d)"' % (
				sc, sc, x - sc * bb[0], y - sc * bb[1])
			)
			fo.write(' >\n')
			polylines(fo, 10, f, ch)
			fo.write('\t</g>\n')
			fo.write('\t</a>\n')

	fo.write('  </g>\n')
	fo.write('</svg>\n')

