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

class font(object):
	def __init__(self, romfile = "01347-80012.bin"):
		self.v = [[]] * 256

		stroke = bytearray(open(romfile, "rb").read())
		idx = bytearray(open("1816-1500.bin", "rb").read())
		used = [False] * len(stroke)

		def buildchar(ch):
			# Address permutation of index ROM
			ia = (ch & 0x1f) | ((ch & 0xe0) << 1)

			# Address permutation of stroke ROM
			sa = idx[ia] << 2
			sa |= ((1 ^ (ch >> 5) ^ (ch >> 6)) & 1) << 10
			sa |= ((ch >> 7) & 1) << 11

			if not stroke[sa] and not stroke[sa + 1]:
				return

			l = []
			while True:

				if used[sa]:
					return
				used[sa] = True

				dx = stroke[sa] & 0x3f
				if stroke[sa] & 0x40:
					dx = -dx

				dy = stroke[sa + 1] & 0x3f
				if stroke[sa + 1] & 0x40:
					dy = -dy

				if not stroke[sa] & 0x80:
					l.append([])

				if len(l) == 0:
					l.append([(0,0)])

				l[-1].append((dx, dy))

				if stroke[sa + 1] & 0x80:
					break

				sa += 2

			self.v[ch] = l

		for i in range(128):
			buildchar(i)
		for i in (0x9b, 0x9e, 0x91, 0x82):
			buildchar(i)
		for i in range(128, 256):
			buildchar(i)

	def vectors(self, ch):
		return self.v[ch]

	def bbox(self, ch, bbox = None, x = 0, y = 0):
		if bbox == None:
			bbox = [0,0,-999,-999]
		for i in self.v[ch]:
			for dx,dy in i:
				x += dx
				y += dy
				bbox[0] = int(min(bbox[0], x))
				bbox[1] = int(min(bbox[1], y))
				bbox[2] = int(max(bbox[2], x))
				bbox[3] = int(max(bbox[3], y))
		return bbox, x, y


if __name__ == "__main__":
	f = font()
	fo = open("/tmp/_wargames.txt", "w")
	for ox in range(16):
		for oy in range(16):
			i = oy + ox * 16
			fo.write("# %02x\n" % i)
			x = ox * 64
			y = oy * 64
			for j in f.v[i]:
				for dx,dy in j:
					x += dx
					y += dy
					fo.write("%d %d\n" % (x, y))
				fo.write("\n")
