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


import io
from io import StringIO

from font.hp1345Font import Font


def charToPolylines(
	svg: StringIO,
	indent: int,
	charLines: list[list[tuple[int, int]]],
	x=0,
	y=0,
	fontColour: str = "#000000",
	fontThickness: float = 0.8,
) -> tuple[int, int]:
	"""Create a set of polylines from the given character's vector data"""
	for line in charLines:
		if len(line) == 1:
			(dx, dy) = line[0]
			x += dx
			y += dy
		else:
			x, y = lineToPolyline(svg, indent, line, x, y, fontColour, fontThickness)

	return x, y


def lineToPolyline(
	svg: StringIO,
	indent: int,
	line: list[tuple[int, int]],
	x: int,
	y: int,
	fontColour: str,
	fontThickness: float,
) -> tuple[int, int]:
	"""Create a polyline for the given line"""
	svg.write(f'{" " * indent}<polyline points="')
	for dx, dy in line:
		x += dx
		y += dy
		svg.write(f" {x},{y}")
	svg.write('" />\n')

	# workaround for QTBUG-132468
	if areVectorsSinglePoint(line):
		svg.write(
			(" " * indent)
			+ f"<circle cx='{x}' cy='{y}' r='{fontThickness / 2}' fill='{fontColour}' />\n"
		)

	return x, y


def areVectorsSinglePoint(line: list[tuple[int, int]]) -> bool:
	return all(x == 0 and y == 0 for x, y in line[1:])


def addCharToBoundingBox(
	font: Font, char: int, boundingBox: list[int], x: int, y: int
) -> tuple[list[int], int, int]:
	"""Add the given character to the bounding box"""
	for charLine in font.charVectorsList[char]:
		if chr(char) == "\r":
			x = 0
		boundingBox, x, y = addLineToBoundingBox(charLine, boundingBox, x, y)
	return (boundingBox, x, y)


def addLineToBoundingBox(line: list[tuple[int, int]], boundingBox: list[int], x: int, y: int):
	"""Add the given line to the bounding box"""
	for dx, dy in line:
		x += dx
		y += dy
		boundingBox[0] = int(min(boundingBox[0], x))
		boundingBox[1] = int(min(boundingBox[1], y))
		boundingBox[2] = int(max(boundingBox[2], x))
		boundingBox[3] = int(max(boundingBox[3], y))
	return (boundingBox, x, y)


def textToSvg(svg: StringIO, font: Font, text: bytes, fontColour: str, fontThickness: float):
	"""Add the text to the SVG using the given font"""
	x, y = 0, 0
	for char in text:
		charLines = font.charVectorsList[char]
		x, y = charToPolylines(svg, 6, charLines, x, y, fontColour, fontThickness)
		if chr(char) == "\r":
			x = 0


def makeTextGroup(
	font: Font,
	text: bytes,
	scale=2.0,
	xOffset=0,
	yOffset=0,
	border=10,
	fontThickness=0.8,
	fontColour="#000000",
) -> tuple[str, float, float]:
	"""Create an SVG group for the given text"""
	boundingBox = [0, 0, 0, 0]
	x1, y1 = 0, 0
	for char in text:
		(boundingBox, x1, y1) = addCharToBoundingBox(font, char, boundingBox, x1, y1)

	width = scale * (xOffset + 2 * border + boundingBox[2] - boundingBox[0])
	height = scale * (yOffset + 2 * border + boundingBox[3] - boundingBox[1])

	svg = io.StringIO()
	svg.write(f"""	<g
    stroke-width="{fontThickness}"
    stroke="{fontColour}"
    stroke-linecap="round"
    stroke-linejoin="round"
    transform="matrix({scale},0,0,{-scale},
   {scale * (border + xOffset - boundingBox[0])},
   {scale * (border + yOffset + boundingBox[3])})"
    fill="none">\n""")

	textToSvg(svg, font, text, fontColour, fontThickness)
	svg.write("	</g>\n")

	return (svg.getvalue(), width, height)


def makeSvgString(
	font: Font, text: bytes, scale=2, offset=0, border=10, fontThickness=0.8, fontColour="#000000"
) -> tuple[str, int, int]:
	"""Create an SVG for the given text"""
	boundingBox = [0, 0, 0, 0]
	x1, y1 = 0, 0
	for char in text:
		(boundingBox, x1, y1) = addCharToBoundingBox(font, char, boundingBox, x1, y1)

	width = scale * (offset + 2 * border + boundingBox[2] - boundingBox[0])
	height = scale * (offset + 2 * border + boundingBox[3] - boundingBox[1])

	svg = io.StringIO()
	svg.write(f"""<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
 "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1"
 viewBox="0 0 {width} {height}"
 xmlns="http://www.w3.org/2000/svg">
  <g stroke-linecap="round" stroke-linejoin="round"
   fill="none"
   transform="matrix({scale},0,0,{-scale},
   {scale * (border + offset - boundingBox[0])},
   {scale * (border + offset + boundingBox[3])})"
>
    <g stroke-width="{fontThickness}" stroke="{fontColour}">
""")

	textToSvg(svg, font, text, fontColour, fontThickness)
	svg.write("    </g>\n")

	svg.write("  </g>\n</svg>\n")
	return (svg.getvalue(), width, height)
