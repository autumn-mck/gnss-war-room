#!/usr/bin/env python
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <phk@FreeBSD.org> wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.   Poul-Henning Kamp
# ----------------------------------------------------------------------------
#
# This file reads the ROMS and procduces list of delta-vectors
#

from __future__ import print_function

import math

import hp1345_font

def vectorlist(wl):
	f = hp1345_font.font()
	last_x = 0
	x = y = 0
	dx = 1
	rot = [ 1, 0, 0, 1 ]
	siz = 1.0
	attr = (0,0,0)
	ii = 1.0
	vl = []

	def move(x,y):
		vl.append([ii, (x, y)])

	def line(x,y):
		ox,oy = vl[-1][-1]
		if attr[1] in (2,3):
			l = math.hypot(x - ox, y - oy)
			dx = (x - ox) / l
			dy = (y - oy) / l
			if attr[1] == 2:
				dl = (400. / 13.)
			else:
				dl = (400. / 31.)
			ddx = dx * dl
			ddy = dy * dl
			while l > dl:
				vl[-1].append((ox + ddx, oy + ddy))
				ox += ddx * 2
				oy += ddy * 2
				vl.append([ii, (ox, oy)])
				l -= dl * 2
			if l > 0:
				vl[-1].append((ox + l * dx, oy + l * dy))

		if attr[1] != 5:
			vl[-1].append((x, y))
		if attr[1] in (1,5):
			vl.append([2, (x, y)])
			vl.append([ii, (x, y)])

	for a in wl:
		c = a & 0x6000
		if c == 0x6000:
			# Set Condition
			attr = ((a >> 11) & 3, (a >> 7) & 7, (a >> 3) & 3)
			ii = attr[0] / 3.0 / (4.0 - attr[2])
			vl.append([ii, (x, y)])
		elif c == 0x4000:
			# Text
			if a & 0x0100:
				rot = [
					[  1,  0,  0,  1 ],
					[  0, -1,  1,  0 ],
					[ -1,  0,  0, -1 ],
					[  0,  1, -1,  0 ],
				][(a >> 9) & 3]
				siz = 1.0 + .5 * ((a >> 11) & 3)
				siz = int(siz * 2)
			tl = f.vectors(a & 0x0ff)
			for i in tl:
				l = [ii]
				for dx,dy in i:
					ddx = dx * rot[0] + dy * rot[1]
					ddy = dx * rot[2] + dy * rot[3]
					x += ddx * siz
					y += ddy * siz
					l.append((x, y))
				vl.append(l)
		elif c == 0x2000:
			# Graph
			b = a & 0x7ff
			if a & 0x1000:
				if a & 0x800:
					vl.append((ii, (last_x, y), (x, b)))
				last_x = x
				x += dx
				y = b
			else:
				dx = b

		elif c == 0x0000:
			b = a & 0x7ff
			if a & 0x1000:
				if a & 0x0800:
					line(last_x, b)
				else:
					move(last_x, b)
				x = last_x
				y = b
			else:
				last_x = b

	return vl

def svg(fn, wl, scale=.25):
	fo = open(fn, "w")
	fo.write('<?xml version="1.0" standalone="no"?>\n')
	fo.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n')
	fo.write(' "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
	fo.write('<svg version="1.1"')
	wid = 2048
	asp = 0.74
	ht = wid * asp
	off = 5
	fo.write(' width="%d" height="%d"' % (
		scale * wid + 2 * off, scale * ht + 2 * off)
	)
	fo.write(' xmlns="http://www.w3.org/2000/svg">\n')
	fo.write('<g stroke-linecap="round" fill="none" stroke="black"')
	fo.write(' stroke-width = "%.1f"' % (5.0 * scale))
	fo.write('>\n')
	for i in vectorlist(wl):
		if i[0] <= 1.0:
			c = 255 - int(255 * i[0])
			fo.write('  <polyline points="')
			for x,y in i[1:]:
				fo.write(" %.1f,%.1f" % (
					off + scale * x,
					scale * (ht - y * asp) + off
				))
			fo.write('" stroke="#%02x%02x%02x"' % (c,c,c))
			fo.write('/>\n')
		elif i[0] == 2.0:
			x,y = i[1]
			fo.write('  <circle cx="%d" cy="%d"' % (
				off + scale * x,
				scale * (ht - y * asp) + off
			))
			fo.write(' r="%.1f" fill="black" />\n' % (5 * scale))

	fo.write('</g>\n')
	fo.write('</svg>\n')


if __name__ == "__main__":

	b = bytearray(open("01347-80010.bin", "rb").read())
	l = []
	for a in range(0x31e, 0x400, 2):
		l.append((b[a] << 8) | b[a + 1])
	svg("_focus.svg", l, .3)

	l = []
	for a in range(0x122, 0x150, 2):
		l.append((b[a] << 8) | b[a + 1])
	for a in range(0x150, 0x200, 2):
		l.append((b[a] << 8) | b[a + 1])
	for a in range(0x222, 0x2c8, 2):
		l.append((b[a] << 8) | b[a + 1])
	svg("_align.svg", l, .3)
