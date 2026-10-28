/**
 * ==========================================================================
 * EVENTHUB / BOOKMYSHOW-GRADE CORE APP & UI MANAGER (ES6 Modular Standard)
 * Features: City Selection, Global Shortcuts, Toast System, Header Scroll
 * ==========================================================================
 */

(function () {
  'use strict';

  // State Management
  const AppState = {
    selectedCity: localStorage.getItem('eventhub_city') || 'All Cities',
    searchQuery: '',
    activeCategory: 'all'
  };

  /**
   * Toast Notification Controller
   */
  const Toast = {
    container: null,

    init() {
      if (!this.container) {
        this.container = document.createElement('div');
        this.container.className = 'toast-stack';
        document.body.appendChild(this.container);
      }
    },

    show(message, type = 'success', duration = 4000) {
      this.init();

      const toast = document.createElement('div');
      toast.className = `toast-item ${type}`;

      let iconClass = 'fa-circle-check';
      if (type === 'error') {
        iconClass = 'fa-circle-exclamation';
      } else if (type === 'info') {
        iconClass = 'fa-circle-info';
      }

      toast.innerHTML = `
        <i class="fa-solid ${iconClass} mt-1"></i>
        <div style="flex: 1; font-size: 0.9rem;">${message}</div>
        <button type="button" class="toast-close-btn" aria-label="Close">
          <i class="fa-solid fa-xmark"></i>
        </button>
      `;

      this.container.appendChild(toast);

      // Trigger animation
      requestAnimationFrame(() => toast.classList.add('show'));

      const closeToast = () => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 350);
      };

      toast.querySelector('.toast-close-btn').addEventListener('click', closeToast);
      setTimeout(closeToast, duration);
    }
  };

  // Expose Toast globally
  window.AppToast = Toast;
  window.Toast = Toast;

  /**
   * City Selection Module
   */
  const CityManager = {
    init() {
      const cityBtn = document.getElementById('cityPickerBtn');
      const cityModal = document.getElementById('cityModal');
      const cityNameLabel = document.getElementById('currentCityLabel');
      const cityItems = document.querySelectorAll('.city-card-item');

      if (!cityBtn || !cityModal) return;

      // If on events catalog page without explicit city query, default to All Cities so all events show
      if (window.location.pathname.includes('/events') && !new URLSearchParams(window.location.search).get('city')) {
        AppState.selectedCity = 'All Cities';
        try {
          localStorage.setItem('eventhub_city', 'All Cities');
        } catch (e) {}
      }

      // Update UI with stored city
      if (cityNameLabel && AppState.selectedCity) {
        cityNameLabel.textContent = AppState.selectedCity;
      }

      cityBtn.addEventListener('click', () => {
        cityModal.classList.add('active');
      });

      // City items click handler
      cityItems.forEach(item => {
        const city = item.getAttribute('data-city');
        if (city === AppState.selectedCity) {
          item.classList.add('selected');
        }

        item.addEventListener('click', () => {
          cityItems.forEach(i => i.classList.remove('selected'));
          item.classList.add('selected');

          AppState.selectedCity = city;
          localStorage.setItem('eventhub_city', city);

          if (cityNameLabel) cityNameLabel.textContent = city;
          cityModal.classList.remove('active');

          Toast.show(`Location set to ${city}`, 'success', 2500);

          // Dispatch custom event for event filters
          window.dispatchEvent(new CustomEvent('cityChanged', { detail: { city } }));
        });
      });

      // Close modal on backdrop or close button
      cityModal.addEventListener('click', (e) => {
        if (e.target === cityModal || e.target.closest('.modal-close-icon')) {
          cityModal.classList.remove('active');
        }
      });
    }
  };

  /**
   * Global Keyboard Shortcuts (Ctrl+K or '/' for search)
   */
  const KeyboardShortcuts = {
    init() {
      const searchInputs = document.querySelectorAll('.search-input');
      if (!searchInputs.length) return;

      document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey && e.key === 'k') || (e.key === '/' && document.activeElement.tagName !== 'INPUT')) {
          e.preventDefault();
          searchInputs[0].focus();
          searchInputs[0].select();
        }
      });
    }
  };

  /**
   * Header Scroll Effects
   */
  const HeaderScroll = {
    init() {
      const header = document.querySelector('.site-header');
      if (!header) return;

      window.addEventListener('scroll', () => {
        if (window.scrollY > 30) {
          header.classList.add('scrolled');
        } else {
          header.classList.remove('scrolled');
        }
      }, { passive: true });
    }
  };

  /**
   * Mobile Navigation Toggle
   */
  const MobileNav = {
    init() {
      const toggleBtn = document.getElementById('mobileNavToggle');
      const navMenu = document.getElementById('primaryNavMenu');

      if (!toggleBtn || !navMenu) return;

      toggleBtn.addEventListener('click', () => {
        navMenu.classList.toggle('show');
      });
    }
  };

  /**
   * Newsletter Subscription Controller (AJAX, No Page Refresh, Popup Notification)
   */
  const NewsletterManager = {
    init() {
      const form = document.getElementById('newsletterForm');
      if (!form) return;

      const emailInput = document.getElementById('newsletterEmailInput') || form.querySelector('input[type="email"]');
      const submitBtn = document.getElementById('newsletterSubmitBtn') || form.querySelector('button[type="submit"]');
      const msgBox = document.getElementById('newsletterMsgBox');

      form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = emailInput ? emailInput.value.trim() : '';
        if (!email) {
          Toast.show('Please enter your email address.', 'error', 3000);
          if (emailInput) emailInput.focus();
          return;
        }

        // Basic format check
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          Toast.show('Please enter a valid email address.', 'error', 3000);
          if (emailInput) emailInput.focus();
          return;
        }

        // Disable button & show spinner
        const originalBtnHtml = submitBtn ? submitBtn.innerHTML : 'Subscribe';
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i> Subscribing...';
        }

        if (msgBox) {
          msgBox.style.display = 'none';
        }

        try {
          const csrfTokenInput = form.querySelector('[name=csrfmiddlewaretoken]');
          const csrfToken = csrfTokenInput ? csrfTokenInput.value : '';

          const formData = new FormData(form);

          const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'Accept': 'application/json',
              'X-CSRFToken': csrfToken
            }
          });

          const data = await response.json();

          if (response.ok && data.status === 'success') {
            // Show popup notification
            Toast.show(data.message || 'You have subscribed successfully!', 'success', 4500);

            // Inline feedback
            if (msgBox) {
              msgBox.style.display = 'block';
              msgBox.style.background = '#ecfdf5';
              msgBox.style.color = '#065f46';
              msgBox.style.border = '1px solid #a7f3d0';
              msgBox.innerHTML = '<i class="fa-solid fa-circle-check me-1"></i> ' + (data.message || 'You have subscribed successfully!');
            }

            // Clear input
            if (emailInput) {
              emailInput.value = '';
            }
          } else if (data.status === 'info') {
            Toast.show(data.message || 'You are already subscribed to our newsletter.', 'info', 4000);

            if (msgBox) {
              msgBox.style.display = 'block';
              msgBox.style.background = '#eff6ff';
              msgBox.style.color = '#1e40af';
              msgBox.style.border = '1px solid #bfdbfe';
              msgBox.innerHTML = '<i class="fa-solid fa-circle-info me-1"></i> ' + (data.message || 'You are already subscribed.');
            }
          } else {
            Toast.show(data.message || 'Unable to subscribe. Please try again.', 'error', 4000);

            if (msgBox) {
              msgBox.style.display = 'block';
              msgBox.style.background = '#fef2f2';
              msgBox.style.color = '#991b1b';
              msgBox.style.border = '1px solid #fecaca';
              msgBox.innerHTML = '<i class="fa-solid fa-circle-exclamation me-1"></i> ' + (data.message || 'Subscription failed.');
            }
          }
        } catch (err) {
          console.error('Newsletter submission error:', err);
          Toast.show('An unexpected error occurred. Please try again.', 'error', 4000);
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnHtml;
          }
        }
      });
    }
  };

  /**
   * Theme Manager (Effortless Dynamic Dark/Light Theme Switching)
   */
  const ThemeManager = {
    _transitionTimer: null,

    init() {
      const toggleBtns = document.querySelectorAll('.theme-toggle-btn');

      // Determine active theme (from attribute, localStorage, or system preference)
      const currentTheme = document.documentElement.getAttribute('data-theme') ||
        localStorage.getItem('ke_theme') ||
        'dark';

      this.applyTheme(currentTheme, false);

      toggleBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const activeTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
          const nextTheme = activeTheme === 'dark' ? 'light' : 'dark';
          this.applyTheme(nextTheme, true);
        });
      });

      // Listen for system theme changes when user has not set an explicit preference
      if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
          if (!localStorage.getItem('ke_theme')) {
            this.applyTheme(e.matches ? 'dark' : 'light', true);
          }
        });
      }
    },

    applyTheme(theme, animate = false) {
      if (animate) {
        document.documentElement.classList.add('theme-transitioning');
        clearTimeout(this._transitionTimer);
        this._transitionTimer = setTimeout(() => {
          document.documentElement.classList.remove('theme-transitioning');
        }, 320);
      }

      document.documentElement.setAttribute('data-theme', theme);
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }

      try {
        localStorage.setItem('ke_theme', theme);
      } catch (err) {}

      // Update ARIA labels and titles on all theme buttons
      document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
        const label = theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme';
        btn.setAttribute('aria-label', label);
        btn.setAttribute('title', label);
      });

      // Dispatch event for any other interactive widgets or custom SVGs/Lucide
      window.dispatchEvent(new CustomEvent('themechanged', { detail: { theme } }));
    }
  };

  // Expose ThemeManager globally
  window.AppTheme = ThemeManager;

  /**
   * Event Detail Deep Dive Modal Controller
   * Interactive modal with cover image, live metadata, perks, wishlist sync, and direct booking trigger.
   */
  const EventDetailModal = {
    modal: null,
    closeBtn: null,
    currentEventData: null,

    init() {
      this.modal = document.getElementById('eventDetailsModal');
      if (!this.modal) return;

      this.closeBtn = document.getElementById('closeEventDetailModalBtn') || this.modal.querySelector('.modal-close-icon');

      this.bindCardClicks();
      this.bindModalEvents();
    },

    bindCardClicks() {
      document.addEventListener('click', (e) => {
        // Exclude specific card action buttons (wishlist heart and Book Now button)
        if (e.target.closest('.card-like-btn') || e.target.closest('[data-book-trigger]')) {
          return;
        }

        const card = e.target.closest('.event-card, .spotlight-card');
        if (!card) {
          // Clicking outside any card clears active hover highlight
          document.querySelectorAll('.event-card.card-active, .spotlight-card.card-active, .event-card.selected, .spotlight-card.selected').forEach(c => {
            c.classList.remove('card-active', 'selected', 'is-selected');
          });
          return;
        }

        // Ensure we didn't click inside a modal itself
        if (card.closest('#eventDetailsModal') || card.closest('#bookingConfirmModal') || card.closest('.modal-backdrop-custom')) return;

        // Check if card was already active/selected
        const wasActive = card.classList.contains('card-active') || card.classList.contains('selected');

        // Remove active/hover state from all other cards
        document.querySelectorAll('.event-card, .spotlight-card').forEach(c => {
          if (c !== card) {
            c.classList.remove('card-active', 'selected', 'is-selected');
          }
        });

        // Activate hover effect on clicked card
        card.classList.add('card-active', 'selected', 'is-selected');

        // Open smooth outward expanding image lightbox
        if (window.openImageExpander) {
          window.openImageExpander(card);
        } else if (wasActive || e.detail >= 2) {
          e.preventDefault();
          this.open(card);
        }
      });
    },

    extractCardData(card) {
      // 1. Direct dataset attributes or child fallbacks
      const bookBtn = card.querySelector('[data-book-trigger]');
      const likeBtn = card.querySelector('.card-like-btn');

      const id = card.getAttribute('data-event-id') ||
                 (bookBtn && bookBtn.getAttribute('data-event-id')) ||
                 (likeBtn && likeBtn.getAttribute('data-event-id')) || '1';

      const title = card.getAttribute('data-title') ||
                    (card.querySelector('.event-title') && card.querySelector('.event-title').textContent.trim()) ||
                    (card.querySelector('h3, h2') && card.querySelector('h3, h2').textContent.trim()) || 'Live Event';

      const venue = card.getAttribute('data-venue') ||
                    (card.querySelector('.event-venue-name') && card.querySelector('.event-venue-name').textContent.trim()) ||
                    (card.querySelector('.event-venue-item') && card.querySelector('.event-venue-item').textContent.trim()) || 'Venue Location';

      const category = card.getAttribute('data-category-name') ||
                       (card.querySelector('.badge-category-card') && card.querySelector('.badge-category-card').textContent.trim()) ||
                       card.getAttribute('data-category') || 'Live Event';

      const rawPrice = card.getAttribute('data-price') ||
                       (card.querySelector('.price-amount') && card.querySelector('.price-amount').textContent.replace(/[^0-9.]/g, '')) ||
                       (bookBtn && bookBtn.getAttribute('data-event-price')) || '0';
      const price = parseFloat(rawPrice) || 0;

      const fullDate = card.getAttribute('data-date-formatted') ||
                       (card.querySelector('.event-meta-date-row span') && card.querySelector('.event-meta-date-row span').textContent.trim()) ||
                       (card.querySelector('.event-meta-strip') && card.querySelector('.event-meta-strip').textContent.trim().split('•')[0].trim()) ||
                       card.getAttribute('data-date') || 'Upcoming';

      const dateBadge = card.getAttribute('data-date-badge') ||
                        (card.querySelector('.badge-date-card') && card.querySelector('.badge-date-card').textContent.trim()) || fullDate;

      const imgElem = card.querySelector('.event-card-img, img');
      const image = card.getAttribute('data-image') || (imgElem ? imgElem.src : '');

      const descElem = card.querySelector('.event-description-text');
      const description = card.getAttribute('data-description') ||
                          (descElem ? descElem.textContent.trim() : '') ||
                          'Experience an exhilarating live show featuring talented performers, state-of-the-art acoustics, and seamless digital access.';

      const bookedElem = card.querySelector('.booked-count-badge');
      const booked = card.getAttribute('data-booked') ||
                     (bookedElem ? bookedElem.textContent.replace(/[^0-9]/g, '') : '') || '18';

      return {
        id,
        title,
        venue,
        category,
        price,
        fullDate,
        dateBadge,
        image,
        description,
        booked
      };
    },

    open(card) {
      const data = this.extractCardData(card);
      this.currentEventData = data;

      // Populate Modal Elements
      const imgElem = document.getElementById('eventDetailImg');
      if (imgElem) {
        imgElem.src = data.image || '/static/images/music.jpg';
        imgElem.alt = data.title;
      }

      const catBadge = document.getElementById('eventDetailCategory');
      if (catBadge) catBadge.textContent = data.category;

      const dateBadge = document.getElementById('eventDetailDateBadge');
      if (dateBadge) {
        const cleanBadgeDate = data.dateBadge.replace(/.*calendar\s*/i, '').trim();
        dateBadge.innerHTML = `<i class="fa-regular fa-calendar"></i> ${cleanBadgeDate}`;
      }

      const bookedBadge = document.getElementById('eventDetailBookedBadge');
      if (bookedBadge) {
        bookedBadge.innerHTML = `<i class="fa-solid fa-users"></i> ${data.booked} booked`;
      }

      const titleElem = document.getElementById('eventDetailTitle');
      if (titleElem) titleElem.textContent = data.title;

      const fullDateElem = document.getElementById('eventDetailFullDate');
      if (fullDateElem) fullDateElem.textContent = data.fullDate;

      const venueElem = document.getElementById('eventDetailVenue');
      if (venueElem) venueElem.textContent = data.venue;

      const catNameElem = document.getElementById('eventDetailCategoryName');
      if (catNameElem) catNameElem.textContent = data.category;

      const descElem = document.getElementById('eventDetailDescription');
      if (descElem) descElem.textContent = data.description;

      const priceElem = document.getElementById('eventDetailPriceDisplay');
      if (priceElem) {
        priceElem.textContent = `₹${data.price.toLocaleString('en-IN')}`;
      }

      // Populate Book Now Trigger Button
      const bookBtn = document.getElementById('eventDetailBookBtn');
      if (bookBtn) {
        bookBtn.setAttribute('data-event-id', data.id);
        bookBtn.setAttribute('data-event-title', data.title);
        bookBtn.setAttribute('data-event-venue', data.venue);
        bookBtn.setAttribute('data-event-price', data.price);
        bookBtn.setAttribute('data-event-date', data.fullDate);
        bookBtn.setAttribute('data-event-category', data.category);
      }

      // Sync Wishlist Button state
      this.syncWishlistBtnState();

      // Show Modal
      this.modal.classList.add('active');
      this.modal.style.display = 'flex';
      this.modal.style.opacity = '1';
      this.modal.style.pointerEvents = 'auto';
      document.body.style.overflow = 'hidden';
    },

    syncWishlistBtnState() {
      const wishlistBtn = document.getElementById('eventDetailWishlistBtn');
      if (!wishlistBtn || !this.currentEventData) return;

      const isSaved = window.WishlistController && typeof window.WishlistController.hasItem === 'function'
        ? window.WishlistController.hasItem(this.currentEventData.id)
        : false;

      if (isSaved) {
        wishlistBtn.innerHTML = '<i class="fa-solid fa-heart text-danger me-1"></i> <span>Saved in Wishlist</span>';
        wishlistBtn.classList.add('active');
      } else {
        wishlistBtn.innerHTML = '<i class="fa-regular fa-heart me-1"></i> <span>Wishlist</span>';
        wishlistBtn.classList.remove('active');
      }
    },

    close() {
      if (!this.modal) return;
      this.modal.classList.remove('active');
      this.modal.style.display = '';
      this.modal.style.opacity = '';
      this.modal.style.pointerEvents = '';
      document.body.style.overflow = '';
      this.currentEventData = null;
    },

    bindModalEvents() {
      // Close button
      if (this.closeBtn) {
        this.closeBtn.addEventListener('click', () => this.close());
      }

      // Backdrop click
      this.modal.addEventListener('click', (e) => {
        if (e.target === this.modal || e.target.closest('.event-detail-close-btn') || e.target.closest('.modal-close-icon')) {
          this.close();
        }
      });

      // Escape key to close
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.modal.classList.contains('active')) {
          this.close();
        }
      });

      // Wishlist toggle inside modal
      const wishlistBtn = document.getElementById('eventDetailWishlistBtn');
      if (wishlistBtn) {
        wishlistBtn.addEventListener('click', (e) => {
          e.preventDefault();
          if (!this.currentEventData) return;

          if (window.WishlistController && typeof window.WishlistController.toggleItem === 'function') {
            const item = {
              id: this.currentEventData.id,
              title: this.currentEventData.title,
              venue: this.currentEventData.venue,
              price: this.currentEventData.price,
              date: this.currentEventData.fullDate,
              category: this.currentEventData.category,
              thumbnail: this.currentEventData.image
            };

            const isAdded = window.WishlistController.toggleItem(item);
            this.syncWishlistBtnState();

            if (window.AppToast) {
              window.AppToast.show(
                isAdded ? `Added "${item.title}" to Wishlist` : `Removed "${item.title}" from Wishlist`,
                isAdded ? 'success' : 'info',
                2500
              );
            }
          }
        });
      }

      // Close detail modal when booking trigger is fired so booking confirmation opens cleanly
      const bookBtn = document.getElementById('eventDetailBookBtn');
      if (bookBtn) {
        bookBtn.addEventListener('click', () => {
          // BookingController opens #bookingConfirmModal and controls body overflow
          this.modal.classList.remove('active');
        });
      }
    }
  };

  // Expose EventDetailModal globally
  window.EventDetailModal = EventDetailModal;

  // Initialize all core subsystems when DOM is ready
  document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    CityManager.init();
    KeyboardShortcuts.init();
    HeaderScroll.init();
    MobileNav.init();
    NewsletterManager.init();
    EventDetailModal.init();

    // Check for pending toast notification across page navigation/redirects
    try {
      const pendingToast = sessionStorage.getItem('pending_toast');
      if (pendingToast) {
        sessionStorage.removeItem('pending_toast');
        const parsed = JSON.parse(pendingToast);
        if (parsed && parsed.message) {
          setTimeout(() => Toast.show(parsed.message, parsed.type || 'success', 4500), 200);
        }
      }
    } catch (e) {}
  });

})();
