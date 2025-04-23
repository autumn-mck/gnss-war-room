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
	def __init__(self, romfile="./font/01347-80012.bin") -> None:
		self.charVectorsList: list[list[list[tuple[int, int]]]] = [[]] * 256

		with open(romfile, "rb") as f:
			strokeRom = f.read()
		with open("./font/1816-1500.bin", "rb") as f:
			charIndexRom = f.read()

		used = [False] * len(strokeRom)

		def buildchar(char: int):
			# Address permutation of index ROM
			ia = (char & 0x1F) | ((char & 0xE0) << 1)

			# Address permutation of stroke ROM
			sa = charIndexRom[ia] << 2
			sa |= ((1 ^ (char >> 5) ^ (char >> 6)) & 1) << 10
			sa |= ((char >> 7) & 1) << 11

			if not strokeRom[sa] and not strokeRom[sa + 1]:
				return

			lines: list[list[tuple[int, int]]] = []
			while True:
				if used[sa]:
					return
				used[sa] = True

				dx = strokeRom[sa] & 0x3F
				if strokeRom[sa] & 0x40:
					dx = -dx

				dy = strokeRom[sa + 1] & 0x3F
				if strokeRom[sa + 1] & 0x40:
					dy = -dy

				if not strokeRom[sa] & 0x80:
					lines.append([])

				if len(lines) == 0:
					lines.append([(0, 0)])

				lines[-1].append((dx, dy))

				if strokeRom[sa + 1] & 0x80:
					break

				sa += 2

			self.charVectorsList[char] = lines

		for i in range(128):
			buildchar(i)
		for i in (0x9B, 0x9E, 0x91, 0x82):
			buildchar(i)
		for i in range(128, 256):
			buildchar(i)
