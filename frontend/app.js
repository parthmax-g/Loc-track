const ROOM_ID = "demo-room"; // shared room
const WS_URL = "wss://YOUR-FLY-APP.fly.dev/ws/" + ROOM_ID;

const map = L.map("map").setView([0, 0], 16);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors"
}).addTo(map);

const marker = L.circleMarker([0,0], { radius: 8 }).addTo(map);
const ws = new WebSocket(WS_URL);

let lastSent = 0;

ws.onmessage = (e) => {
  const { lat, lng } = JSON.parse(e.data);
  marker.setLatLng([lat, lng]);
};

navigator.geolocation.watchPosition(pos => {
  const now = Date.now();
  if (now - lastSent < 2000) return; // throttle 2s

  lastSent = now;
  const payload = {
    lat: pos.coords.latitude,
    lng: pos.coords.longitude,
    ts: now
  };

  ws.readyState === 1 && ws.send(JSON.stringify(payload));
});
