import { requireRole, api, showToast, hydrateUserBadge, attachLogout, setGreeting, animateStagger } from './app.js';

const auth = requireRole([3]);
if (!auth) return;

hydrateUserBadge(auth);
attachLogout();
setGreeting();

const analyticsCards = document.querySelector('#analytics-cards');
const placementRate = document.querySelector('#placement-rate');
const branchStats = document.querySelector('#branch-stats');
const jobTypes = document.querySelector('#job-types');
const pendingUsersEl = document.querySelector('#pending-users');
const pendingJobsEl = document.querySelector('#pending-jobs');
const announcementsEl = document.querySelector('#admin-announcements');

async function loadData() {
  try {
    const [analytics, users, jobs, anns] = await Promise.all([
      api('/admin/analytics'),
      api('/admin/pending-users'),
      api('/admin/pending-jobs'),
      api('/admin/announcements'),
    ]);
    renderAnalytics(analytics || {});
    renderPendingUsers(users || []);
    renderPendingJobs(jobs || []);
    renderAnnouncements(anns || []);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function renderAnalytics(analytics) {
  const overall = analytics.overall || {};
  analyticsCards.innerHTML = `
    <div class="card animate"><p class="minor">Total Students</p><h2>${overall.total_students || 0}</h2></div>
    <div class="card animate"><p class="minor">Placed</p><h2>${overall.placed_students || 0}</h2></div>
    <div class="card animate"><p class="minor">Companies</p><h2>${overall.total_companies || 0}</h2></div>
    <div class="card animate"><p class="minor">Active Jobs</p><h2>${overall.total_jobs || 0}</h2></div>
  `;
  const rate = overall.placement_percentage || 0;
  placementRate.innerHTML = `
    <div class="card animate">
      <div class="section-title"><h3>Placement Rate</h3><span class="badge badge-green">${rate}%</span></div>
      <div class="progress" style="margin: 10px 0 4px;"><span style="width:${rate}%"></span></div>
      <p class="minor">${overall.placed_students || 0} of ${overall.total_students || 0} placed</p>
    </div>`;

  branchStats.innerHTML = (analytics.branch_wise || []).map(item => `
    <div class="card animate">
      <div class="section-title"><h4>${item.branch}</h4><span class="badge badge-blue">${item.placed}/${item.total}</span></div>
      <div class="chart-bar"><span style="width:${item.total ? (item.placed / item.total) * 100 : 0}%"></span></div>
    </div>
  `).join('') || '<p class="minor">No branch data.</p>';

  jobTypes.innerHTML = (analytics.job_types || []).map(j => `
    <div class="card animate">
      <div class="section-title"><h4>${j.type}</h4><span class="badge badge-amber">${j.count}</span></div>
      <div class="progress"><span style="width:${Math.min(j.count * 10, 100)}%"></span></div>
    </div>
  `).join('') || '<p class="minor">No job type data.</p>';
}

function renderPendingUsers(users) {
  pendingUsersEl.innerHTML = users.length ? users.map(user => `
    <div class="card animate" data-user-id="${user.id}">
      <div class="section-title">
        <h4>${user.role_id === 1 ? 'Student' : 'Company'}</h4>
        <span class="badge badge-amber">Pending</span>
      </div>
      <p class="minor">${user.email}</p>
      ${user.profile ? `<p class="minor">${user.role_id === 1 ? `${user.profile.full_name} • ${user.profile.branch}` : user.profile.company_name}</p>` : ''}
      <div class="inline-actions" style="margin-top:10px;">
        <button class="btn btn-primary" data-verify="${user.id}">Verify</button>
      </div>
    </div>
  `).join('') : '<p class="minor">No pending users.</p>';
}

pendingUsersEl?.addEventListener('click', async (e) => {
  const id = e.target.getAttribute('data-verify');
  if (!id) return;
  try {
    await api(`/admin/verify-user/${id}`, { method: 'PUT' });
    showToast('User verified', 'success');
    loadData();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

function renderPendingJobs(jobs) {
  pendingJobsEl.innerHTML = jobs.length ? jobs.map(job => `
    <div class="card animate" data-job-id="${job.id}">
      <div class="section-title">
        <h4>${job.title}</h4>
        <span class="badge badge-amber">${job.status}</span>
      </div>
      <p class="minor">${job.company_name} • ${job.location}</p>
      <p class="minor" style="margin:8px 0;">${job.description || '—'}</p>
      <div class="job-meta">
        <span>CGPA ${job.min_cgpa || 0}+</span>
        <span>Deadline ${new Date(job.application_deadline).toLocaleDateString()}</span>
      </div>
      <div class="inline-actions" style="margin-top:12px;">
        <button class="btn btn-primary" data-approve="${job.id}">Approve</button>
        <button class="btn btn-ghost" data-reject="${job.id}">Reject</button>
      </div>
    </div>
  `).join('') : '<p class="minor">No pending jobs.</p>';
}

pendingJobsEl?.addEventListener('click', async (e) => {
  const approveId = e.target.getAttribute('data-approve');
  const rejectId = e.target.getAttribute('data-reject');
  if (!approveId && !rejectId) return;
  const jobId = approveId || rejectId;
  const status = approveId ? 'Approved' : 'Rejected';
  try {
    await api(`/admin/approve-job/${jobId}`, { method: 'PUT', body: { status } });
    showToast(`Job ${status.toLowerCase()}`, 'success');
    loadData();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

function renderAnnouncements(list) {
  announcementsEl.innerHTML = list.length ? list.map(a => `
    <div class="card animate">
      <div class="section-title"><h4>${a.title}</h4><span class="badge badge-blue">${a.target_role ? (a.target_role === 1 ? 'Students' : 'Companies') : 'All'}</span></div>
      <p class="minor">${a.message}</p>
      <span class="badge badge-amber">${new Date(a.created_at).toLocaleDateString()}</span>
    </div>
  `).join('') : '<p class="minor">No announcements.</p>';
}

const annForm = document.querySelector('#announcement-form');
annForm?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = new FormData(annForm);
  const payload = {
    title: data.get('title'),
    message: data.get('message'),
    target_role: data.get('target_role') ? parseInt(data.get('target_role'), 10) : null,
  };
  const btn = annForm.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = 'Posting...';
  try {
    await api('/admin/announcements', { method: 'POST', body: payload });
    showToast('Announcement posted', 'success');
    annForm.reset();
    loadData();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create Announcement';
  }
});

loadData();
