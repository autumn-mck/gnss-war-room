# pylint: skip-file
from font.fetch import fetchFontRomsIfNeeded
from font.hp1345Font import Font
from font.mksvgs import makeSvgString, makeTextGroup

fetchFontRomsIfNeeded()


def test_loadFont():
	"""Test that the font can be loaded without error"""
	Font("./font/01347-80012.bin")


font = Font("./font/01347-80012.bin")

chars: list[int] = list(range(0x7F))  # ignoring the couple of higher characters
chars.remove(0x03)  # doesn't exist


def test_charVectorsList():
	"""Test that the charVectorsList is populated"""
	assert len(font.charVectorsList) == 256


def test_charsExist():
	"""Test that the font contains the ASCII characters"""
	for char in chars:
		print(f"Testing char {chr(char)}")
		assert font.charVectorsList[char]


def test_generateCharSvgs():
	"""Test that the font can be generated from the ASCII characters"""
	for char in chars:
		print(f"Testing char {chr(char)}")
		svg, _, _ = makeSvgString(font, chr(char).encode("ascii"))
		assert svg


def test_generateCharGroups():
	"""Test that the font can be generated from the ASCII characters"""
	for char in chars:
		print(f"Testing char {chr(char)}")
		svg, _, _ = makeTextGroup(font, chr(char).encode("ascii"))
		assert svg
