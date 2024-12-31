const map = document.getElementById("map");
const comboBox = document.getElementById("toDisplay");

async function fetchMap() {
	const toFetch = comboBox.value;
	const response = await fetch(`/${toFetch}`);
	const svg = await response.text();
	map.innerHTML = svg;
}

fetchMap();
setInterval(async () => fetchMap(), 1000);
comboBox.addEventListener("change", async () => fetchMap());
