import { requireRole, api, showToast, hydrateUserBadge, attachLogout, setGreeting, animateStagger } from './app.js';

const auth = requireRole([2]);
if (!auth) return;

hydrateUserBadge(auth);
attachLogout();
setGreeting();

const jobsEl = document.querySelector('#company-jobs');
const statsEl = document.querySelector('#company-stats');
const annEl = document.querySelector('#company-announcements');
const applicantsEl = document.querySelector('#applicants-table');
const applicantsTitle = document.querySelector('#applicants-title');

let jobs = [];
let announcements = [];
let currentJobId = null;

async function loadAll() {
  try {
    const [jobsRes, annRes] = await Promise.all([
      api('/company/jobs'),
      api('/announcements'),
    ]);
    jobs = jobsRes || [];
    announcements = annRes || [];
    renderStats();
    renderJobs();
    renderAnnouncements();
    if (jobs[0]) selectJob(jobs[0].id, false);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function renderStats() {
  const total = jobs.length;
  const active = jobs.filter(j => j.status === 'Approved').length;
  const pending = jobs.filter(j => j.status === 'Pending').length;
  const closed = jobs.filter(j => j.status === 'Closed').length;
  statsEl.innerHTML = `
    <div class="card animate"><p class="minor">Total Jobs</p><h2>${total}</h2></div>
    <div class="card animate"><p class="minor">Active</p><h2>${active}</h2></div>
    <div class="card animate"><p class="minor">Pending</p><h2>${pending}</h2></div>
    <div class="card animate"><p class="minor">Closed</p><h2>${closed}</h2></div>
  `;
}

function renderJobs() {
  jobsEl.innerHTML = jobs.map(job => `
    <article class="job-card animate" data-job-id="${job.id}">
      <div class="inline-actions" style="justify-content: space-between; align-items: flex-start;">
        <div>
          <h3>${job.title}</h3>
          <div class="job-meta">${job.job_type} • ${job.location}</div>
        </div>
        <span class="badge ${badgeByStatus(job.status)}">${job.status}</span>
      </div>
      <p class="minor" style="margin: 10px 0;">${job.description || '—'}</p>
      <div class="job-meta">
        <span>CGPA ${job.min_cgpa || 0}+</span>
        ${job.salary_range ? `<span>${job.salary_range}</span>` : ''}
        <span>Deadline ${new Date(job.application_deadline).toLocaleDateString()}</span>
      </div>
      <div class="inline-actions" style="margin-top: 12px;">
        <button class="btn btn-ghost" data-view-applicants="${job.id}">View applicants</button>
      </div>
    </article>
  `).join('');
  animateStagger('.job-card');
}

function badgeByStatus(status) {
  if (status === 'Approved') return 'badge-green';
  if (status === 'Pending') return 'badge-amber';
  if (status === 'Closed') return 'badge-blue';
  return 'badge-red';
}

jobsEl?.addEventListener('click', (e) => {
  const jobId = e.target.getAttribute('data-view-applicants');
  if (jobId) selectJob(jobId, true);
});

async function selectJob(jobId, showToastFlag = false) {
  currentJobId = jobId;
  applicantsTitle.textContent = `Applicants for Job #${jobId}`;
  try {
    const list = await api(`/company/job/${jobId}/applicants`);
    renderApplicants(list || []);
    if (showToastFlag) showToast('Loaded applicants', 'info');
  } catch (err) {
    applicantsEl.innerHTML = `<tr><td colspan="7" class="minor">${err.message}</td></tr>`;
  }
}

function renderAnnouncements() {
  annEl.innerHTML = announcements.length ? announcements.map(a => `
    <div class="card animate">
      <h4>${a.title}</h4>
      <p class="minor">${a.message}</p>
      <span class="badge badge-amber">${new Date(a.created_at).toLocaleDateString()}</span>
    </div>
  `).join('') : '<p class="minor">No announcements.</p>';
}

function renderApplicants(list) {
  applicantsEl.innerHTML = list.length ? list.map(app => `
    <tr>
      <td>${app.full_name}</td>
      <td class="minor">${app.branch || '—'}</td>
      <td>${app.cgpa ?? '—'}</td>
      <td>${app.phone || '—'}</td>
      <td class="minor">${(app.skills || '').slice(0, 40)}</td>
      <td class="minor">${new Date(app.applied_at).toLocaleDateString()}</td>
      <td>
        <select data-status="${app.application_id}" value="${app.application_status}">
          ${['Applied','Shortlisted','Interview','Selected','Rejected'].map(opt => `<option value="${opt}" ${opt===app.application_status ? 'selected' : ''}>${opt}</option>`).join('')}
        </select>
      </td>
    </tr>
  `).join('') : '<tr><td colspan="7" class="minor">No applicants yet.</td></tr>';
}

applicantsEl?.addEventListener('change', async (e) => {
  const appId = e.target.getAttribute('data-status');
  if (!appId) return;
  const newStatus = e.target.value;
  try {
    await api('/company/applicant-status', { method: 'PUT', body: { application_id: appId, status: newStatus } });
    showToast('Status updated', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
});

const form = document.querySelector('#job-form');
form?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  payload.min_cgpa = parseFloat(payload.min_cgpa || 0);
  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Posting...';
  try {
    await api('/company/jobs', { method: 'POST', body: payload });
    showToast('Job posted (pending approval)', 'success');
    form.reset();
    await loadAll();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Post Job';
  }
});

loadAll();
