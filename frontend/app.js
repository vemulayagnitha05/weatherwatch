const citySelect = document.getElementById("city");
const statusEl = document.getElementById("status");

async function loadCities() {
  const response = await fetch("/api/cities");
  if (!response.ok) throw new Error("Unable to load cities");
  const cities = await response.json();

  citySelect.innerHTML = "";
  cities.forEach(city => {
    const option = document.createElement("option");
    option.value = city.name;
    option.textContent = `${city.name}, ${city.country || ""}`;
    citySelect.appendChild(option);
  });
}

function valueOrDash(value, suffix = "") {
  return value === null || value === undefined ? "—" : `${Number(value).toFixed(1)}${suffix}`;
}

async function loadWeather() {
  const city = citySelect.value;
  if (!city) return;

  statusEl.textContent = `Loading ${city}...`;

  const [currentResponse, historyResponse] = await Promise.all([
    fetch(`/api/weather/${encodeURIComponent(city)}`),
    fetch(`/api/weather/${encodeURIComponent(city)}/history?hours=24`)
  ]);

  if (!currentResponse.ok) {
    statusEl.textContent = "No reading available yet. The collector may still be running.";
    return;
  }

  const current = await currentResponse.json();
  const history = await historyResponse.json();

  document.getElementById("temperature").textContent = valueOrDash(current.temperature_c, " °C");
  document.getElementById("humidity").textContent = valueOrDash(current.humidity_percent, " %");
  document.getElementById("wind").textContent = valueOrDash(current.wind_speed_kmh, " km/h");
  document.getElementById("pm25").textContent = valueOrDash(current.pm25, " µg/m³");
  document.getElementById("pm10").textContent = valueOrDash(current.pm10, " µg/m³");
  document.getElementById("aqi").textContent = valueOrDash(current.european_aqi);

  document.getElementById("updated").textContent =
    `Latest reading: ${new Date(current.observed_at).toLocaleString()}`;

  const tbody = document.getElementById("history-body");
  tbody.innerHTML = "";

  history.slice(-30).reverse().forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${new Date(row.observed_at).toLocaleString()}</td>
      <td>${valueOrDash(row.temperature_c)}</td>
      <td>${valueOrDash(row.humidity_percent)}</td>
      <td>${valueOrDash(row.pm25)}</td>
      <td>${valueOrDash(row.european_aqi)}</td>
    `;
    tbody.appendChild(tr);
  });

  statusEl.textContent = `${city} data loaded successfully.`;
}

document.getElementById("refresh").addEventListener("click", loadWeather);
citySelect.addEventListener("change", loadWeather);

(async function init() {
  try {
    await loadCities();
    await loadWeather();
  } catch (error) {
    console.error(error);
    statusEl.textContent = "Unable to connect to the WeatherWatch API.";
  }
})();
