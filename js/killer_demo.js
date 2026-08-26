/**
 * LifeLink Killer Demo Flow Controller
 * Implements the full step-by-step hackathon pitch demo (PDF Pages 10-11 & 14)
 */

class KillerDemoRunner {
  constructor() {
    this.currentStep = 0;
    this.demoSteps = [
      {
        title: "Step 1: Patient Login & Health Profile",
        desc: "Srijan logs in. Patient profile shows Thalassemia Major with Blood Group B+.",
        action: async () => {
          await window.app.switchRole('PATIENT');
          window.app.switchTab('home');
        }
      },
      {
        title: "Step 2: Patient Dashboard & Next Care Task",
        desc: "Notice the high-priority care card: 'Blood Transfusion on 05 September (B+ • 2 Units)' with action button [Arrange Blood].",
        action: async () => {
          window.app.switchTab('home');
        }
      },
      {
        title: "Step 3: Blood Search & Real-Time Availability",
        desc: "Patient searches for B+ PRBC in Kolkata. ABC Blood Bank shows 5 units available (2.7 km away).",
        action: async () => {
          window.app.switchTab('blood');
          document.getElementById('search-blood-group').value = 'B+';
          document.getElementById('search-component').value = 'PRBC';
          await window.app.performBloodSearch();
        }
      },
      {
        title: "Step 4: Request Blood Reservation (PENDING)",
        desc: "Patient reserves 2 units of B+ PRBC at ABC Blood Bank for 05 September 2026. Status begins in PENDING.",
        action: async () => {
          const banks = await window.api.searchBlood('B+', 'PRBC');
          const abc = banks.find(b => b.name.includes('ABC')) || banks[0];
          window.app.openReservationModal(abc.blood_bank_id, 'B+', 'PRBC', 2);
          // Auto submit after a brief delay
          setTimeout(async () => {
            await window.app.submitReservation();
            window.app.switchTab('reservations');
          }, 800);
        }
      },
      {
        title: "Step 5: Blood Bank Manager Portal",
        desc: "Switching to ABC Blood Bank portal. Officer sees the new inbound reservation request from Srijan.",
        action: async () => {
          await window.app.switchRole('BLOOD_BANK');
          window.app.switchTab('bloodbank-requests');
        }
      },
      {
        title: "Step 6: Blood Bank Accepts Request",
        desc: "Blood Bank Officer reviews and clicks ACCEPT. Inventory automatically decrements and real-time push alert is triggered!",
        action: async () => {
          const requests = await window.api.getAllReservationRequests();
          const pending = requests.find(r => r.status === 'PENDING') || requests[0];
          if (pending) {
            await window.app.handleReservationDecision(pending.id, 'ACCEPTED');
          }
        }
      },
      {
        title: "Step 7: Patient & Caregiver Notification Alert",
        desc: "Switching back to Patient. Live notification delivered: 'Blood Reservation Accepted!' and Caregiver Anita alerted.",
        action: async () => {
          await window.app.switchRole('PATIENT');
          window.app.switchTab('home');
          await window.app.loadNotifications();
        }
      },
      {
        title: "Step 8: AI Care Assistant Summary Updated",
        desc: "AI Care Assistant summarizes the day's tasks safely, verifying the blood reservation is confirmed for the 05 Sep transfusion!",
        action: async () => {
          window.app.openAISummaryModal();
        }
      }
    ];
  }

  startDemo() {
    this.currentStep = 0;
    const overlay = document.getElementById('demo-stepper-overlay');
    if (overlay) overlay.style.display = 'block';
    this.renderStep();
  }

  stopDemo() {
    const overlay = document.getElementById('demo-stepper-overlay');
    if (overlay) overlay.style.display = 'none';
    this.currentStep = 0;
  }

  async renderStep() {
    const step = this.demoSteps[this.currentStep];
    if (!step) {
      this.stopDemo();
      return;
    }

    const titleEl = document.getElementById('demo-step-title');
    const descEl = document.getElementById('demo-step-desc');
    const stepCounterEl = document.getElementById('demo-step-counter');

    if (titleEl) titleEl.innerText = step.title;
    if (descEl) descEl.innerText = step.desc;
    if (stepCounterEl) stepCounterEl.innerText = `Step ${this.currentStep + 1} of ${this.demoSteps.length}`;

    // Execute step action
    await step.action();
  }

  async nextStep() {
    if (this.currentStep < this.demoSteps.length - 1) {
      this.currentStep++;
      await this.renderStep();
    } else {
      window.appState.showToast("Demo Completed", "Full end-to-end LifeLink hackathon workflow demonstrated!", "🏆");
      this.stopDemo();
    }
  }

  async prevStep() {
    if (this.currentStep > 0) {
      this.currentStep--;
      await this.renderStep();
    }
  }
}

window.killerDemo = new KillerDemoRunner();
