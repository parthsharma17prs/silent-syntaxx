import { api, showToast } from './app.js';

const form = document.querySelector('#register-form');
const roleRadios = document.querySelectorAll('input[name="role"]');
const studentFields = document.querySelector('[data-student-fields]');
const companyFields = document.querySelector('[data-company-fields]');
const submitBtn = document.querySelector('#register-submit');

function currentRole() {
  const checked = Array.from(roleRadios).find(r => r.checked);
  return checked ? parseInt(checked.value, 10) : 1;
}

function toggleFields() {
  const role = currentRole();
  if (role === 1) {
    studentFields?.classList.remove('hidden');
    companyFields?.classList.add('hidden');
  } else {
    studentFields?.classList.add('hidden');
    companyFields?.classList.remove('hidden');
  }
}

roleRadios.forEach(r => r.addEventListener('change', toggleFields));
toggleFields();

form?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(form);
  const payload = {
    email: formData.get('email'),
    password: formData.get('password'),
    role_id: currentRole(),
  };

  if (formData.get('password') !== formData.get('confirm_password')) {
    showToast('Passwords do not match', 'error');
    return;
  }

  if (payload.role_id === 1) {
    payload.full_name = formData.get('full_name');
    payload.enrollment_number = formData.get('enrollment_number');
    payload.branch = formData.get('branch');
    payload.cgpa = parseFloat(formData.get('cgpa'));
    payload.graduation_year = parseInt(formData.get('graduation_year'), 10);
    payload.phone = formData.get('phone');
  } else {
    payload.company_name = formData.get('company_name');
    payload.industry = formData.get('industry');
    payload.hr_name = formData.get('hr_name');
    payload.hr_phone = formData.get('hr_phone');
  }

  submitBtn.disabled = true;
  submitBtn.textContent = 'Creating account...';
  try {
    await api('/auth/register', { method: 'POST', body: payload });
    showToast('Account created. Await verification.', 'success');
    window.location.href = 'index.html';
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Register';
  }
});
