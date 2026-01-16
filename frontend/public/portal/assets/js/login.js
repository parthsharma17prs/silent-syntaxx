import { api, saveAuth, redirectToRole, showToast } from './app.js';

const form = document.querySelector('#login-form');
const emailInput = document.querySelector('#email');
const passwordInput = document.querySelector('#password');
const submitBtn = document.querySelector('#login-submit');

const existingToken = localStorage.getItem('token');
if (existingToken) {
  try {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (user?.role_id) redirectToRole(user.role_id);
  } catch (_) {
    // ignore parse error
  }
}

form?.addEventListener('submit', async (e) => {
  e.preventDefault();
  submitBtn.disabled = true;
  submitBtn.textContent = 'Signing in...';
  try {
    const { access_token, user, profile } = await api('/auth/login', {
      method: 'POST',
      body: {
        email: emailInput.value.trim(),
        password: passwordInput.value,
      },
    });
    saveAuth({ token: access_token, user, profile });
    showToast('Welcome back!', 'success');
    redirectToRole(user.role_id);
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Sign In';
  }
});
