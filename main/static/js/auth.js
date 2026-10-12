/**
 * ==========================================================================
 * AUTHENTICATION MODAL & FORM CONTROLLER (ES6 Modular Standard)
 * Features: Asynchronous AJAX Login/Sign Up, Password Visibility,
 * Live Validation, Instant Visual Feedback, CSRF Protection
 * ==========================================================================
 */

(function () {
  'use strict';

  const AuthModal = {
    modal: null,
    tabBtns: null,
    loginForm: null,
    signupForm: null,
    alertBox: null,
    alertText: null,
    successBox: null,
    successText: null,

    init() {
      this.bindPasswordToggles();

      this.modal = document.getElementById('authModal');
      if (!this.modal) return;

      this.tabBtns = this.modal.querySelectorAll('.auth-tab-btn');
      this.loginForm = document.getElementById('loginForm');
      this.signupForm = document.getElementById('signupForm');
      this.alertBox = document.getElementById('authModalAlert');
      this.alertText = document.getElementById('authModalAlertText');
      this.successBox = document.getElementById('authModalSuccess');
      this.successText = document.getElementById('authModalSuccessText');

      this.bindTriggers();
      this.bindTabs();
      this.bindAjaxForms();
      this.bindInputClear();
    },

    bindTriggers() {
      // Buttons opening Login or Signup
      document.querySelectorAll('[data-auth-trigger]').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const targetTab = btn.getAttribute('data-auth-trigger') || 'login';
          this.open(targetTab);
        });
      });

      // Close modal on background click or close icon
      this.modal.addEventListener('click', (e) => {
        if (e.target === this.modal || e.target.closest('.modal-close-icon')) {
          this.close();
        }
      });

      // Escape key to close
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.modal.classList.contains('active')) {
          this.close();
        }
      });
    },

    open(activeTab = 'login') {
      this.clearBanners();
      this.switchTab(activeTab);
      this.modal.classList.add('active');
      document.body.style.overflow = 'hidden';

      // Focus first input of active form
      setTimeout(() => {
        const activeForm = activeTab === 'signup' ? this.signupForm : this.loginForm;
        if (activeForm) {
          const firstInput = activeForm.querySelector('input:not([type="hidden"])');
          if (firstInput) firstInput.focus();
        }
      }, 150);
    },

    close() {
      this.modal.classList.remove('active');
      document.body.style.overflow = '';
      this.clearBanners();
    },

    bindTabs() {
      this.tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
          const tab = btn.getAttribute('data-tab');
          this.switchTab(tab);
        });
      });
    },

    switchTab(tab) {
      this.clearBanners();

      this.tabBtns.forEach(btn => {
        if (btn.getAttribute('data-tab') === tab) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });

      if (tab === 'login') {
        if (this.loginForm) this.loginForm.style.display = 'block';
        if (this.signupForm) this.signupForm.style.display = 'none';
      } else {
        if (this.loginForm) this.loginForm.style.display = 'none';
        if (this.signupForm) this.signupForm.style.display = 'block';
      }
    },

    showError(message) {
      if (this.successBox) this.successBox.style.display = 'none';
      if (this.alertBox && this.alertText) {
        this.alertText.textContent = message || 'An unexpected error occurred. Please try again.';
        this.alertBox.style.display = 'flex';
      } else if (window.Toast) {
        window.Toast.show(message, 'error', 4000);
      } else {
        alert(message);
      }
    },

    showSuccess(message) {
      if (this.alertBox) this.alertBox.style.display = 'none';
      if (this.successBox && this.successText) {
        this.successText.textContent = message || 'Success!';
        this.successBox.style.display = 'flex';
      }
    },

    clearBanners() {
      if (this.alertBox) this.alertBox.style.display = 'none';
      if (this.successBox) this.successBox.style.display = 'none';
    },

    bindInputClear() {
      if (this.modal) {
        this.modal.querySelectorAll('input').forEach(input => {
          input.addEventListener('input', () => {
            if (this.alertBox && this.alertBox.style.display !== 'none') {
              this.alertBox.style.display = 'none';
            }
          });
        });
      }
    },

    bindPasswordToggles() {
      document.querySelectorAll('.password-toggle-btn').forEach(btn => {
        if (btn.dataset.toggleBound) return;
        btn.dataset.toggleBound = 'true';

        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const input = btn.previousElementSibling || btn.closest('.auth-input-wrapper')?.querySelector('input');
          if (!input) return;

          const isPassword = input.getAttribute('type') === 'password';
          input.setAttribute('type', isPassword ? 'text' : 'password');

          const icon = btn.querySelector('i');
          if (icon) {
            if (isPassword) {
              icon.classList.remove('fa-eye');
              icon.classList.add('fa-eye-slash');
            } else {
              icon.classList.remove('fa-eye-slash');
              icon.classList.add('fa-eye');
            }
          }
        });
      });
    },

    bindAjaxForms() {
      const getCsrf = (form) => {
        return form.querySelector('[name=csrfmiddlewaretoken]')?.value ||
          document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
      };

      // 1. AJAX LOGIN FORM SUBMISSION
      if (this.loginForm) {
        this.loginForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          this.clearBanners();

          const submitBtn = this.loginForm.querySelector('button[type="submit"]');
          const origBtnHtml = submitBtn ? submitBtn.innerHTML : 'Sign In';

          const emailInput = this.loginForm.querySelector('input[name="email"]');
          const pwdInput = this.loginForm.querySelector('input[name="password"]');

          const email = (emailInput?.value || '').trim();
          const password = (pwdInput?.value || '').trim();

          if (!email || !password) {
            this.showError('Please enter both your email address and password.');
            return;
          }

          if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin me-1"></i> Signing In...';
          }

          try {
            const formData = new FormData(this.loginForm);
            formData.set('ajax', '1');

            const response = await fetch(this.loginForm.action || window.location.href, {
              method: 'POST',
              headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrf(this.loginForm)
              },
              body: formData
            });

            const data = await response.json().catch(() => null);

            if (response.ok && data && data.success) {
              const msg = data.message || 'Signed in successfully!';
              this.showSuccess(msg);
              const toastFn = window.AppToast || window.Toast;
              if (toastFn) {
                toastFn.show(msg, 'success', 3500);
              }
              try {
                sessionStorage.setItem('pending_toast', JSON.stringify({
                  message: msg,
                  type: 'success'
                }));
              } catch (e) {}

              setTimeout(() => {
                this.close();
                window.location.href = data.redirect_url || window.location.href;
              }, 800);
            } else {
              const errorMsg = (data && data.error) ? data.error : 'Invalid email or password. Please check your credentials.';
              this.showError(errorMsg);
              if (pwdInput) {
                pwdInput.value = '';
                pwdInput.focus();
              }
              if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = origBtnHtml;
              }
            }
          } catch (err) {
            console.error('Login network error:', err);
            this.showError('Unable to connect to server. Please check your connection and try again.');
            if (submitBtn) {
              submitBtn.disabled = false;
              submitBtn.innerHTML = origBtnHtml;
            }
          }
        });
      }

      // 2. AJAX SIGNUP FORM SUBMISSION
      if (this.signupForm) {
        this.signupForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          this.clearBanners();

          const submitBtn = this.signupForm.querySelector('button[type="submit"]');
          const origBtnHtml = submitBtn ? submitBtn.innerHTML : 'Create Account';

          const nameInput = this.signupForm.querySelector('input[name="name"]');
          const emailInput = this.signupForm.querySelector('input[name="email"]');
          const pwdInput = this.signupForm.querySelector('input[name="password"]');
          const confirmPwdInput = this.signupForm.querySelector('input[name="confirm_password"]');

          const name = (nameInput?.value || '').trim();
          const email = (emailInput?.value || '').trim();
          const password = (pwdInput?.value || '').trim();
          const confirmPassword = (confirmPwdInput?.value || '').trim();

          if (!name || !email || !password) {
            this.showError('Please fill in all required fields.');
            return;
          }

          if (password.length < 6) {
            this.showError('Password must be at least 6 characters long.');
            if (pwdInput) pwdInput.focus();
            return;
          }

          if (password !== confirmPassword) {
            this.showError('Passwords do not match. Please verify.');
            if (confirmPwdInput) confirmPwdInput.focus();
            return;
          }

          if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin me-1"></i> Creating Account...';
          }

          try {
            const formData = new FormData(this.signupForm);
            formData.set('ajax', '1');

            const response = await fetch(this.signupForm.action || window.location.href, {
              method: 'POST',
              headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrf(this.signupForm)
              },
              body: formData
            });

            const data = await response.json().catch(() => null);

            if (response.ok && data && data.success) {
              const successMsg = data.message || 'You have signed up successfully!';
              this.showSuccess(successMsg);
              const toastFn = window.AppToast || window.Toast;
              if (toastFn) {
                toastFn.show(successMsg, 'success', 4500);
              }
              try {
                sessionStorage.setItem('pending_toast', JSON.stringify({
                  message: successMsg,
                  type: 'success'
                }));
              } catch (e) {}

              setTimeout(() => {
                this.close();
                window.location.href = data.redirect_url || window.location.href;
              }, 1200);
            } else {
              const errorMsg = (data && data.error) ? data.error : 'Failed to create account. Please check your information.';
              this.showError(errorMsg);
              if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = origBtnHtml;
              }
            }
          } catch (err) {
            console.error('Signup network error:', err);
            this.showError('Unable to connect to server. Please check your connection and try again.');
            if (submitBtn) {
              submitBtn.disabled = false;
              submitBtn.innerHTML = origBtnHtml;
            }
          }
        });
      }
    }
  };

  document.addEventListener('DOMContentLoaded', () => {
    AuthModal.init();
  });

  window.AuthModal = AuthModal;
})();
