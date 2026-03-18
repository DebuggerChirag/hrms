const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// State
let currentPatient = null;

// Auth Elements
const authContainer = document.getElementById('auth-container');
const loginCard = document.getElementById('login-card');
const signupCard = document.getElementById('signup-card');
const mainApp = document.getElementById('main-app');

// Toggle Login / Signup
document.getElementById('showSignupBtn').addEventListener('click', () => {
  loginCard.classList.add('hidden');
  signupCard.classList.remove('hidden');
});
document.getElementById('showLoginBtn').addEventListener('click', () => {
  signupCard.classList.add('hidden');
  loginCard.classList.remove('hidden');
});

// Post Request Helper
async function postAPI(endpoint, data) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if(!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || "API Error");
  }
  return response.json();
}

// Signup Logic
const signupForm = document.getElementById('signupForm');
const signupResult = document.getElementById('signupResult');
signupForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    name: document.getElementById('signupName').value,
    email: document.getElementById('signupEmail').value,
    phone: document.getElementById('signupPhone').value,
    dob: document.getElementById('signupDob').value
  };
  try {
    const patient = await postAPI('/patients/signup', payload);
    signupResult.innerHTML = `
      <h3 style="color: var(--success-color); margin-bottom:10px;">Registration Successful!</h3>
      <p style="margin-bottom:10px;">Your automatically generated Policy Number is: <br/><strong style="font-size:1.6rem; color:var(--accent-color); letter-spacing:1px; display:block; margin-top:5px;">${patient.policy_number}</strong></p>
      <p style="font-size: 0.9rem;">Please save this policy number securely. You will need it to login.</p>
    `;
    signupResult.classList.remove('hidden');
    signupForm.reset();
  } catch(err) {
    signupResult.innerHTML = `<h3 style="color: var(--error-color);">Registration Failed</h3><p>${err.message}</p>`;
    signupResult.classList.remove('hidden');
  }
});

// Login Logic
const loginForm = document.getElementById('loginForm');
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    policy_number: document.getElementById('loginPolicy').value,
    dob: document.getElementById('loginDob').value
  };
  try {
    const patient = await postAPI('/patients/login', payload);
    currentPatient = patient;
    
    // Switch to Dashboard
    authContainer.classList.remove('active');
    authContainer.classList.add('hidden');
    mainApp.classList.remove('hidden');
    mainApp.classList.add('active');
    
    // Update Dashboard Header
    document.getElementById('welcomeSubtitle').textContent = `Policy: ${patient.policy_number}`;
    document.getElementById('headerPatientName').textContent = patient.name;
    
    // Switch to Submit Request View properly
    document.getElementById('new-request-view').classList.remove('hidden');
    document.getElementById('status-view').classList.add('hidden');
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector('.nav-item[data-target="new-request-view"]').classList.add('active');

    // Pre-fill refunds list
    renderRefunds();
  } catch(err) {
    alert("Login failed: " + err.message);
  }
});

// Logout
document.getElementById('logoutBtn').addEventListener('click', () => {
  currentPatient = null;
  mainApp.classList.remove('active');
  mainApp.classList.add('hidden');
  authContainer.classList.remove('hidden');
  authContainer.classList.add('active');
  loginForm.reset();
});

// Navigation Logic
document.querySelectorAll('.nav-item[data-target]').forEach(item => {
  item.addEventListener('click', (e) => {
    document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
    e.currentTarget.classList.add('active');
    document.querySelectorAll('.view').forEach(view => view.classList.add('hidden'));
    
    const targetId = e.currentTarget.getAttribute('data-target');
    const targetEl = document.getElementById(targetId);
    if(targetEl) {
       targetEl.classList.remove('hidden');
       targetEl.classList.add('active');
    }
    
    if(targetId === 'status-view') {
      renderRefunds(); // Fresh render on opening tab
    }
  });
});

// Refund Submission Logic
const refundForm = document.getElementById('refundForm');
const submitBtn = refundForm.querySelector('button[type="submit"]');
const submitLoader = document.getElementById('submitSpinner');
const btnText = submitBtn.querySelector('.btn-text');
const submitResult = document.getElementById('submitResult');
const fileInput = document.querySelector('.file-input');
const fileUploadDiv = document.querySelector('.file-upload');

fileInput.addEventListener('change', (e) => {
  if(e.target.files.length > 0) fileUploadDiv.classList.add('has-file');
  else fileUploadDiv.classList.remove('has-file');
});

refundForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  submitBtn.disabled = true;
  submitLoader.classList.remove('hidden');
  btnText.textContent = "Processing with AI...";
  submitResult.classList.add('hidden');

  const formData = new FormData(refundForm);
  // Add patient ID to form data
  formData.append('patient_id', currentPatient.id);

  try {
    const response = await fetch(`${API_BASE_URL}/refunds/submit`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    const data = await response.json();
    
    // Add to local state
    if(!currentPatient.refunds) currentPatient.refunds = [];
    currentPatient.refunds.push(data);
    
    submitResult.innerHTML = `
      <h3 style="color: var(--success-color);">Claim Request Processed!</h3>
      <p>Tracking ID: <strong>#${data.id}</strong></p>
      <div style="margin: 15px 0;">
        <span class="status-badge status-${data.status.toLowerCase()}">${data.status}</span>
      </div>
      <p style="font-size: 0.95rem;"><strong>AI Diagnostic Feedback:</strong> ${data.ai_decision_reason || "Pending review"}</p>
    `;
    submitResult.classList.remove('hidden');
    refundForm.reset();
    fileUploadDiv.classList.remove('has-file');
  } catch (error) {
    submitResult.innerHTML = `<h3 style="color: var(--error-color);">Submission Failed</h3><p>${error.message}</p>`;
    submitResult.classList.remove('hidden');
  } finally {
    submitBtn.disabled = false;
    submitLoader.classList.add('hidden');
    btnText.textContent = "Submit Claim";
  }
});

// Render Refunds
function renderRefunds() {
  const container = document.getElementById('refundsList');
  if(!currentPatient.refunds || currentPatient.refunds.length === 0) {
    container.innerHTML = `<div class="result-card" style="text-align:center;"><p>No refund claim history found.</p></div>`;
    return;
  }
  
  // Sort by created_at desc
  const sorted = [...currentPatient.refunds].sort((a,b) => new Date(b.created_at) - new Date(a.created_at));
  
  container.innerHTML = sorted.map(ref => `
    <div class="result-card" style="padding: 1.5rem;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
           <h3 style="margin-bottom:0.5rem; color: var(--text-primary); font-size: 1.2rem;">Claim #${ref.id}</h3>
           <p style="margin-bottom: 5px;"><strong>Request Amount:</strong> $${ref.amount_requested}</p>
           <p><strong>Clinical Reason:</strong> ${ref.reason}</p>
           <p style="font-size:0.85rem; margin-top:10px; color:var(--text-secondary);">${new Date(ref.created_at).toLocaleString()}</p>
        </div>
        <span class="status-badge status-${ref.status.toLowerCase()}">${ref.status}</span>
      </div>
      ${ref.ai_decision_reason ? `<div style="margin-top:15px; padding-top:15px; border-top:1px solid rgba(0,0,0,0.05);"><p style="font-size: 0.95rem;"><strong>AI Audit Note:</strong> ${ref.ai_decision_reason}</p></div>` : ''}
    </div>
  `).join('');
}
