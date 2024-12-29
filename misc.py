import tempfile

def saveToTempFile(string: str) -> str:
	"""Save a string to a temporary file and return its file path."""
	with tempfile.NamedTemporaryFile(delete=False) as temp:
		with open(temp.name, "w", encoding="utf8") as f:
			f.write(string)
	return temp.name