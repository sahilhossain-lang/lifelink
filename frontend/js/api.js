/**
 * LifeLink API Client
 * Connects frontend to FastAPI backend with automatic JWT and token caching
 */

const API_BASE = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
  ? `${window.location.origin}/api`
  : '/api';

class LifeLinkAPI {
  constructor() {
    this.token = localStorage.getItem('lifelink_token') || null;
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('lifelink_token', token);
    } else {
      localStorage.removeItem('lifelink_token');
    }
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json'
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        let errorMsg = `HTTP Error ${response.status}`;
        try {
          const errData = await response.json();
          errorMsg = errData.detail || errorMsg;
        } catch (e) {}
        throw new Error(errorMsg);
      }
      return await response.json();
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  }

  // Auth endpoints
  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  }

  async register(userData) {
    const data = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  }

  async getMe() {
    return await this.request('/auth/me');
  }

  // Patient profile
  async getPatientProfile() {
    return await this.request('/patients/me');
  }

  async updatePatientProfile(data) {
    return await this.request('/patients/me', {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  // Blood & Blood Banks
  async searchBlood(bloodGroup, component = 'PRBC', location = 'Kolkata') {
    const encodedGroup = encodeURIComponent(bloodGroup);
    return await this.request(`/blood/search?blood_group=${encodedGroup}&component=${component}&location=${location}`);
  }

  async getBloodBanks() {
    return await this.request('/blood-banks');
  }

  async getBloodBank(id) {
    return await this.request(`/blood-banks/${id}`);
  }

  async updateBloodInventory(bankId, bloodGroup, component, units) {
    return await this.request(`/blood-banks/${bankId}/inventory`, {
      method: 'PUT',
      body: JSON.stringify({ blood_group: bloodGroup, component, units_available: units })
    });
  }

  // Blood Reservations
  async createReservation(data) {
    return await this.request('/reservations', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async getReservations(bloodBankId = null, status = null) {
    let url = '/reservations';
    const params = [];
    if (bloodBankId) params.push(`blood_bank_id=${bloodBankId}`);
    if (status) params.push(`status=${status}`);
    if (params.length > 0) url += `?${params.join('&')}`;
    return await this.request(url);
  }

  async getAllReservationRequests(bloodBankId = null) {
    let url = '/reservations/all-requests';
    if (bloodBankId) url += `?blood_bank_id=${bloodBankId}`;
    return await this.request(url);
  }

  async updateReservationStatus(id, status) {
    return await this.request(`/reservations/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status })
    });
  }

  // Treatments (Transfusion & Chemotherapy)
  async getTreatments() {
    return await this.request('/treatments');
  }

  async createTreatment(data) {
    return await this.request('/treatments', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async deleteTreatment(id) {
    return await this.request(`/treatments/${id}`, { method: 'DELETE' });
  }

  // Medicines
  async getMedicines() {
    return await this.request('/medicines');
  }

  async createMedicine(data) {
    return await this.request('/medicines', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateMedicine(id, data) {
    return await this.request(`/medicines/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }

  async deleteMedicine(id) {
    return await this.request(`/medicines/${id}`, { method: 'DELETE' });
  }

  // Caregivers
  async getCaregivers() {
    return await this.request('/caregivers');
  }

  async addCaregiver(data) {
    return await this.request('/caregivers', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async removeCaregiver(id) {
    return await this.request(`/caregivers/${id}`, { method: 'DELETE' });
  }

  // Notifications
  async getNotifications() {
    return await this.request('/notifications');
  }

  async markNotificationRead(id) {
    return await this.request(`/notifications/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_read: true })
    });
  }

  async markAllNotificationsRead() {
    return await this.request('/notifications/read-all', { method: 'POST' });
  }

  // AI Care Assistant
  async getAIDailySummary() {
    return await this.request('/ai/daily-summary');
  }

  // Critical Medicines (Albumin)
  async getCriticalMedicines(search = '') {
    const url = search ? `/critical-medicines?search=${encodeURIComponent(search)}` : '/critical-medicines';
    return await this.request(url);
  }
}

window.api = new LifeLinkAPI();
