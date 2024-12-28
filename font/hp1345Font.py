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

class Font:
	def __init__(self, romfile = "01347-80012.bin"):
		self.v: list[list[list[tuple[int, int]]]] = [[]] * 256

		stroke = bytearray(open(romfile, "rb").read())
		idx = bytearray(open("./font/1816-1500.bin", "rb").read())
		used = [False] * len(stroke)

		def buildchar(char: int):
			# Address permutation of index ROM
			ia = (char & 0x1f) | ((char & 0xe0) << 1)

			# Address permutation of stroke ROM
			sa = idx[ia] << 2
			sa |= ((1 ^ (char >> 5) ^ (char >> 6)) & 1) << 10
			sa |= ((char >> 7) & 1) << 11

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

			self.v[char] = l

		for i in range(128):
			buildchar(i)
		for i in (0x9b, 0x9e, 0x91, 0x82):
			buildchar(i)
		for i in range(128, 256):
			buildchar(i)

	def vectors(self, char: int):
		return self.v[char]

	def boundingBox(self, char: int, bbox: list[int] | None = None, x = 0, y = 0) -> tuple[list[int], int, int]:
		if bbox is None:
			bbox = [0,0,-999,-999]
		for i in self.v[char]:
			for dx,dy in i:
				x += dx
				if chr(char) == '\r':
					x = 0
				y += dy
				bbox[0] = int(min(bbox[0], x))
				bbox[1] = int(min(bbox[1], y))
				bbox[2] = int(max(bbox[2], x))
				bbox[3] = int(max(bbox[3], y))
		return bbox, x, y

def main():
	font = Font()
	file = open("/tmp/_wargames.txt", "w", encoding="utf8")
	for ox in range(16):
		for oy in range(16):
			i = oy + ox * 16
			file.write(f'# {i:02x}\n')
			x = ox * 64
			y = oy * 64
			for j in font.v[i]:
				for dx,dy in j:
					x += dx
					y += dy
					file.write(f'{x} {y}\n')
				file.write("\n")

if __name__ == "__main__":
	main()
