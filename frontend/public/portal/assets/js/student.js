import { requireRole, api, showToast, hydrateUserBadge, attachLogout, setGreeting, animateStagger } from './app.js';

const auth = requireRole([1]);
if (!auth) return;

hydrateUserBadge(auth);
attachLogout();
setGreeting();

const statsEl = document.querySelector('#stats');
const jobsEl = document.querySelector('#jobs-list');
const announcementsEl = document.querySelector('#announcements');
const applicationsEl = document.querySelector('#applications');

let jobs = [];
let applications = [];

async function loadEverything() {
  try {
    const [jobsRes, appsRes, annRes] = await Promise.all([
      api('/student/jobs'),
      api('/student/applications'),
      api('/announcements'),
    ]);
    jobs = jobsRes || [];
    applications = appsRes || [];
    renderStats();
    renderJobs();
    renderAnnouncements(annRes || []);
    renderApplications();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function renderStats() {
  const eligible = jobs.filter(j => !j.has_applied).length;
  const applied = applications.length;
  const shortlisted = applications.filter(a => a.status === 'Shortlisted' || a.status === 'Interview').length;
  const selected = applications.filter(a => a.status === 'Selected').length;
  statsEl.innerHTML = `
    <div class="card animate">
      <p class="minor">Eligible Jobs</p>
      <h2>${eligible}</h2>
    </div>
    <div class="card animate">
      <p class="minor">Applications</p>
      <h2>${applied}</h2>
    </div>
    <div class="card animate">
      <p class="minor">Shortlisted / Interview</p>
      <h2>${shortlisted}</h2>
    </div>
    <div class="card animate">
      <p class="minor">Selected</p>
      <h2>${selected}</h2>
    </div>`;
}

function renderJobs() {
  jobsEl.innerHTML = jobs.map(job => `
    <article class="job-card animate" data-job-id="${job.id}">
      <div class="inline-actions" style="justify-content: space-between; align-items: flex-start;">
        <div>
          <h3>${job.title}</h3>
          <div class="job-meta">${job.company_name || 'Company'} • ${job.location}</div>
        </div>
        <span class="badge ${job.job_type === 'Internship' ? 'badge-amber' : 'badge-blue'}">${job.job_type}</span>
      </div>
      <p class="minor" style="margin: 10px 0;">${job.description || 'No description provided.'}</p>
      <div class="job-meta">
        <span>CGPA ${job.min_cgpa || 0}+</span>
        <span>Deadline ${new Date(job.application_deadline).toLocaleDateString()}</span>
        ${job.salary_range ? `<span>${job.salary_range}</span>` : ''}
      </div>
      <div class="job-meta">${job.requirements || ''}</div>
      <div class="inline-actions" style="margin-top: 12px;">
        ${job.has_applied ? `<span class="badge badge-green">Applied</span>` : `<button class="btn btn-primary" data-apply="${job.id}">Apply</button>`}
        <span class="chip">${job.job_type}</span>
      </div>
    </article>
  `).join('');
  animateStagger('.job-card');
}

jobsEl?.addEventListener('click', async (e) => {
  const applyId = e.target.getAttribute('data-apply');
  if (!applyId) return;
  const btn = e.target;
  btn.disabled = true;
  btn.textContent = 'Applying...';
  try {
    await api(`/student/apply/${applyId}`, { method: 'POST' });
    showToast('Application submitted', 'success');
    await loadEverything();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Apply';
  }
});

function renderAnnouncements(list) {
  announcementsEl.innerHTML = list.length ? list.map(item => `
    <div class="card animate">
      <h4>${item.title}</h4>
      <p class="minor" style="margin: 6px 0 12px;">${item.message}</p>
      <span class="badge badge-amber">${new Date(item.created_at).toLocaleDateString()}</span>
    </div>
  `).join('') : '<p class="minor">No announcements right now.</p>';
  animateStagger('#announcements .card');
}

function renderApplications() {
  const byStatus = ['Applied', 'Shortlisted', 'Interview', 'Selected', 'Rejected'];
  applicationsEl.innerHTML = byStatus.map(status => {
    const group = applications.filter(a => a.status === status);
    return `
      <div class="card animate">
        <div class="section-title">
          <h4>${status}</h4>
          <span class="badge badge-blue">${group.length}</span>
        </div>
        <div class="app-grid">
          ${group.map(app => `
            <div class="app-card">
              <h4>${app.job_title}</h4>
              <p class="minor">${app.company_name}</p>
              <div class="chip">Applied ${new Date(app.applied_at).toLocaleDateString()}</div>
            </div>
          `).join('') || '<p class="minor">No applications here yet.</p>'}
        </div>
      </div>`;
  }).join('');
  animateStagger('#applications .card');
}

// ==================== Profile Management ====================
const profileView = document.querySelector('#profile-view');
const dashboardView = document.querySelector('#dashboard-view');
const navDashboard = document.querySelector('#nav-dashboard');
const navProfile = document.querySelector('#nav-profile');
const editProfileBtn = document.querySelector('#edit-profile-btn');
const saveProfileBtn = document.querySelector('#save-profile-btn');
const cancelEditBtn = document.querySelector('#cancel-edit-btn');
const uploadResumeBtn = document.querySelector('#upload-resume-btn');
const resumeUploadInput = document.querySelector('#resume-upload');
const profileForm = document.querySelector('#profile-form');

let isEditing = false;
let studentProfile = null;

// Navigation between views
navDashboard.addEventListener('click', (e) => {
  e.preventDefault();
  dashboardView.style.display = 'block';
  profileView.style.display = 'none';
  navDashboard.classList.add('active');
  navProfile.classList.remove('active');
});

navProfile.addEventListener('click', (e) => {
  e.preventDefault();
  dashboardView.style.display = 'none';
  profileView.style.display = 'block';
  navDashboard.classList.remove('active');
  navProfile.classList.add('active');
  loadProfile();
});

// Load profile data
async function loadProfile() {
  try {
    const profile = await api('/student/profile');
    studentProfile = profile;
    populateProfileForm(profile);
    updateResumeStatus(profile.resume_url);
  } catch (err) {
    showToast('Failed to load profile: ' + err.message, 'error');
  }
}

// Populate form with profile data
function populateProfileForm(profile) {
  document.querySelector('#full_name').value = profile.full_name || '';
  document.querySelector('#enrollment_number').value = profile.enrollment_number || '';
  document.querySelector('#phone').value = profile.phone || '';
  document.querySelector('#branch').value = profile.branch || '';
  document.querySelector('#cgpa').value = profile.cgpa || '';
  document.querySelector('#graduation_year').value = profile.graduation_year || '';
  document.querySelector('#tenth_percentage').value = profile.tenth_percentage || '';
  document.querySelector('#twelfth_percentage').value = profile.twelfth_percentage || '';
  document.querySelector('#linkedin_url').value = profile.linkedin_url || '';
  document.querySelector('#github_url').value = profile.github_url || '';
  document.querySelector('#skills').value = profile.skills || '';
  document.querySelector('#experience').value = profile.experience || '';
  document.querySelector('#projects').value = profile.projects || '';
  document.querySelector('#certifications').value = profile.certifications || '';
}

// Update resume status display
function updateResumeStatus(resumeUrl) {
  const resumeStatus = document.querySelector('#resume-status');
  const resumeLink = document.querySelector('#resume-link');
  
  if (resumeUrl) {
    resumeStatus.textContent = '✅ Resume uploaded';
    resumeStatus.style.color = '#10b981';
    resumeLink.href = 'http://localhost:5000' + resumeUrl;
    resumeLink.style.display = 'inline-block';
  } else {
    resumeStatus.textContent = 'No resume uploaded yet';
    resumeStatus.style.color = '#6b7280';
    resumeLink.style.display = 'none';
    document.querySelector('#resume-parse-info').style.display = 'block';
  }
}

// Edit profile
editProfileBtn.addEventListener('click', () => {
  isEditing = true;
  enableFormInputs(true);
  editProfileBtn.style.display = 'none';
  saveProfileBtn.style.display = 'inline-block';
  cancelEditBtn.style.display = 'inline-block';
});

// Cancel edit
cancelEditBtn.addEventListener('click', () => {
  isEditing = false;
  enableFormInputs(false);
  editProfileBtn.style.display = 'inline-block';
  saveProfileBtn.style.display = 'none';
  cancelEditBtn.style.display = 'none';
  if (studentProfile) {
    populateProfileForm(studentProfile);
  }
});

// Enable/disable form inputs
function enableFormInputs(enable) {
  const inputs = profileForm.querySelectorAll('input, textarea');
  inputs.forEach(input => {
    if (input.id !== 'enrollment_number' && input.id !== 'branch' && input.id !== 'graduation_year') {
      input.disabled = !enable;
    }
  });
}

// Save profile
saveProfileBtn.addEventListener('click', async () => {
  try {
    const formData = {
      full_name: document.querySelector('#full_name').value,
      phone: document.querySelector('#phone').value,
      cgpa: parseFloat(document.querySelector('#cgpa').value),
      tenth_percentage: parseFloat(document.querySelector('#tenth_percentage').value) || null,
      twelfth_percentage: parseFloat(document.querySelector('#twelfth_percentage').value) || null,
      linkedin_url: document.querySelector('#linkedin_url').value,
      github_url: document.querySelector('#github_url').value,
      skills: document.querySelector('#skills').value,
      experience: document.querySelector('#experience').value,
      projects: document.querySelector('#projects').value,
      certifications: document.querySelector('#certifications').value
    };

    const updated = await api('/student/profile', 'PUT', formData);
    studentProfile = updated;
    
    isEditing = false;
    enableFormInputs(false);
    editProfileBtn.style.display = 'inline-block';
    saveProfileBtn.style.display = 'none';
    cancelEditBtn.style.display = 'none';
    
    showToast('Profile updated successfully!', 'success');
  } catch (err) {
    showToast('Failed to update profile: ' + err.message, 'error');
  }
});

// Resume upload
uploadResumeBtn.addEventListener('click', () => {
  resumeUploadInput.click();
});

resumeUploadInput.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  try {
    uploadResumeBtn.disabled = true;
    uploadResumeBtn.innerHTML = '<span>⏳ Uploading...</span>';

    const formData = new FormData();
    formData.append('resume', file);

    const token = localStorage.getItem('token');
    const response = await fetch('http://localhost:5000/api/student/upload-resume', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Upload failed');
    }

    const result = await response.json();
    showToast(result.message, 'success');
    
    // Update resume status
    updateResumeStatus(result.resume_url);
    document.querySelector('#resume-parse-info').style.display = 'none';

    // Auto-fill form with parsed data
    if (result.parsed_data && Object.keys(result.parsed_data).length > 0) {
      showToast('Auto-filling profile from resume...', 'info');
      await autofillFromParsedData(result.parsed_data);
    }

    // Reload profile
    await loadProfile();

  } catch (err) {
    showToast('Upload failed: ' + err.message, 'error');
  } finally {
    uploadResumeBtn.disabled = false;
    uploadResumeBtn.innerHTML = '<span>📤 Upload Resume</span>';
    resumeUploadInput.value = '';
  }
});

// Auto-fill form from parsed resume data
async function autofillFromParsedData(parsedData) {
  const fieldsToUpdate = {};
  
  if (parsedData.phone) fieldsToUpdate.phone = parsedData.phone;
  if (parsedData.cgpa) fieldsToUpdate.cgpa = parsedData.cgpa;
  if (parsedData.tenth_percentage) fieldsToUpdate.tenth_percentage = parsedData.tenth_percentage;
  if (parsedData.twelfth_percentage) fieldsToUpdate.twelfth_percentage = parsedData.twelfth_percentage;
  if (parsedData.skills) fieldsToUpdate.skills = parsedData.skills;
  if (parsedData.experience) fieldsToUpdate.experience = parsedData.experience;
  if (parsedData.projects) fieldsToUpdate.projects = parsedData.projects;
  if (parsedData.certifications) fieldsToUpdate.certifications = parsedData.certifications;
  if (parsedData.linkedin_url) fieldsToUpdate.linkedin_url = parsedData.linkedin_url;
  if (parsedData.github_url) fieldsToUpdate.github_url = parsedData.github_url;

  if (Object.keys(fieldsToUpdate).length > 0) {
    try {
      await api('/student/profile', 'PUT', fieldsToUpdate);
      showToast('Profile updated with resume data!', 'success');
    } catch (err) {
      console.error('Failed to auto-update profile:', err);
    }
  }
}

loadEverything();
