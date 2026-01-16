/**
 * Dashboard Widget Manager
 * Coordinates all dashboard components and data flow
 */

class DashboardManager {
  constructor(auth) {
    this.auth = auth;
    this.API_BASE = 'http://localhost:5000/api';
    this.widgets = {};
    this.cache = {};
  }

  async api(path, opts = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (this.auth?.token) headers.Authorization = `Bearer ${this.auth.token}`;
    const resp = await fetch(`${this.API_BASE}${path}`, {
      method: opts.method || 'GET',
      headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    }).catch(networkError => {
      throw new Error('Cannot connect to server. Please ensure the backend is running on http://localhost:5000');
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Request failed');
    return data;
  }

  showToast(msg, type = 'info') {
    let stack = document.getElementById('toast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.id = 'toast-stack';
      stack.className = 'toast-stack';
      document.body.appendChild(stack);
    }
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = msg;
    stack.appendChild(t);
    setTimeout(() => t.remove(), 4200);
  }

  registerWidget(name, widget) {
    this.widgets[name] = widget;
  }

  async initializeAll() {
    try {
      // Load all widget data in parallel
      const results = await Promise.all([
        this.api('/student/dashboard-summary'),
        this.api('/student/applications-summary'),
        this.api('/student/notifications?unread=true'),
        this.api('/student/company-visits/upcoming'),
        this.api('/student/interview-experiences/recent'),
      ]);

      const [summary, applications, notifications, visits, interviews] = results;

      // Initialize widgets with data
      if (this.widgets.driveFeed) {
        await this.widgets.driveFeed.render(visits);
      }
      if (this.widgets.kanbanBoard) {
        await this.widgets.kanbanBoard.render(applications);
      }
      if (this.widgets.notificationCenter) {
        await this.widgets.notificationCenter.render(notifications);
      }
      if (this.widgets.interviewRepo) {
        await this.widgets.interviewRepo.render(interviews);
      }

      console.log('Dashboard loaded successfully');
    } catch (err) {
      console.error('Dashboard init error:', err);
      this.showToast(err.message, 'error');
    }
  }

  markNotificationRead(notificationId) {
    this.api(`/student/notifications/${notificationId}/read`, { method: 'PUT' })
      .catch(err => console.error('Mark read error:', err));
  }
}

/**
 * WIDGET 1: LIVE DRIVE FEED
 * Shows visiting companies with skill matching logic
 */
class DriveFeedWidget {
  constructor(containerId, manager) {
    this.container = document.querySelector(containerId);
    this.manager = manager;
  }

  async render(visits) {
    if (!this.container) return;
    if (!visits || visits.length === 0) {
      this.container.innerHTML = '<p class="minor">No upcoming company visits scheduled</p>';
      return;
    }

    this.container.innerHTML = visits.map(visit => this.createVisitCard(visit)).join('');
    this.attachEventListeners();
  }

  createVisitCard(visit) {
    const eligibility = this.checkEligibility(visit);
    const badgeClass = eligibility.eligible ? 'badge-green' : 'badge-red';
    const badgeText = eligibility.eligible ? '✓ Eligible' : '✗ Not Eligible';

    return `
      <div class="card job-card animate" data-visit-id="${visit.id}">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
          <div>
            <h3>${visit.company_name}</h3>
            <div class="job-meta">${visit.recruitment_type} • ${new Date(visit.visit_date).toLocaleDateString()}</div>
          </div>
          <span class="badge ${badgeClass}">${badgeText}</span>
        </div>
        <p class="minor">${visit.description || 'No description provided'}</p>
        <div class="job-meta">
          <span>📍 ${visit.location || 'TBD'}</span>
          <span>💰 ${visit.expected_ctc_range || 'Salary TBD'}</span>
          <span>🕐 ${visit.visit_time || 'Time TBD'}</span>
        </div>
        ${eligibility.missingSkills.length > 0 ? `
          <div class="chip" style="margin-top: 8px; padding: 10px; background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3);">
            <strong style="color: #dc2626;">Missing Skills:</strong> ${eligibility.missingSkills.join(', ')}
          </div>
        ` : ''}
        <div class="inline-actions" style="margin-top: 10px; gap: 8px;">
          <button class="btn btn-primary" data-register-visit="${visit.id}">Register Interest</button>
          <button class="btn btn-ghost" data-view-details="${visit.id}">View Details</button>
        </div>
      </div>
    `;
  }

  checkEligibility(visit) {
    // Mock implementation - in production, fetch actual student skills
    const studentSkills = JSON.parse(localStorage.getItem('student_skills') || '["JavaScript", "Python", "React"]');
    const requiredSkills = visit.eligibility_criteria ? visit.eligibility_criteria.split(',').map(s => s.trim()) : [];
    
    const missingSkills = requiredSkills.filter(skill => !studentSkills.some(s => s.toLowerCase().includes(skill.toLowerCase())));
    const eligible = missingSkills.length === 0 || requiredSkills.length === 0;

    return { eligible, missingSkills };
  }

  attachEventListeners() {
    this.container.querySelectorAll('[data-register-visit]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const visitId = e.target.getAttribute('data-register-visit');
        this.registerInterest(visitId);
      });
    });

    this.container.querySelectorAll('[data-view-details]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const visitId = e.target.getAttribute('data-view-details');
        alert(`Showing details for visit ${visitId}`);
      });
    });
  }

  async registerInterest(visitId) {
    try {
      await this.manager.api(`/student/company-visits/${visitId}/register`, { method: 'POST' });
      this.manager.showToast('Interest registered successfully', 'success');
    } catch (err) {
      this.manager.showToast(err.message, 'error');
    }
  }
}

/**
 * WIDGET 2: APPLICATION KANBAN BOARD
 * Status tracking with drag-and-drop
 */
class KanbanBoardWidget {
  constructor(containerId, manager) {
    this.container = document.querySelector(containerId);
    this.manager = manager;
    this.statuses = ['Applied', 'Shortlisted', 'Interview', 'Selected'];
  }

  async render(applications) {
    if (!this.container) return;
    
    const grouped = this.groupByStatus(applications || []);
    const html = this.statuses.map(status => this.createColumn(status, grouped[status] || [])).join('');
    this.container.innerHTML = `<div class="kanban-board">${html}</div>`;
    this.attachEventListeners();
  }

  groupByStatus(applications) {
    return applications.reduce((acc, app) => {
      const status = app.status || 'Applied';
      if (!acc[status]) acc[status] = [];
      acc[status].push(app);
      return acc;
    }, {});
  }

  createColumn(status, apps) {
    return `
      <div class="kanban-column card glass">
        <div class="kanban-header">
          <h3>${status}</h3>
          <span class="badge badge-blue">${apps.length}</span>
        </div>
        <div class="kanban-cards" data-status="${status}">
          ${apps.map(app => this.createCard(app)).join('') || '<p class="minor">No applications</p>'}
        </div>
      </div>
    `;
  }

  createCard(app) {
    const rounds = Array.isArray(app.rounds) ? [...app.rounds].sort((a, b) => (a.sequence || 0) - (b.sequence || 0)) : [];
    const progress = typeof app.progress_pct === 'number' ? app.progress_pct : 0;
    const roundSteps = rounds.map(r => this.renderRoundStep(r)).join('');

    return `
      <div class="kanban-card animate" data-app-id="${app.id}" draggable="true">
        <h4>${app.job_title}</h4>
        <p class="minor">${app.company_name}</p>
        <div class="inline-actions" style="gap: 4px; margin-top: 8px;">
          <span class="chip" style="font-size: 11px;">Applied ${new Date(app.applied_at).toLocaleDateString()}</span>
          ${app.rounds_total ? `<span class="chip" style="font-size: 11px;">${app.rounds_cleared}/${app.rounds_total} rounds</span>` : ''}
        </div>
        <div class="progress" style="margin-top: 10px; height: 8px; background: rgba(255,255,255,0.06); border-radius: 999px; overflow: hidden;">
          <div style="width: ${progress}%; height: 100%; background: linear-gradient(90deg, #22c55e, #3b82f6);"></div>
        </div>
        ${roundSteps ? `<div class="round-stepper" style="display:flex; gap:6px; flex-wrap:wrap; margin-top:10px;">${roundSteps}</div>` : ''}
        <button class="btn btn-ghost" data-view-app="${app.id}" style="width: 100%; margin-top: 10px; padding: 6px; font-size: 12px;">View</button>
      </div>
    `;
  }

  renderRoundStep(round) {
    const status = (round.status || 'Pending').toLowerCase();
    const palette = {
      pending: { bg: 'rgba(255,255,255,0.04)', fg: '#cbd5e1', border: 'rgba(255,255,255,0.08)' },
      scheduled: { bg: 'rgba(59,130,246,0.12)', fg: '#93c5fd', border: 'rgba(59,130,246,0.3)' },
      completed: { bg: 'rgba(16,185,129,0.12)', fg: '#6ee7b7', border: 'rgba(16,185,129,0.3)' },
      passed: { bg: 'rgba(16,185,129,0.12)', fg: '#6ee7b7', border: 'rgba(16,185,129,0.3)' },
      failed: { bg: 'rgba(248,113,113,0.12)', fg: '#fecdd3', border: 'rgba(248,113,113,0.3)' },
    };
    const theme = palette[status] || palette.pending;
    return `
      <span class="chip" style="background:${theme.bg}; color:${theme.fg}; border-color:${theme.border}; font-size:11px;">
        ${round.sequence ? `${round.sequence}. ` : ''}${round.name || 'Round'}
      </span>
    `;
  }

  attachEventListeners() {
    this.container.querySelectorAll('[data-view-app]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const appId = e.target.getAttribute('data-view-app');
        console.log('View application:', appId);
      });
    });

    // Drag and drop mock (implement real drag-drop as needed)
    const cards = this.container.querySelectorAll('[draggable="true"]');
    cards.forEach(card => {
      card.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('appId', card.getAttribute('data-app-id'));
      });
    });
  }
}

/**
 * WIDGET 3: NOTIFICATION CENTER
 * Real-time alerts and updates
 */
class NotificationCenterWidget {
  constructor(containerId, manager) {
    this.container = document.querySelector(containerId);
    this.manager = manager;
    this.notificationTypeIcons = {
      interview_schedule: '📅',
      application_update: '📝',
      job_match: '🎯',
      company_visit: '🏢',
      announcement: '📢',
      skill_alert: '⚡',
    };
  }

  async render(notifications) {
    if (!this.container) return;
    
    if (!notifications || notifications.length === 0) {
      this.container.innerHTML = '<p class="minor">No new notifications</p>';
      return;
    }

    const grouped = this.groupByPriority(notifications);
    const html = this.renderNotifications(grouped);
    this.container.innerHTML = html;
    this.attachEventListeners();
  }

  groupByPriority(notifications) {
    return notifications.reduce((acc, n) => {
      const priority = n.priority || 'medium';
      if (!acc[priority]) acc[priority] = [];
      acc[priority].push(n);
      return acc;
    }, {});
  }

  renderNotifications(grouped) {
    const priorities = ['high', 'medium', 'low'];
    return priorities.map(priority => {
      const notifs = grouped[priority] || [];
      if (notifs.length === 0) return '';
      return `
        <div style="margin-bottom: 16px;">
          <div class="minor" style="font-weight: 600; margin-bottom: 8px; text-transform: uppercase; color: var(--muted);">${priority} Priority</div>
          ${notifs.map(n => this.createNotification(n)).join('')}
        </div>
      `;
    }).join('');
  }

  createNotification(n) {
    const icon = this.notificationTypeIcons[n.type] || '🔔';
    const priorityColor = n.priority === 'high' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(255, 255, 255, 0.04)';
    
    return `
      <div class="card animate" data-notif-id="${n.id}" style="background: ${priorityColor}; margin-bottom: 10px; padding: 12px; cursor: pointer;">
        <div style="display: flex; gap: 10px; align-items: flex-start;">
          <span style="font-size: 18px;">${icon}</span>
          <div style="flex: 1;">
            <h4 style="margin: 0 0 4px 0;">${n.title}</h4>
            <p class="minor" style="margin: 0;">${n.message}</p>
            <span class="badge badge-blue" style="margin-top: 6px;">${new Date(n.created_at).toLocaleDateString()}</span>
          </div>
          <button class="btn btn-ghost" data-mark-read="${n.id}" style="padding: 6px 10px; font-size: 12px;">✓ Read</button>
        </div>
      </div>
    `;
  }

  attachEventListeners() {
    this.container.querySelectorAll('[data-mark-read]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const notifId = btn.getAttribute('data-mark-read');
        this.manager.markNotificationRead(notifId);
        btn.closest('[data-notif-id]').style.opacity = '0.5';
      });
    });
  }
}

/**
 * WIDGET 4: INTERVIEW EXPERIENCE REPOSITORY
 * Searchable database of past interview experiences
 */
class InterviewRepositoryWidget {
  constructor(containerId, manager) {
    this.container = document.querySelector(containerId);
    this.manager = manager;
    this.filteredExperiences = [];
  }

  async render(experiences) {
    if (!this.container) return;
    
    this.filteredExperiences = experiences || [];
    const html = this.createUI();
    this.container.innerHTML = html;
    this.attachEventListeners();
  }

  createUI() {
    return `
      <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
        <input type="text" id="interview-search" placeholder="Search company or topic..." style="flex: 1; min-width: 200px; padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.08); background: rgba(255, 255, 255, 0.04); color: #fff;">
        <select id="interview-difficulty" style="padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.08); background: rgba(255, 255, 255, 0.04); color: #fff;">
          <option value="">All Difficulty Levels</option>
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>
        <select id="interview-type" style="padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.08); background: rgba(255, 255, 255, 0.04); color: #fff;">
          <option value="">All Interview Types</option>
          <option value="Online">Online</option>
          <option value="Phone">Phone</option>
          <option value="In-Person">In-Person</option>
        </select>
      </div>
      <div id="interview-list" class="grid grid-2">
        ${this.filteredExperiences.length > 0 ? this.filteredExperiences.map(exp => this.createExperienceCard(exp)).join('') : '<p class="minor">No interview experiences found</p>'}
      </div>
    `;
  }

  createExperienceCard(exp) {
    const difficultyColor = exp.difficulty_level === 'Hard' ? 'badge-red' : exp.difficulty_level === 'Medium' ? 'badge-amber' : 'badge-green';
    const outcomeColor = exp.outcome === 'Passed' ? 'badge-green' : exp.outcome === 'Failed' ? 'badge-red' : 'badge-blue';

    return `
      <div class="card job-card animate" data-exp-id="${exp.id}">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
          <div>
            <h3>${exp.company_name || 'Company'}</h3>
            <div class="job-meta">${exp.interview_type} • Round ${exp.interview_round}</div>
          </div>
          <span class="badge ${difficultyColor}">${exp.difficulty_level}</span>
        </div>
        <p class="minor" style="margin: 10px 0;">${exp.experience_summary || 'No summary available'}</p>
        <div class="inline-actions" style="gap: 6px; margin-bottom: 10px; flex-wrap: wrap;">
          <span class="badge ${outcomeColor}">${exp.outcome || 'Pending'}</span>
          ${exp.rating ? `<span class="chip">⭐ ${exp.rating}/5</span>` : ''}
          <span class="chip">Topics: ${(exp.topics_covered || '').split(',').length}</span>
        </div>
        <button class="btn btn-primary" data-view-exp="${exp.id}" style="width: 100%; padding: 8px;">Read Full Experience</button>
      </div>
    `;
  }

  attachEventListeners() {
    const searchInput = document.querySelector('#interview-search');
    const diffSelect = document.querySelector('#interview-difficulty');
    const typeSelect = document.querySelector('#interview-type');

    const applyFilters = () => {
      const search = searchInput.value.toLowerCase();
      const difficulty = diffSelect.value;
      const type = typeSelect.value;

      const filtered = this.filteredExperiences.filter(exp => {
        const matchSearch = !search || exp.company_name.toLowerCase().includes(search) || (exp.topics_covered || '').toLowerCase().includes(search);
        const matchDifficulty = !difficulty || exp.difficulty_level === difficulty;
        const matchType = !type || exp.interview_type === type;
        return matchSearch && matchDifficulty && matchType;
      });

      const list = document.querySelector('#interview-list');
      list.innerHTML = filtered.length > 0 ? filtered.map(exp => this.createExperienceCard(exp)).join('') : '<p class="minor">No interviews match your filters</p>';
      this.attachCardListeners();
    };

    searchInput?.addEventListener('input', applyFilters);
    diffSelect?.addEventListener('change', applyFilters);
    typeSelect?.addEventListener('change', applyFilters);

    this.attachCardListeners();
  }

  attachCardListeners() {
    document.querySelectorAll('[data-view-exp]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const expId = e.target.getAttribute('data-view-exp');
        alert(`Opening interview experience ${expId}`);
      });
    });
  }
}

/**
 * WIDGET 5: RESUME SCORER (MOCK AI)
 * Analyze resume vs job description
 */
class ResumeScorlerWidget {
  constructor(containerId, manager) {
    this.container = document.querySelector(containerId);
    this.manager = manager;
  }

  render() {
    if (!this.container) return;
    this.container.innerHTML = `
      <div class="card glass" style="padding: 24px;">
        <h3 style="margin-bottom: 16px;">Resume Match Scorer</h3>
        <p class="minor" style="margin-bottom: 16px;">Upload your resume and paste a job description to get an AI-powered match score.</p>
        
        <div class="form-grid">
          <div>
            <label>Job Description</label>
            <textarea id="job-desc" placeholder="Paste job description here..." rows="6" style="width: 100%; padding: 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.08); background: rgba(255, 255, 255, 0.04); color: #fff;"></textarea>
          </div>
        </div>
        
        <div class="inline-actions" style="margin-top: 16px;">
          <button id="analyze-resume" class="btn btn-primary">Analyze Match</button>
        </div>
        
        <div id="score-result" style="margin-top: 20px;"></div>
      </div>
    `;
    this.attachEventListeners();
  }

  attachEventListeners() {
    document.querySelector('#analyze-resume')?.addEventListener('click', () => {
      const jobDesc = document.querySelector('#job-desc').value;
      if (!jobDesc) {
        this.manager.showToast('Please enter a job description', 'error');
        return;
      }
      this.analyzeResume(jobDesc);
    });
  }

  analyzeResume(jobDescription) {
    // Mock AI scoring logic
    const mockScore = Math.floor(Math.random() * 100);
    const mockKeywords = ['JavaScript', 'React', 'Node.js', 'REST API'];
    const studentSkills = JSON.parse(localStorage.getItem('student_skills') || '["JavaScript", "React", "Python"]');
    
    const matched = mockKeywords.filter(k => studentSkills.some(s => s.toLowerCase().includes(k.toLowerCase())));
    const missing = mockKeywords.filter(k => !matched.includes(k));

    const resultHtml = `
      <div class="card" style="background: linear-gradient(135deg, rgba(124, 58, 237, 0.1), rgba(20, 184, 166, 0.1)); border: 1px solid rgba(124, 58, 237, 0.3);">
        <h4>Match Score: ${mockScore}%</h4>
        <div class="progress" style="margin: 12px 0;">
          <span style="width: ${mockScore}%;"></span>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px;">
          <div>
            <h5 style="color: #22c55e; margin-bottom: 8px;">✓ Matched Skills (${matched.length})</h5>
            <div>${matched.map(k => `<span class="chip" style="background: rgba(34, 197, 94, 0.15); border-color: rgba(34, 197, 94, 0.3); color: #bbf7d0; margin-bottom: 4px;">${k}</span>`).join('')}</div>
          </div>
          <div>
            <h5 style="color: #ef4444; margin-bottom: 8px;">✗ Missing Skills (${missing.length})</h5>
            <div>${missing.map(k => `<span class="chip" style="background: rgba(239, 68, 68, 0.15); border-color: rgba(239, 68, 68, 0.3); color: #fecdd3; margin-bottom: 4px;">${k}</span>`).join('')}</div>
          </div>
        </div>
        
        <p class="minor" style="margin-top: 12px;">💡 <strong>Recommendation:</strong> Focus on improving ${missing[0] || 'your technical skills'} to increase your match score.</p>
      </div>
    `;

    document.querySelector('#score-result').innerHTML = resultHtml;
  }
}

/**
 * WIDGET 6: SKILL GAP VISUALIZER
 * Chart comparing student skills vs market demand
 */
class SkillGapVisualizerWidget {
  constructor(containerId, manager) {
    this.container = document.querySelector(containerId);
    this.manager = manager;
  }

  render(skillsData = null) {
    if (!this.container) return;

    // Mock skill data
    const mockData = [
      { skill: 'JavaScript', studentLevel: 85, marketDemand: 95 },
      { skill: 'React', studentLevel: 70, marketDemand: 90 },
      { skill: 'Python', studentLevel: 80, marketDemand: 85 },
      { skill: 'SQL', studentLevel: 60, marketDemand: 75 },
      { skill: 'Node.js', studentLevel: 50, marketDemand: 80 },
      { skill: 'Docker', studentLevel: 20, marketDemand: 70 },
    ];

    const data = skillsData || mockData;

    const chartHtml = `
      <div class="card glass" style="padding: 20px;">
        <h3 style="margin-bottom: 20px;">Skill Gap Analysis</h3>
        <div style="display: grid; gap: 16px;">
          ${data.map(item => this.createSkillBar(item)).join('')}
        </div>
        <p class="minor" style="margin-top: 16px; color: #22c55e;">
          📈 <strong>Priority Skills to Learn:</strong> ${data.filter(d => d.studentLevel < d.marketDemand - 20).map(d => d.skill).join(', ')}
        </p>
      </div>
    `;

    this.container.innerHTML = chartHtml;
  }

  createSkillBar(item) {
    const gapPercentage = item.marketDemand - item.studentLevel;
    const gapColor = gapPercentage > 30 ? '#ef4444' : gapPercentage > 15 ? '#f59e0b' : '#22c55e';

    return `
      <div>
        <div class="section-title">
          <h4>${item.skill}</h4>
          <span class="minor">${item.studentLevel}% (You) vs ${item.marketDemand}% (Market)</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
          <div>
            <span class="minor">Your Proficiency</span>
            <div class="progress" style="margin-top: 4px;">
              <span style="width: ${item.studentLevel}%; background: #7c3aed;"></span>
            </div>
          </div>
          <div>
            <span class="minor">Market Demand</span>
            <div class="progress" style="margin-top: 4px;">
              <span style="width: ${item.marketDemand}%; background: ${gapColor};"></span>
            </div>
          </div>
        </div>
      </div>
    `;
  }
}

// Export for use
window.DashboardManager = DashboardManager;
window.DriveFeedWidget = DriveFeedWidget;
window.KanbanBoardWidget = KanbanBoardWidget;
window.NotificationCenterWidget = NotificationCenterWidget;
window.InterviewRepositoryWidget = InterviewRepositoryWidget;
window.ResumeScorlerWidget = ResumeScorlerWidget;
window.SkillGapVisualizerWidget = SkillGapVisualizerWidget;
