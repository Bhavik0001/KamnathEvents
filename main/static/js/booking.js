/**
 * ==========================================================================
 * REALISTIC EVENT TICKET EXPRESS BOOKING CONTROLLER (ES6 Module)
 * Handles instant ticket pass booking, quantity selection, dynamic pricing,
 * and direct transition to My Bookings / Tickets page.
 * ==========================================================================
 */

(function () {
  'use strict';

  const BookingController = {
    modal: null,
    btnConfirmAction: null,
    btnConfirmTextElem: null,
    eventTitleElem: null,
    eventCategoryElem: null,
    eventMetaElem: null,
    eventPriceElem: null,
    basePriceElem: null,
    pricePerTicketLabelElem: null,
    attendeeNameElem: null,
    attendeeEmailElem: null,
    ticketQtyElem: null,
    btnQtyMinus: null,
    btnQtyPlus: null,

    currentEventId: null,
    currentUnitPrice: 0,
    currentQuantity: 1,
    isSubmitting: false,
    initialized: false,
    _lastPromptTime: 0,

    init() {
      if (this.initialized) return;
      this.initialized = true;

      this.modal = document.getElementById('bookingConfirmModal');
      this.btnConfirmAction = document.getElementById('btnConfirmBookingAction');
      this.btnConfirmTextElem = document.getElementById('btnConfirmBookingText');
      this.eventTitleElem = document.getElementById('confirmEventTitle');
      this.eventCategoryElem = document.getElementById('confirmEventCategory');
      this.eventMetaElem = document.getElementById('confirmEventMeta');
      this.eventPriceElem = document.getElementById('confirmEventPrice');
      this.basePriceElem = document.getElementById('confirmBasePrice');
      this.pricePerTicketLabelElem = document.getElementById('confirmPricePerTicketLabel');
      this.attendeeNameElem = document.getElementById('confirmAttendeeName');
      this.attendeeEmailElem = document.getElementById('confirmAttendeeEmail');

      this.ticketQtyElem = document.getElementById('confirmTicketQty');
      this.btnQtyMinus = document.getElementById('btnQtyMinus');
      this.btnQtyPlus = document.getElementById('btnQtyPlus');

      this.bindTriggers();
      this.bindModalClose();
      this.bindStepper();
      this.bindConfirmAction();
    },

    isUserLoggedIn() {
      return document.body.getAttribute('data-user-logged-in') === 'true';
    },

    bindTriggers() {
      document.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-book-trigger]');
        if (!btn) return;

        e.preventDefault();

        const eventId = btn.getAttribute('data-event-id');
        const title = btn.getAttribute('data-event-title') || 'Event Experience';
        const venue = btn.getAttribute('data-event-venue') || 'Official Venue';
        const price = btn.getAttribute('data-event-price') || '0';
        const date = btn.getAttribute('data-event-date') || 'Upcoming';
        const category = btn.getAttribute('data-event-category') || 'Live Event';

        // Close event detail modal if open
        const detailModal = document.getElementById('eventDetailsModal');
        if (detailModal && detailModal.classList.contains('active')) {
          detailModal.classList.remove('active');
        }

        // Check if user is logged in
        if (!this.isUserLoggedIn()) {
          this.promptLogin(eventId, title);
          return;
        }

        // Open direct pass checkout modal
        this.openConfirmation({
          id: eventId,
          title: title,
          venue: venue,
          price: price,
          date: date,
          category: category
        });
      });
    },

    promptLogin(eventId, eventTitle) {
      const now = Date.now();
      if (now - this._lastPromptTime < 1000) return;
      this._lastPromptTime = now;

      const authModal = document.getElementById('authModal');
      if (authModal) {
        authModal.classList.add('active');

        if (window.App && typeof window.App.showToast === 'function') {
          window.App.showToast(`Please sign in to book passes for ${eventTitle}`, 'info');
        } else if (window.AppToast && typeof window.AppToast.show === 'function') {
          window.AppToast.show(`Please sign in to book passes for ${eventTitle}`, 'info');
        }

        const loginTabBtn = document.querySelector('.auth-tab-btn[data-tab="login"]');
        if (loginTabBtn) loginTabBtn.click();
      } else {
        window.location.href = `/index/?next=/book-event/${eventId}/`;
      }
    },

    openConfirmation(eventData) {
      if (!this.modal) {
        window.location.href = `/book-event/${eventData.id}/`;
        return;
      }

      this.currentEventId = eventData.id;
      this.currentUnitPrice = parseFloat(eventData.price) || 0;
      this.currentQuantity = 1;
      this.isSubmitting = false;

      if (this.eventTitleElem) this.eventTitleElem.textContent = eventData.title;
      if (this.eventCategoryElem) this.eventCategoryElem.textContent = eventData.category;
      if (this.eventMetaElem) {
        this.eventMetaElem.innerHTML = `<i class="fa-regular fa-calendar me-1"></i> ${eventData.date} • <i class="fa-solid fa-location-dot ms-1 me-1"></i> ${eventData.venue}`;
      }

      // Attendee information sync
      const userName = document.body.getAttribute('data-user-name');
      const userEmail = document.body.getAttribute('data-user-email');

      if (this.attendeeNameElem && userName) {
        this.attendeeNameElem.textContent = userName;
      }
      if (this.attendeeEmailElem && userEmail) {
        this.attendeeEmailElem.textContent = userEmail;
      }

      // Reset button state
      if (this.btnConfirmAction) {
        this.btnConfirmAction.classList.remove('disabled');
        this.btnConfirmAction.style.pointerEvents = 'auto';
        this.btnConfirmAction.style.opacity = '1';
      }

      this.updateCalculations();

      this.modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    },

    updateCalculations() {
      const total = this.currentUnitPrice * this.currentQuantity;
      const formattedTotal = `₹${Math.round(total).toLocaleString('en-IN')}`;
      const formattedUnit = `₹${Math.round(this.currentUnitPrice).toLocaleString('en-IN')}`;

      if (this.ticketQtyElem) {
        this.ticketQtyElem.textContent = this.currentQuantity;
      }

      if (this.basePriceElem) {
        this.basePriceElem.textContent = formattedTotal;
      }

      if (this.pricePerTicketLabelElem) {
        const passWord = this.currentQuantity > 1 ? 'Passes' : 'Pass';
        this.pricePerTicketLabelElem.textContent = `${this.currentQuantity} × ${formattedUnit} / ${passWord}`;
      }

      if (this.eventPriceElem) {
        this.eventPriceElem.textContent = formattedTotal;
      }

      if (this.btnConfirmTextElem) {
        this.btnConfirmTextElem.textContent = `Confirm Booking • ${formattedTotal}`;
      }

      if (this.btnConfirmAction) {
        this.btnConfirmAction.href = `/book-event/${this.currentEventId}/?qty=${this.currentQuantity}`;
      }
    },

    bindStepper() {
      if (this.btnQtyMinus) {
        this.btnQtyMinus.addEventListener('click', (e) => {
          e.preventDefault();
          if (this.currentQuantity > 1) {
            this.currentQuantity -= 1;
            this.updateCalculations();
          }
        });
      }

      if (this.btnQtyPlus) {
        this.btnQtyPlus.addEventListener('click', (e) => {
          e.preventDefault();
          if (this.currentQuantity < 10) {
            this.currentQuantity += 1;
            this.updateCalculations();
          }
        });
      }
    },

    bindConfirmAction() {
      if (this.btnConfirmAction) {
        this.btnConfirmAction.addEventListener('click', (e) => {
          if (this.isSubmitting) {
            e.preventDefault();
            return;
          }

          this.isSubmitting = true;
          this.btnConfirmAction.style.pointerEvents = 'none';
          this.btnConfirmAction.style.opacity = '0.85';

          if (this.btnConfirmTextElem) {
            this.btnConfirmTextElem.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin me-2"></i> Securing Your Passes...';
          }
        });
      }
    },

    close() {
      if (this.modal) {
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
      }
    },

    bindModalClose() {
      if (!this.modal) return;

      this.modal.addEventListener('click', (e) => {
        if (e.target === this.modal || e.target.closest('.booking-modal-close-btn') || e.target.id === 'btnCancelBookingModal' || e.target.closest('#btnCancelBookingModal')) {
          this.close();
        }
      });

      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.modal.classList.contains('active')) {
          this.close();
        }
      });
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => BookingController.init());
  } else {
    BookingController.init();
  }

  window.BookingController = BookingController;
})();
