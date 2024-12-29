const map = document.getElementById("map");

async function fetchMap() {
	const response = await fetch("/map");
	const svg = await response.text();
	map.innerHTML = svg;
}

fetchMap();
setInterval(async () => fetchMap(), 1000);
