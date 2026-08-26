/**
 * LifeLink State Manager
 * Handles active user roles, presets, notification audio, and event pub/sub
 */

class AppState {
  constructor() {
    this.currentRole = 'PATIENT'; // PATIENT, BLOOD_BANK, CAREGIVER, ADMIN
    this.currentUser = {
      name: 'Srijan',
      email: 'srijan@lifelink.org',
      role: 'PATIENT',
      blood_group: 'B+',
      location: 'Kolkata, West Bengal',
      condition_diagnosis: 'Thalassemia Major (Transfusion Dependent)'
    };
    this.activeBloodBankId = 1; // ABC Blood Bank
    this.bloodBanks = [];
    this.reservations = [];
    this.notifications = [];
    this.unreadCount = 0;
    this.activeReservationForDemo = null;
    this.audioContext = null;
  }

  // Preconfigured Demo Credentials (from PDF specifications)
  getDemoUsers() {
    return {
      PATIENT: {
        email: 'srijan@lifelink.org',
        password: 'patient123',
        name: 'Srijan',
        role: 'PATIENT',
        subtitle: 'Patient • Thalassemia Major (B+)'
      },
      BLOOD_BANK: {
        email: 'manager@abcbloodbank.org',
        password: 'bloodbank123',
        name: 'ABC Blood Bank & Research Centre',
        role: 'BLOOD_BANK',
        subtitle: 'Blood Bank Officer • Kolkata'
      },
      CAREGIVER: {
        email: 'anita.caregiver@lifelink.org',
        password: 'caregiver123',
        name: 'Anita Roy',
        role: 'CAREGIVER',
        subtitle: 'Caregiver • Mother of Srijan'
      },
      ADMIN: {
        email: 'admin@lifelink.org',
        password: 'admin123',
        name: 'System Administrator',
        role: 'ADMIN',
        subtitle: 'Platform Manager'
      }
    };
  }

  // Play subtle chime sound for push notifications
  playNotificationSound() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      if (!this.audioContext) {
        this.audioContext = new AudioContext();
      }
      const ctx = this.audioContext;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, now); // D5
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.15); // A5

      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 0.35);
    } catch (e) {
      console.warn("Audio playback not permitted yet:", e);
    }
  }

  showToast(title, message, icon = '🩸') {
    this.playNotificationSound();
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
      <div class="toast-icon">${icon}</div>
      <div class="toast-body">
        <h4>${title}</h4>
        <p>${message}</p>
      </div>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(40px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4500);
  }
}

window.appState = new AppState();
