/**
 * LifeLink Main Application Controller
 * Handles tabs, modals, real-time UI rendering, and role synchronizations
 */

class LifeLinkApp {
  constructor() {
    this.activeTab = 'home';
    this.currentBloodBanks = [];
    this.selectedBloodBankForReservation = null;
  }

  async init() {
    console.log("Initializing LifeLink App...");
    this.setupEventListeners();
    await this.switchRole('PATIENT');
    this.initTheme();

    // Auto-refresh notifications and data every 20 seconds
    setInterval(() => {
      this.loadNotifications(false);
    }, 20000);
  }

  setupEventListeners() {
    // Navigation Tabs
    document.querySelectorAll('.nav-item[data-tab]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tab = e.currentTarget.getAttribute('data-tab');
        this.switchTab(tab);
      });
    });

    // Role Switcher Dropdown
    const roleSelect = document.getElementById('role-select');
    if (roleSelect) {
      roleSelect.addEventListener('change', async (e) => {
        await this.switchRole(e.target.value);
      });
    }

    // Theme Toggle Button
    const themeToggle = document.getElementById('theme-toggle-btn');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => this.toggleTheme());
    }

    // Blood Search Form
    const searchBtn = document.getElementById('btn-search-blood');
    if (searchBtn) {
      searchBtn.addEventListener('click', () => this.performBloodSearch());
    }

    // Quick Actions
    document.querySelectorAll('[data-action]').forEach(el => {
      el.addEventListener('click', (e) => {
        const action = e.currentTarget.getAttribute('data-action');
        this.handleQuickAction(action);
      });
    });
  }

  initTheme() {
    const saved = localStorage.getItem('lifelink_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    this.updateThemeIcon(saved);
  }

  toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('lifelink_theme', next);
    this.updateThemeIcon(next);
  }

  updateThemeIcon(theme) {
    const icon = document.getElementById('theme-toggle-icon');
    if (icon) {
      icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
  }

  async switchRole(role) {
    window.appState.currentRole = role;
    const presets = window.appState.getDemoUsers();
    const creds = presets[role];

    try {
      // Auto login as role
      await window.api.login(creds.email, creds.password);
    } catch (e) {
      console.warn("Using local role context:", e);
    }

    // Update UI headers
    const roleSelect = document.getElementById('role-select');
    if (roleSelect && roleSelect.value !== role) {
      roleSelect.value = role;
    }

    const userNameEl = document.getElementById('sidebar-user-name');
    const userRoleEl = document.getElementById('sidebar-user-role');
    const avatarEl = document.getElementById('sidebar-user-avatar');

    if (userNameEl) userNameEl.innerText = creds.name;
    if (userRoleEl) userRoleEl.innerText = creds.subtitle;
    if (avatarEl) avatarEl.innerText = creds.name.charAt(0);

    // Adjust Nav Items visibility based on Role (PDF Page 10)
    document.querySelectorAll('.role-nav').forEach(el => {
      const allowed = el.getAttribute('data-roles')?.split(',') || [];
      if (allowed.includes(role) || allowed.length === 0) {
        el.style.display = 'flex';
      } else {
        el.style.display = 'none';
      }
    });

    // Reload active tab data
    await this.loadTabData(this.activeTab);
    await this.loadNotifications(true);
  }

  switchTab(tabId) {
    this.activeTab = tabId;

    // Update active nav class
    document.querySelectorAll('.nav-item').forEach(btn => {
      if (btn.getAttribute('data-tab') === tabId) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(tab => {
      if (tab.id === `tab-${tabId}`) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });

    this.loadTabData(tabId);
  }

  async loadTabData(tabId) {
    switch (tabId) {
      case 'home':
        await this.renderHomeDashboard();
        break;
      case 'blood':
        await this.performBloodSearch();
        setTimeout(() => window.lifelinkMap.initMap(), 100);
        break;
      case 'reservations':
        await this.renderMyReservations();
        break;
      case 'bloodbank-inventory':
        await this.renderBloodBankInventory();
        break;
      case 'bloodbank-requests':
        await this.renderBloodBankRequests();
        break;
      case 'treatments':
        await this.renderTreatments();
        break;
      case 'medicines':
        await this.renderMedicines();
        break;
      case 'critical-medicines':
        await this.renderCriticalMedicines();
        break;
      case 'caregivers':
        await this.renderCaregivers();
        break;
      case 'notifications':
        await this.renderNotificationsList();
        break;
    }
  }

  // 1. Home Dashboard (PDF Page 7)
  async renderHomeDashboard() {
    try {
      const profile = await window.api.getPatientProfile();
      const treatments = await window.api.getTreatments();
      const medicines = await window.api.getMedicines();
      const reservations = await window.api.getReservations();

      // Find transfusion treatment
      const transfusion = treatments.find(t => t.type.toUpperCase() === 'TRANSFUSION') || {
        scheduled_date: '05 September 2026',
        expected_units: 2,
        blood_group: profile.blood_group || 'B+'
      };

      const heroTitle = document.getElementById('hero-transfusion-title');
      const heroMeta = document.getElementById('hero-transfusion-meta');
      const heroBadge = document.getElementById('hero-blood-badge');

      if (heroTitle) heroTitle.innerText = `Blood Transfusion (${transfusion.blood_group} • ${transfusion.expected_units} Units)`;
      if (heroMeta) heroMeta.innerText = `Scheduled: ${transfusion.scheduled_date} • CMRI Hospital`;
      if (heroBadge) heroBadge.innerText = transfusion.blood_group;

      // Render upcoming list
      const upcomingContainer = document.getElementById('upcoming-tasks-list');
      if (upcomingContainer) {
        let itemsHtml = `
          <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-date">Today • 08:00 PM</div>
              <div class="timeline-title">Medicine: Deferasirox 500mg (2 tablets)</div>
              <div class="timeline-desc">Take with liquid on an empty stomach</div>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-date">05 September 2026</div>
              <div class="timeline-title">Transfusion: 2 Units B+ PRBC</div>
              <div class="timeline-desc">Calcutta Medical Research Institute</div>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-dot cyan"></div>
            <div class="timeline-content">
              <div class="timeline-date">12 September 2026 • 10:00 AM</div>
              <div class="timeline-title">Chemotherapy: Cycle 3 of 6</div>
              <div class="timeline-desc">Tata Medical Center</div>
            </div>
          </div>
        `;
        upcomingContainer.innerHTML = itemsHtml;
      }
    } catch (e) {
      console.warn("Error rendering home dashboard:", e);
    }
  }

  // 2. Blood Search & Map View (PDF Page 5, 7, 9, 10)
  async performBloodSearch() {
    const bgSelect = document.getElementById('search-blood-group');
    const compSelect = document.getElementById('search-component');
    const locInput = document.getElementById('search-location');

    const bloodGroup = bgSelect ? bgSelect.value : 'B+';
    const component = compSelect ? compSelect.value : 'PRBC';
    const location = locInput ? locInput.value : 'Kolkata';

    const resultsList = document.getElementById('blood-results-list');
    if (resultsList) resultsList.innerHTML = '<div style="padding: 20px; color: var(--text-muted);">Searching verified blood banks...</div>';

    try {
      const results = await window.api.searchBlood(bloodGroup, component, location);
      this.currentBloodBanks = results;

      if (resultsList) {
        if (results.length === 0) {
          resultsList.innerHTML = '<div style="padding: 20px; color: var(--text-muted);">No blood banks found with the selected criteria.</div>';
        } else {
          resultsList.innerHTML = results.map(b => `
            <div class="blood-bank-card" onclick="window.lifelinkMap.focusBloodBank(${b.blood_bank_id})">
              <div class="bb-header">
                <div>
                  <div class="bb-name">${b.name}</div>
                  <div class="bb-source-badge"><i class="fas fa-shield-alt" style="color:#06d6a0;"></i> ${b.source_name}</div>
                </div>
                <span class="bb-distance">${b.distance_km} km</span>
              </div>
              <div class="bb-details">
                <div><i class="fas fa-map-marker-alt"></i> ${b.address}</div>
                <div><i class="fas fa-phone"></i> ${b.phone}</div>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-subtle); padding-top:10px;">
                <div class="bb-inventory-pill">
                  <i class="fas fa-tint" style="color:var(--accent-blood);"></i>
                  <span>${b.blood_group} ${b.component}: <b>${b.units_available} Units</b></span>
                </div>
                <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); window.app.openReservationModal(${b.blood_bank_id}, '${b.blood_group}', '${b.component}', 2)">
                  Reserve Blood
                </button>
              </div>
            </div>
          `).join('');
        }
      }

      // Update Map Markers
      window.lifelinkMap.updateMarkers(results, bloodGroup, component);
    } catch (e) {
      if (resultsList) resultsList.innerHTML = `<div style="color:var(--accent-blood); padding:16px;">Error fetching blood banks: ${e.message}</div>`;
    }
  }

  // 3. Open Reservation Modal (PDF Page 7, 10)
  openReservationModal(bloodBankId, bloodGroup = 'B+', component = 'PRBC', defaultUnits = 2) {
    this.selectedBloodBankForReservation = bloodBankId;
    const bb = this.currentBloodBanks.find(b => b.blood_bank_id === bloodBankId || b.id === bloodBankId);

    const bankNameEl = document.getElementById('res-modal-bank-name');
    const groupInput = document.getElementById('res-modal-group');
    const compInput = document.getElementById('res-modal-component');
    const unitsInput = document.getElementById('res-modal-units');
    const dateInput = document.getElementById('res-modal-date');

    if (bankNameEl) bankNameEl.innerText = bb ? bb.name : 'ABC Blood Bank';
    if (groupInput) groupInput.value = bloodGroup;
    if (compInput) compInput.value = component;
    if (unitsInput) unitsInput.value = defaultUnits;
    if (dateInput) dateInput.value = '05 September 2026';

    const modal = document.getElementById('reservation-modal');
    if (modal) modal.classList.add('active');
  }

  closeReservationModal() {
    const modal = document.getElementById('reservation-modal');
    if (modal) modal.classList.remove('active');
  }

  async submitReservation() {
    const bloodBankId = this.selectedBloodBankForReservation || 1;
    const bloodGroup = document.getElementById('res-modal-group').value;
    const component = document.getElementById('res-modal-component').value;
    const units = parseInt(document.getElementById('res-modal-units').value, 10) || 1;
    const requiredDate = document.getElementById('res-modal-date').value || '05 September 2026';
    const hospital = document.getElementById('res-modal-hospital').value || 'Calcutta Medical Research Institute';
    const notes = document.getElementById('res-modal-notes').value || 'Scheduled 21-day transfusion cycle.';

    try {
      const res = await window.api.createReservation({
        blood_bank_id: bloodBankId,
        blood_group: bloodGroup,
        component: component,
        units: units,
        required_date: requiredDate,
        hospital_name: hospital,
        patient_notes: notes
      });

      this.closeReservationModal();
      window.appState.showToast("Reservation Submitted (PENDING)", `Requested ${units} units of ${bloodGroup} ${component}. Awaiting Blood Bank confirmation.`, "🩸");
      this.switchTab('reservations');
    } catch (e) {
      alert(`Error submitting reservation: ${e.message}`);
    }
  }

  // 4. Render My Reservations (Patient View)
  async renderMyReservations() {
    const listEl = document.getElementById('my-reservations-list');
    if (!listEl) return;

    try {
      const reservations = await window.api.getReservations();
      if (reservations.length === 0) {
        listEl.innerHTML = '<div style="padding: 24px; color: var(--text-muted); text-align: center;">No blood reservations made yet. Use "Find Blood" to reserve units.</div>';
        return;
      }

      listEl.innerHTML = `
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Blood Bank</th>
              <th>Blood & Units</th>
              <th>Required Date</th>
              <th>Hospital</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${reservations.map(r => `
              <tr>
                <td>#${r.id}</td>
                <td><b>${r.blood_bank_name}</b><br><small style="color:var(--text-muted);">${r.blood_bank_phone}</small></td>
                <td><span class="blood-badge" style="padding:2px 8px; font-size:12px;">${r.blood_group}</span> • ${r.units} Unit(s) (${r.component})</td>
                <td>${r.required_date}</td>
                <td>${r.hospital_name || 'CMRI Hospital'}</td>
                <td><span class="status-badge status-${r.status.toLowerCase()}">${r.status}</span></td>
                <td>
                  ${r.status === 'ACCEPTED' ? '<span style="color:#06d6a0; font-weight:700;"><i class="fas fa-check-circle"></i> Confirmed</span>' : ''}
                  ${r.status === 'PENDING' ? '<span style="color:#ffb703; font-weight:600;"><i class="fas fa-clock"></i> In Review</span>' : ''}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    } catch (e) {
      listEl.innerHTML = `<div style="color:var(--accent-blood);">Error: ${e.message}</div>`;
    }
  }

  // 5. Render Blood Bank Portal (Manager View: Inventory & Inbound Requests)
  async renderBloodBankInventory() {
    const tableBody = document.getElementById('bb-inventory-table-body');
    if (!tableBody) return;

    try {
      const bb = await window.api.getBloodBank(1); // ABC Blood Bank
      tableBody.innerHTML = bb.inventory.map(item => `
        <tr>
          <td><span class="blood-badge">${item.blood_group}</span></td>
          <td><b>${item.component}</b></td>
          <td>
            <input type="number" min="0" max="100" value="${item.units_available}" id="inv-input-${item.blood_group}-${item.component}"
              style="width: 70px; padding: 6px; border-radius: 6px; background: var(--bg-tertiary); border: 1px solid var(--border-strong); color: #fff; font-weight: 700;">
          </td>
          <td>${new Date(item.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="window.app.saveInventoryItem('${item.blood_group}', '${item.component}')">
              Update Stock
            </button>
          </td>
        </tr>
      `).join('');
    } catch (e) {
      console.warn("Error loading blood bank inventory:", e);
    }
  }

  async saveInventoryItem(bloodGroup, component) {
    const input = document.getElementById(`inv-input-${bloodGroup}-${component}`);
    if (!input) return;
    const units = parseInt(input.value, 10);

    try {
      await window.api.updateBloodInventory(1, bloodGroup, component, units);
      window.appState.showToast("Inventory Updated", `Set ${bloodGroup} ${component} to ${units} units`, "📦");
    } catch (e) {
      alert(`Error updating inventory: ${e.message}`);
    }
  }

  async renderBloodBankRequests() {
    const container = document.getElementById('bb-requests-container');
    if (!container) return;

    try {
      const requests = await window.api.getAllReservationRequests();
      if (requests.length === 0) {
        container.innerHTML = '<div style="padding: 24px; color: var(--text-muted);">No reservation requests yet.</div>';
        return;
      }

      container.innerHTML = requests.map(r => `
        <div class="card" style="margin-bottom: 16px; border-left: 4px solid ${r.status === 'PENDING' ? '#ffb703' : (r.status === 'ACCEPTED' ? '#06d6a0' : '#e63946')};">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
              <div style="font-size:16px; font-weight:800; color:var(--text-primary);">
                Request #${r.id} — Patient: ${r.patient_name || 'Srijan'}
              </div>
              <div style="font-size:13px; color:var(--text-muted); margin-top:2px;">
                Contact: ${r.patient_phone || '+91 98300 12345'} • Hospital: ${r.hospital_name || 'CMRI Hospital'}
              </div>
            </div>
            <span class="status-badge status-${r.status.toLowerCase()}">${r.status}</span>
          </div>

          <div style="margin: 14px 0; padding: 10px 14px; background: var(--bg-tertiary); border-radius: var(--radius-md); display: flex; gap: 24px; font-size: 13.5px;">
            <div>Requested: <b style="color:var(--accent-blood);">${r.blood_group} ${r.component}</b></div>
            <div>Quantity: <b>${r.units} Unit(s)</b></div>
            <div>Date Needed: <b>${r.required_date}</b></div>
          </div>

          ${r.status === 'PENDING' ? `
            <div style="display:flex; gap:10px; justify-content:flex-end;">
              <button class="btn btn-secondary btn-sm" onclick="window.app.handleReservationDecision(${r.id}, 'REJECTED')">
                <i class="fas fa-times"></i> Reject
              </button>
              <button class="btn btn-success btn-sm" onclick="window.app.handleReservationDecision(${r.id}, 'ACCEPTED')">
                <i class="fas fa-check"></i> Accept & Reserve Stock
              </button>
            </div>
          ` : `
            <div style="font-size:12px; color:var(--text-muted); text-align:right;">
              Processed on ${new Date(r.updated_at).toLocaleString()}
            </div>
          `}
        </div>
      `).join('');
    } catch (e) {
      container.innerHTML = `<div style="color:var(--accent-blood);">Error: ${e.message}</div>`;
    }
  }

  async handleReservationDecision(reservationId, decision) {
    try {
      await window.api.updateReservationStatus(reservationId, decision);
      window.appState.showToast(
        decision === 'ACCEPTED' ? "Reservation Confirmed" : "Reservation Rejected",
        `Reservation #${reservationId} is now ${decision}. Inventory updated and push notification sent!`,
        decision === 'ACCEPTED' ? "✅" : "❌"
      );
      await this.renderBloodBankRequests();
    } catch (e) {
      alert(`Error updating reservation: ${e.message}`);
    }
  }

  // 6. Trackers: Transfusion & Chemotherapy (PDF Pages 7-8)
  async renderTreatments() {
    const listEl = document.getElementById('treatments-list');
    if (!listEl) return;

    try {
      const treatments = await window.api.getTreatments();
      listEl.innerHTML = treatments.map(t => {
        const isTransfusion = t.type.toUpperCase() === 'TRANSFUSION';
        return `
          <div class="card" style="margin-bottom: 16px;">
            <div class="card-header" style="margin-bottom:12px;">
              <div class="card-title">
                <i class="${isTransfusion ? 'fas fa-tint' : 'fas fa-dna'}" style="color:${isTransfusion ? 'var(--accent-blood)' : 'var(--accent-cyan)'};"></i>
                <span>${t.type}: ${isTransfusion ? `${t.blood_group} • ${t.expected_units} Units` : (t.cycle || 'Scheduled Cycle')}</span>
              </div>
              <span class="status-badge status-accepted">${t.status}</span>
            </div>
            <div style="font-size:13.5px; color:var(--text-secondary); margin-bottom:10px;">
              <div><b>Hospital:</b> ${t.hospital}</div>
              <div><b>Date & Time:</b> ${t.scheduled_date} at ${t.appointment_time || '10:00 AM'}</div>
              ${isTransfusion ? `<div><b>Transfusion Interval:</b> Every ${t.repeat_interval_days || 21} Days</div>` : ''}
              <div><b>Notes:</b> ${t.notes || t.hospital_provided_notes || 'Standard protocol'}</div>
            </div>
            ${isTransfusion ? `
              <div style="padding:10px 14px; background:rgba(230,57,70,0.1); border-radius:var(--radius-sm); border:1px solid rgba(230,57,70,0.2); font-size:12.5px; color:#ff8585;">
                <i class="fas fa-bell"></i> <b>Automated Reminder Schedule:</b> 7-day, 2-day, 1-day, and same-day notifications active.
              </div>
            ` : ''}
          </div>
        `;
      }).join('');
    } catch (e) {
      listEl.innerHTML = `<div style="color:var(--accent-blood);">Error: ${e.message}</div>`;
    }
  }

  // 7. Medicine Tracker & Dynamic Stock Calculator (PDF Page 8)
  async renderMedicines() {
    const listEl = document.getElementById('medicines-list');
    if (!listEl) return;

    try {
      const medicines = await window.api.getMedicines();
      listEl.innerHTML = medicines.map(m => {
        const pct = Math.max(5, Math.min(100, Math.round((m.remaining_quantity / m.initial_quantity) * 100)));
        const isLow = m.remaining_quantity <= 5;
        return `
          <div class="card" style="margin-bottom: 16px;">
            <div class="card-header" style="margin-bottom:8px;">
              <div class="card-title">
                <i class="fas fa-pills" style="color:var(--accent-blue);"></i>
                <span>${m.name} (${m.dosage})</span>
              </div>
              <span class="status-badge ${isLow ? 'status-rejected' : 'status-accepted'}">
                ${isLow ? '<i class="fas fa-exclamation-triangle"></i> Low Supply' : 'Adequate Supply'}
              </span>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:13px; color:var(--text-secondary); margin-bottom:6px;">
              <span>Daily Dose: <b>${m.frequency}</b> (at ${m.reminder_time})</span>
              <span>Stock Left: <b style="color:${isLow ? '#ff6b6b' : '#06d6a0'}; font-size:14px;">${m.remaining_quantity} / ${m.initial_quantity} tablets</b> (${m.days_left} days remaining)</span>
            </div>
            <div class="stock-progress-bar">
              <div class="stock-progress-fill ${isLow ? 'low' : ''}" style="width: ${pct}%;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px; font-size:12px; color:var(--text-muted);">
              <div><i class="fas fa-info-circle"></i> ${m.instructions || 'Take as instructed'}</div>
              <button class="btn btn-secondary btn-sm" onclick="window.app.takeMedicineDose(${m.id}, ${m.remaining_quantity})">
                <i class="fas fa-check"></i> Mark Dose Taken
              </button>
            </div>
          </div>
        `;
      }).join('');
    } catch (e) {
      listEl.innerHTML = `<div style="color:var(--accent-blood);">Error: ${e.message}</div>`;
    }
  }

  async takeMedicineDose(id, currentRemaining) {
    try {
      const nextRemaining = Math.max(0, currentRemaining - 1);
      await window.api.updateMedicine(id, { remaining_quantity: nextRemaining });
      window.appState.showToast("Dose Recorded", "Medicine dose logged and inventory decremented.", "💊");
      await this.renderMedicines();
    } catch (e) {
      alert(`Error recording dose: ${e.message}`);
    }
  }

  // 8. Critical Medicine / Albumin Tracker (PDF Page 8 Section 12)
  async renderCriticalMedicines() {
    const listEl = document.getElementById('critical-medicines-list');
    if (!listEl) return;

    try {
      const searchInput = document.getElementById('critical-med-search');
      const search = searchInput ? searchInput.value : '';
      const items = await window.api.getCriticalMedicines(search);

      listEl.innerHTML = items.map(c => `
        <div class="card" style="margin-bottom: 16px; border-left: 4px solid #8338ec;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
              <div style="font-size:16px; font-weight:800; color:var(--text-primary);">${c.name}</div>
              <div style="font-size:13px; color:var(--text-muted);"><i class="fas fa-hospital"></i> ${c.pharmacy_name} — ${c.address}</div>
            </div>
            <span class="bb-distance">${c.distance_km} km</span>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; padding-top:10px; border-top:1px solid var(--border-subtle);">
            <div style="font-size:14px; font-weight:700; color:#06d6a0;">
              <i class="fas fa-check-circle"></i> Available: <b>${c.units_available} Units</b>
            </div>
            <a href="tel:${c.phone}" class="btn btn-secondary btn-sm" style="text-decoration:none;">
              <i class="fas fa-phone"></i> Call Pharmacy (${c.phone})
            </a>
          </div>
        </div>
      `).join('');
    } catch (e) {
      listEl.innerHTML = `<div style="color:var(--accent-blood);">Error: ${e.message}</div>`;
    }
  }

  // 9. Caregiver Portal (PDF Page 8, 9)
  async renderCaregivers() {
    const listEl = document.getElementById('caregivers-list');
    if (!listEl) return;

    try {
      const caregivers = await window.api.getCaregivers();
      listEl.innerHTML = caregivers.map(cg => `
        <div class="card" style="margin-bottom: 14px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:15px; font-weight:700;">${cg.caregiver_name} (${cg.relationship})</div>
              <div style="font-size:12.5px; color:var(--text-muted);">
                <i class="fas fa-phone"></i> ${cg.phone} ${cg.email ? `• <i class="fas fa-envelope"></i> ${cg.email}` : ''}
              </div>
            </div>
            <span class="status-badge status-accepted"><i class="fas fa-link"></i> Linked & Active</span>
          </div>
        </div>
      `).join('');
    } catch (e) {
      listEl.innerHTML = `<div style="color:var(--accent-blood);">Error: ${e.message}</div>`;
    }
  }

  async addCaregiverFromModal() {
    const name = document.getElementById('cg-name').value;
    const relationship = document.getElementById('cg-relationship').value;
    const phone = document.getElementById('cg-phone').value;
    const email = document.getElementById('cg-email').value;

    if (!name || !phone) {
      alert("Please enter caregiver name and phone number");
      return;
    }

    try {
      await window.api.addCaregiver({ caregiver_name: name, relationship, phone, email });
      document.getElementById('caregiver-modal').classList.remove('active');
      window.appState.showToast("Caregiver Linked", `${name} added to shared notifications and critical care alerts.`, "👥");
      await this.renderCaregivers();
    } catch (e) {
      alert(`Error adding caregiver: ${e.message}`);
    }
  }

  // 10. AI Care Assistant Summary Modal (PDF Page 9, 13)
  async openAISummaryModal() {
    const modal = document.getElementById('ai-summary-modal');
    const contentEl = document.getElementById('ai-summary-modal-content');
    if (!modal || !contentEl) return;

    modal.classList.add('active');
    contentEl.innerHTML = '<div style="padding:20px; color:var(--text-muted);"><i class="fas fa-spinner fa-spin"></i> AI Care Assistant is compiling your safe daily care briefing...</div>';

    try {
      const summary = await window.api.getAIDailySummary();
      contentEl.innerHTML = `
        <div class="ai-header-badge">
          <i class="fas fa-robot"></i> LifeLink AI Care Summary
        </div>
        <div class="ai-content-text">${summary.ai_summary_text}</div>
        <div class="ai-safety-alert">
          <i class="fas fa-shield-alt"></i> <b>Safety Boundary:</b> ${summary.safety_disclaimer}
        </div>
      `;
    } catch (e) {
      contentEl.innerHTML = `<div style="color:var(--accent-blood);">Error loading AI summary: ${e.message}</div>`;
    }
  }

  closeAISummaryModal() {
    const modal = document.getElementById('ai-summary-modal');
    if (modal) modal.classList.remove('active');
  }

  // 11. Notifications Drawer & Alerts (PDF Page 4, 9)
  async loadNotifications(updateBadgeOnly = false) {
    try {
      const notifs = await window.api.getNotifications();
      window.appState.notifications = notifs;
      const unread = notifs.filter(n => !n.is_read).length;
      window.appState.unreadCount = unread;

      const badge = document.getElementById('nav-notif-badge');
      if (badge) {
        badge.innerText = unread > 0 ? unread : '';
        badge.style.display = unread > 0 ? 'inline-flex' : 'none';
      }

      if (!updateBadgeOnly && this.activeTab === 'notifications') {
        await this.renderNotificationsList();
      }
    } catch (e) {
      console.warn("Notifications refresh error:", e);
    }
  }

  async renderNotificationsList() {
    const container = document.getElementById('notifications-list');
    if (!container) return;

    try {
      const notifs = await window.api.getNotifications();
      if (notifs.length === 0) {
        container.innerHTML = '<div style="padding: 24px; color: var(--text-muted); text-align: center;">No notifications in your inbox.</div>';
        return;
      }

      container.innerHTML = notifs.map(n => `
        <div class="card" style="margin-bottom: 12px; opacity: ${n.is_read ? '0.75' : '1'}; border-left: 4px solid var(--accent-blood);">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
              <div style="font-size:14.5px; font-weight:700; color:var(--text-primary);">${n.title}</div>
              <div style="font-size:13px; color:var(--text-secondary); margin-top:4px;">${n.message}</div>
            </div>
            <span style="font-size:11px; color:var(--text-muted);">${new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        </div>
      `).join('');
    } catch (e) {
      container.innerHTML = `<div style="color:var(--accent-blood);">Error: ${e.message}</div>`;
    }
  }

  async markAllNotificationsRead() {
    try {
      await window.api.markAllNotificationsRead();
      await this.loadNotifications();
      window.appState.showToast("Inbox Cleared", "All notifications marked as read.", "📬");
    } catch (e) {}
  }

  handleQuickAction(action) {
    switch (action) {
      case 'find-blood':
        this.switchTab('blood');
        break;
      case 'medicines':
        this.switchTab('medicines');
        break;
      case 'treatment':
        this.switchTab('treatments');
        break;
      case 'caregiver':
        this.switchTab('caregivers');
        break;
    }
  }
}

window.app = new LifeLinkApp();
document.addEventListener('DOMContentLoaded', () => window.app.init());
