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

# pylint: skip-file

import math
from hp1345Font import Font


def vectorlist(wl):
	font = Font()
	lastX = 0
	x, y = 0, 0
	dx = 1
	rot = [1, 0, 0, 1]
	siz = 1.0
	attr = (0, 0, 0)
	ii = 1.0
	vl = []

	def move(x, y):
		vl.append([ii, (x, y)])

	def line(x, y):
		ox, oy = vl[-1][-1]
		if attr[1] in (2, 3):
			line = math.hypot(x - ox, y - oy)
			dx = (x - ox) / line
			dy = (y - oy) / line
			dl = 400.0 / 13.0 if attr[1] == 2 else 400.0 / 31.0
			ddx = dx * dl
			ddy = dy * dl
			while line > dl:
				vl[-1].append((ox + ddx, oy + ddy))
				ox += ddx * 2
				oy += ddy * 2
				vl.append([ii, (ox, oy)])
				line -= dl * 2
			if line > 0:
				vl[-1].append((ox + line * dx, oy + line * dy))

		if attr[1] != 5:
			vl[-1].append((x, y))
		if attr[1] in (1, 5):
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
				rot = [[1, 0, 0, 1], [0, -1, 1, 0], [-1, 0, 0, -1], [0, 1, -1, 0]][(a >> 9) & 3]
				siz = 1.0 + 0.5 * ((a >> 11) & 3)
				siz = int(siz * 2)
			tl = font.vectors(a & 0x0FF)
			for i in tl:
				lines = [ii]
				for dx, dy in i:
					ddx = dx * rot[0] + dy * rot[1]
					ddy = dx * rot[2] + dy * rot[3]
					x += ddx * siz
					y += ddy * siz
					lines.append((x, y))
				vl.append(lines)
		elif c == 0x2000:
			# Graph
			b = a & 0x7FF
			if a & 0x1000:
				if a & 0x800:
					vl.append((ii, (lastX, y), (x, b)))
				lastX = x
				x += dx
				y = b
			else:
				dx = b

		elif c == 0x0000:
			b = a & 0x7FF
			if a & 0x1000:
				if a & 0x0800:
					line(lastX, b)
				else:
					move(lastX, b)
				x = lastX
				y = b
			else:
				lastX = b

	return vl


def writeSvg(fileName: str, wl, scale=0.25):
	svg = open(fileName, "w", encoding="utf8")
	svg.write('<?xml version="1.0" standalone="no"?>\n')
	svg.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n')
	svg.write(' "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
	svg.write('<svg version="1.1"')
	width = 2048
	aspectRatio = 0.74
	height = width * aspectRatio
	offset = 5
	svg.write(f' width="{scale * width + 2 * offset}" height="{scale * height + 2 * offset}"')
	svg.write(' xmlns="http://www.w3.org/2000/svg">\n')
	svg.write('<g stroke-linecap="round" fill="none" stroke="black"')
	svg.write(f' stroke-width="{(scale * 5):.1f}"')
	svg.write(">\n")
	for i in vectorlist(wl):
		if i[0] <= 1.0:
			c = 255 - int(255 * i[0])
			svg.write('  <polyline points="')
			for x, y in i[1:]:
				svg.write(
					f" {(offset + scale * x):.1f}"
					f",{(scale * (height - y * aspectRatio) + offset):.1f}"
				)
			svg.write(f'" stroke="#{c:02x}{c:02x}{c:02x}"')
			svg.write("/>\n")
		elif i[0] == 2.0:
			x, y = i[1]
			svg.write(
				f'  <circle cx="{offset + scale * x}" '
				f'cy="{scale * (height - y * aspectRatio) + offset}"'
			)
			svg.write(f' r="{(5 * scale):.1f}" fill="black" />\n')

	svg.write("</g>\n")
	svg.write("</svg>\n")
	svg.close()


def main():
	b = bytearray(open("01347-80010.bin", "rb").read())
	lines = [(b[a] << 8) | b[a + 1] for a in range(0x31E, 0x400, 2)]
	writeSvg("_focus.svg", lines, 0.3)

	lines = [(b[a] << 8) | b[a + 1] for a in range(0x122, 0x150, 2)]
	lines.extend([(b[a] << 8) | b[a + 1] for a in range(0x200, 0x222, 2)])
	lines.extend([(b[a] << 8) | b[a + 1] for a in range(0x222, 0x2C8, 2)])
	writeSvg("_align.svg", lines, 0.3)


if __name__ == "__main__":
	main()
