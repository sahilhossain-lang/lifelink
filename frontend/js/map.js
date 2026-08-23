/**
 * LifeLink Interactive Map Module
 * Leaflet map visualization for blood banks, inventory badges, distance circles, and routing
 */

class LifeLinkMap {
  constructor() {
    this.map = null;
    this.markers = [];
    this.userMarker = null;
    this.userLat = 22.5726;
    this.userLng = 88.3639;
    this.circleRadius = null;
  }

  initMap() {
    const mapElement = document.getElementById('leaflet-map');
    if (!mapElement || this.map) return;

    // Initialize map centered at Kolkata
    this.map = L.map('leaflet-map', {
      center: [this.userLat, this.userLng],
      zoom: 12,
      zoomControl: true
    });

    // Dark sleek tile layer for premium medical tech theme
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://carto.com/">CARTO</a>, &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19
    }).addTo(this.map);

    // Add Patient / User location pin
    const userIcon = L.divIcon({
      className: 'custom-user-marker',
      html: `
        <div style="background: #3a86ff; width: 22px; height: 22px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 0 15px rgba(58,134,255,0.7); display: flex; align-items: center; justify-content: center; color: white; font-size: 10px; font-weight: 800;">
          P
        </div>
      `,
      iconSize: [22, 22],
      iconAnchor: [11, 11]
    });

    this.userMarker = L.marker([this.userLat, this.userLng], { icon: userIcon })
      .addTo(this.map)
      .bindPopup(`<b>You (Srijan)</b><br>Kolkata Central<br><span style="color:#e63946; font-weight:700;">Blood: B+</span>`);

    // Invalidate size on container show
    setTimeout(() => {
      if (this.map) this.map.invalidateSize();
    }, 200);
  }

  updateMarkers(bloodBanks, selectedBloodGroup = 'B+', selectedComponent = 'PRBC') {
    if (!this.map) this.initMap();

    // Clear existing markers
    this.markers.forEach(m => this.map.removeLayer(m));
    this.markers = [];

    const bounds = L.latLngBounds([ [this.userLat, this.userLng] ]);

    bloodBanks.forEach(bb => {
      const lat = bb.latitude || 22.5726;
      const lng = bb.longitude || 88.3639;
      bounds.extend([lat, lng]);

      const units = bb.units_available !== undefined ? bb.units_available : (
        bb.inventory ? (bb.inventory.find(i => i.blood_group === selectedBloodGroup)?.units_available || 0) : 0
      );

      const hasStock = units > 0;
      const markerColor = hasStock ? '#e63946' : '#64748b';
      const shadowColor = hasStock ? 'rgba(230,57,70,0.6)' : 'transparent';

      const customIcon = L.divIcon({
        className: 'custom-blood-marker',
        html: `
          <div style="
            background: ${markerColor};
            width: 32px;
            height: 32px;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            border: 2px solid #ffffff;
            box-shadow: 0 0 16px ${shadowColor};
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
          ">
            <div style="transform: rotate(45deg); color: #fff; font-size: 11px; font-weight: 800;">
              ${units}
            </div>
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 32]
      });

      const popupContent = `
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; min-width: 200px; padding: 4px;">
          <h4 style="margin: 0 0 4px; font-size: 14px; font-weight: 700; color: #0f172a;">${bb.name}</h4>
          <p style="margin: 0 0 6px; font-size: 12px; color: #64748b;">${bb.address}</p>
          <div style="display: flex; justify-content: space-between; align-items: center; margin: 8px 0; padding: 6px 8px; background: #f1f5f9; border-radius: 6px;">
            <span style="font-size: 12px; font-weight: 700; color: #e63946;">${selectedBloodGroup} ${selectedComponent}: <b>${units} Units</b></span>
            <span style="font-size: 11px; color: #3a86ff; font-weight: 600;">${bb.distance_km ? bb.distance_km + ' km' : 'Nearby'}</span>
          </div>
          <button onclick="window.app.openReservationModal(${bb.blood_bank_id || bb.id}, '${selectedBloodGroup}', '${selectedComponent}')"
            style="width: 100%; background: #e63946; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-weight: 700; font-size: 12px; cursor: pointer;">
            Reserve Blood Units
          </button>
        </div>
      `;

      const marker = L.marker([lat, lng], { icon: customIcon })
        .addTo(this.map)
        .bindPopup(popupContent);

      marker.bloodBankId = bb.blood_bank_id || bb.id;
      this.markers.push(marker);
    });

    if (this.markers.length > 0) {
      this.map.fitBounds(bounds, { padding: [40, 40] });
    }
  }

  focusBloodBank(id) {
    const marker = this.markers.find(m => m.bloodBankId === id);
    if (marker && this.map) {
      this.map.setView(marker.getLatLng(), 14, { animate: true });
      marker.openPopup();
    }
  }
}

window.lifelinkMap = new LifeLinkMap();
