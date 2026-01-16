const API_BASE = 'http://localhost:5000/api';

const toastStackId = 'toast-stack';

export function loadAuth() {
  try {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    const profile = JSON.parse(localStorage.getItem('profile') || 'null');
    if (!token || !user) return null;
    return { token, user, profile };
  } catch (err) {
    console.error('Auth load failed', err);
    return null;
  }
}

export function saveAuth({ token, user, profile }) {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
  if (profile) {
    localStorage.setItem('profile', JSON.stringify(profile));
  }
}

export function clearAuth() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  localStorage.removeItem('profile');
}

export function redirectToRole(roleId) {
  if (roleId === 1) window.location.href = 'student.html';
  else if (roleId === 2) window.location.href = 'company.html';
  else if (roleId === 3) window.location.href = 'admin.html';
  else window.location.href = 'index.html';
}

export function requireRole(allowedRoles = []) {
  const auth = loadAuth();
  if (!auth) {
    window.location.href = 'index.html';
    return null;
  }
  if (allowedRoles.length && !allowedRoles.includes(auth.user.role_id)) {
    redirectToRole(auth.user.role_id);
    return null;
  }
  return auth;
}

export async function api(path, { method = 'GET', body, headers = {}, token } = {}) {
  const auth = loadAuth();
  const finalHeaders = {
    'Content-Type': 'application/json',
    ...headers,
  };
  const authToken = token || auth?.token;
  if (authToken) finalHeaders.Authorization = `Bearer ${authToken}`;

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: finalHeaders,
    body: body ? JSON.stringify(body) : undefined,
  }).catch(networkError => {
    throw new Error('Cannot connect to server. Please ensure the backend is running on http://localhost:5000');
  });

  let data = {};
  try {
    data = await response.json();
  } catch (err) {
    // ignore
  }

  if (!response.ok) {
    const message = data?.error || 'Request failed';
    throw new Error(message);
  }

  return data;
}

export function showToast(message, type = 'info') {
  let stack = document.getElementById(toastStackId);
  if (!stack) {
    stack = document.createElement('div');
    stack.id = toastStackId;
    stack.className = 'toast-stack';
    document.body.appendChild(stack);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  stack.appendChild(toast);
  setTimeout(() => toast.remove(), 4200);
}

export function formatDate(value) {
  if (!value) return '—';
  const d = new Date(value);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

export function hydrateUserBadge(auth) {
  if (!auth) return;
  const name = auth.user.role_id === 1
    ? auth.profile?.full_name || auth.user.email
    : auth.user.role_id === 2
      ? auth.profile?.company_name || auth.user.email
      : auth.user.email;
  const email = auth.user.email;

  const nameEl = document.querySelector('[data-user-name]');
  const emailEl = document.querySelector('[data-user-email]');
  const avatarEl = document.querySelector('[data-user-avatar]');
  const roleEl = document.querySelector('[data-user-role]');

  if (nameEl) nameEl.textContent = name;
  if (emailEl) emailEl.textContent = email;
  if (avatarEl) avatarEl.textContent = name.charAt(0).toUpperCase();
  if (roleEl) roleEl.textContent = roleLabel(auth.user.role_id);
}

export function attachLogout() {
  const btn = document.querySelector('[data-logout]');
  if (!btn) return;
  btn.addEventListener('click', () => {
    clearAuth();
    window.location.href = 'index.html';
  });
}

export function roleLabel(roleId) {
  if (roleId === 1) return 'Student';
  if (roleId === 2) return 'Company';
  if (roleId === 3) return 'Admin';
  return 'User';
}

export function animateStagger(selector) {
  const items = document.querySelectorAll(selector);
  items.forEach((el, idx) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(12px)';
    setTimeout(() => {
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
      el.style.transition = 'all 320ms ease';
    }, idx * 90 + 80);
  });
}

export function setGreeting(selector = '[data-greeting]') {
  const el = document.querySelector(selector);
  if (el) {
    const hour = new Date().getHours();
    const text = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
    el.textContent = text;
  }
}

export function guardNavLinks(roleId) {
  const links = document.querySelectorAll('[data-role-link]');
  links.forEach(link => {
    const allowed = (link.getAttribute('data-role-link') || '').split(',').map(v => parseInt(v, 10));
    if (allowed.length && !allowed.includes(roleId)) {
      link.style.display = 'none';
    }
  });
}
