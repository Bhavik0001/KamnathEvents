/**
 * ==========================================================================
 * ADMIN & ORGANIZER DASHBOARD CONTROLLER (ES6 Modular Standard)
 * Features: Tab/Section Switcher, Table Filtering, Modals, Status Filter
 * ==========================================================================
 */

(function () {
  'use strict';

  const AdminDashboard = {
    init() {
      this.bindSidebarToggle();
      this.bindSectionNavigation();
      this.bindTableSearches();
      this.bindBookingFilters();
      this.bindDatePickers();
      this.checkEditModal();
      this.restoreActiveSection();
    },

    bindSidebarToggle() {
      const toggleBtn = document.getElementById('sidebarToggle');
      const sidebar = document.getElementById('sidebar');

      if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
          sidebar.classList.toggle('active');
        });
      }
    },

    bindSectionNavigation() {
      // Sidebar links
      document.querySelectorAll('[data-section]').forEach(link => {
        link.addEventListener('click', (e) => {
          e.preventDefault();
          const sectionId = link.getAttribute('data-section');
          this.showSection(sectionId);
        });
      });

      // Inline section buttons
      document.querySelectorAll('[data-section-button]').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const sectionId = btn.getAttribute('data-section-button');
          this.showSection(sectionId);
        });
      });
    },

    showSection(sectionId) {
      const sections = document.querySelectorAll('.page-section');
      const navLinks = document.querySelectorAll('.sidebar nav a');
      const topTitle = document.getElementById('topTitle');

      sections.forEach(sec => sec.classList.remove('active'));
      navLinks.forEach(link => link.classList.remove('active'));

      const targetSection = document.getElementById(sectionId);
      if (targetSection) {
        targetSection.classList.add('active');
      }

      const activeLink = document.querySelector(`.sidebar nav a[data-section="${sectionId}"]`);
      if (activeLink) {
        activeLink.classList.add('active');
      }

      // Update page title
      const titles = {
        dashboard: 'Dashboard Overview',
        events: 'Event Management',
        categories: 'Categories',
        bookings: 'Booking Records',
        users: 'Customer Accounts',
        contacts: 'Support & Inquiries',
        reports: 'Analytics & Reports'
      };

      if (topTitle && titles[sectionId]) {
        topTitle.textContent = titles[sectionId];
      }

      // Update URL query parameter without full reload
      const newUrl = new URL(window.location);
      newUrl.searchParams.set('section', sectionId);
      window.history.pushState({}, '', newUrl);
    },

    restoreActiveSection() {
      const params = new URLSearchParams(window.location.search);
      const section = params.get('section') || 'dashboard';
      this.showSection(section);
    },

    bindTableSearches() {
      // Event search
      const eventSearch = document.getElementById('eventSearch');
      if (eventSearch) {
        eventSearch.addEventListener('input', (e) => {
          const query = e.target.value.toLowerCase().trim();
          const rows = document.querySelectorAll('#events .table tbody tr');

          rows.forEach(row => {
            const titleCol = row.querySelector('td:first-child')?.textContent.toLowerCase() || '';
            row.style.display = titleCol.includes(query) ? '' : 'none';
          });
        });
      }

      // Customer search
      const customerSearch = document.getElementById('customerSearch');
      const customerTbody = document.getElementById('customerTableBody');

      if (customerSearch && customerTbody) {
        customerSearch.addEventListener('input', (e) => {
          const query = customerSearch.value.toLowerCase().trim();
          const rows = customerTbody.querySelectorAll('tr');

          rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
          });
        });
      }
    },

    bindBookingFilters() {
      const statusFilter = document.getElementById('bookingStatusFilter');
      if (!statusFilter) return;

      const bookingRows = document.querySelectorAll('.booking-row');

      statusFilter.addEventListener('change', () => {
        const selected = statusFilter.value;

        bookingRows.forEach(row => {
          const rowStatus = row.dataset.status;
          if (selected === 'All Status' || rowStatus === selected) {
            row.style.display = '';
          } else {
            row.style.display = 'none';
          }
        });
      });
    },

    checkEditModal() {
      const editModalElem = document.getElementById('editEventModal');
      if (editModalElem && typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(editModalElem);
        modal.show();
      }
    },

    bindDatePickers() {
      // Enhance all date inputs to trigger calendar picker when clicked
      document.querySelectorAll('input[type="date"]').forEach(input => {
        input.addEventListener('click', () => {
          try {
            if (typeof input.showPicker === 'function') {
              input.showPicker();
            }
          } catch (e) {}
        });
      });
    }
  };

  // Helper functions exposed for templates
  window.confirmDelete = function (type) {
    return confirm(`Are you sure you want to delete this ${type}? This action cannot be undone.`);
  };

  window.showSection = function (sectionId) {
    AdminDashboard.showSection(sectionId);
  };

  window.viewBookingDetails = function (btn) {
    if (!btn) return;
    const target = btn.getAttribute('data-bs-target');
    if (target) {
      const modalEl = document.querySelector(target);
      if (modalEl && typeof bootstrap !== 'undefined') {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
      }
    }
  };

  document.addEventListener('DOMContentLoaded', () => {
    AdminDashboard.init();
  });

  window.AdminDashboard = AdminDashboard;
})();
