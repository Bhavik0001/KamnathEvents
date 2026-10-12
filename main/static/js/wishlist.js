/**
 * ==========================================================================
 * PRODUCTION WISHLIST & CART CONTROLLER (ES6 Modular Standard)
 * Features: LocalStorage Persistence, Real-time Navbar Badge, Drawer Offcanvas,
 *           Direct Booking Modal Trigger, Smooth Micro-animations & Toast Sync
 * ==========================================================================
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'eventhub_wishlist_v1';

  const WishlistController = {
    items: [],
    drawer: null,
    backdrop: null,
    badge: null,
    mobileBadge: null,
    listContainer: null,
    emptyState: null,
    totalPriceElem: null,
    itemCountSubtitle: null,

    init() {
      this.loadFromStorage();
      this.cacheDom();
      this.bindEvents();
      this.syncUI();
    },

    loadFromStorage() {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        this.items = stored ? JSON.parse(stored) : [];
        if (!Array.isArray(this.items)) {
          this.items = [];
        }
      } catch (err) {
        console.warn('WishlistController: LocalStorage unavailable, using memory store.', err);
        this.items = [];
      }
    },

    saveToStorage() {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.items));
      } catch (err) {
        console.warn('WishlistController: Could not save to localStorage.', err);
      }
    },

    cacheDom() {
      this.drawer = document.getElementById('wishlistDrawer');
      this.backdrop = document.getElementById('wishlistBackdrop');
      this.badge = document.getElementById('wishlistBadgeCount');
      this.mobileBadge = document.getElementById('mobileWishlistBadgeCount');
      this.listContainer = document.getElementById('wishlistItemsList');
      this.emptyState = document.getElementById('wishlistEmptyState');
      this.totalPriceElem = document.getElementById('wishlistTotalPrice');
      this.itemCountSubtitle = document.getElementById('wishlistDrawerSubtitle');
    },

    bindEvents() {
      // 1. Open drawer triggers
      document.querySelectorAll('#openWishlistDrawerBtn, #openWishlistDrawerBtnMobile, [data-wishlist-trigger="open"]').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          this.openDrawer();
        });
      });

      // 2. Close drawer triggers
      const closeBtn = document.getElementById('closeWishlistDrawerBtn');
      if (closeBtn) {
        closeBtn.addEventListener('click', () => this.closeDrawer());
      }
      if (this.backdrop) {
        this.backdrop.addEventListener('click', () => this.closeDrawer());
      }

      // 3. Escape key closes drawer
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isDrawerOpen()) {
          this.closeDrawer();
        }
      });

      // 4. Clear all button
      const clearBtn = document.getElementById('clearWishlistBtn');
      if (clearBtn) {
        clearBtn.addEventListener('click', () => {
          if (this.items.length === 0) return;
          if (confirm('Are you sure you want to clear your saved events wishlist?')) {
            this.clear();
            if (window.AppToast) {
              window.AppToast.show('Wishlist cleared', 'info', 2000);
            }
          }
        });
      }

      // 5. Global delegated click handler for card like buttons (.card-like-btn)
      document.addEventListener('click', (e) => {
        const likeBtn = e.target.closest('.card-like-btn');
        if (!likeBtn) return;

        e.preventDefault();
        e.stopPropagation();

        const item = this.extractItemData(likeBtn);
        if (!item || !item.id) return;

        const isAdded = this.toggleItem(item);

        // Micro-bounce animation on button
        likeBtn.classList.add('pop');
        setTimeout(() => likeBtn.classList.remove('pop'), 250);

        if (window.AppToast) {
          window.AppToast.show(
            isAdded ? `Added "${item.title}" to Wishlist` : `Removed "${item.title}" from Wishlist`,
            isAdded ? 'success' : 'info',
            2500
          );
        }
      });

      // 6. Delegated clicks inside wishlist drawer (Remove & Book Now)
      if (this.listContainer) {
        this.listContainer.addEventListener('click', (e) => {
          // Remove button
          const removeBtn = e.target.closest('.wishlist-btn-remove');
          if (removeBtn) {
            e.preventDefault();
            const id = removeBtn.getAttribute('data-remove-id');
            if (id) {
              const item = this.items.find(i => String(i.id) === String(id));
              this.removeItem(id);
              if (window.AppToast && item) {
                window.AppToast.show(`Removed "${item.title}" from Wishlist`, 'info', 2000);
              }
            }
            return;
          }

          // Book now button inside drawer
          const bookBtn = e.target.closest('[data-book-trigger]');
          if (bookBtn) {
            // Let booking.js handle the click, and close drawer smoothly
            setTimeout(() => this.closeDrawer(), 300);
          }
        });
      }
    },

    extractItemData(likeBtn) {
      // 1. First priority: attributes on the button itself
      let id = likeBtn.getAttribute('data-event-id');
      let title = likeBtn.getAttribute('data-event-title');
      let venue = likeBtn.getAttribute('data-event-venue');
      let price = likeBtn.getAttribute('data-event-price');
      let date = likeBtn.getAttribute('data-event-date');
      let category = likeBtn.getAttribute('data-event-category');
      let thumbnail = likeBtn.getAttribute('data-event-thumbnail');

      // 2. Second priority: read from parent .event-card or .event-card-wrapper
      const card = likeBtn.closest('.event-card') || likeBtn.closest('.event-card-wrapper');
      if (card) {
        if (!id) id = card.getAttribute('data-id') || card.getAttribute('data-event-id');
        if (!title) title = card.getAttribute('data-title') || card.querySelector('.event-title')?.textContent?.trim();
        if (!venue) venue = card.getAttribute('data-venue') || card.querySelector('.event-venue-name')?.textContent?.trim();
        if (!price) price = card.getAttribute('data-price') || card.querySelector('.price-amount')?.textContent?.replace(/[^0-9]/g, '');
        if (!date) date = card.getAttribute('data-date') || card.querySelector('.event-meta-date-row span')?.textContent?.trim();
        if (!category) category = card.getAttribute('data-category') || card.querySelector('.badge-category-card')?.textContent?.trim();
        if (!thumbnail) {
          const img = card.querySelector('img.event-card-img') || card.querySelector('img');
          if (img) thumbnail = img.getAttribute('src');
        }

        // Also check if book button inside this card has event id
        if (!id) {
          const bookBtn = card.querySelector('[data-book-trigger]');
          if (bookBtn) {
            id = bookBtn.getAttribute('data-event-id');
            if (!price) price = bookBtn.getAttribute('data-event-price');
            if (!date) date = bookBtn.getAttribute('data-event-date');
            if (!venue) venue = bookBtn.getAttribute('data-event-venue');
            if (!title) title = bookBtn.getAttribute('data-event-title');
          }
        }
      }

      // Fallback synthetic ID if missing
      if (!id && title) {
        id = 'event-' + title.toLowerCase().replace(/[^a-z0-9]/g, '-');
      }

      return {
        id: String(id || Date.now()),
        title: title || 'Live Event',
        venue: venue || 'Gujarat, India',
        price: parseFloat(price) || 0,
        date: date || 'Upcoming',
        category: category || 'Event',
        thumbnail: thumbnail || '/static/images/music.jpg'
      };
    },

    hasItem(id) {
      return this.items.some(i => String(i.id) === String(id));
    },

    toggleItem(item) {
      const idx = this.items.findIndex(i => String(i.id) === String(item.id));
      let isAdded = false;

      if (idx > -1) {
        this.items.splice(idx, 1);
        isAdded = false;
      } else {
        this.items.unshift(item);
        isAdded = true;
      }

      this.saveToStorage();
      this.syncUI();
      return isAdded;
    },

    removeItem(id) {
      const initialLen = this.items.length;
      this.items = this.items.filter(i => String(i.id) !== String(id));
      if (this.items.length !== initialLen) {
        this.saveToStorage();
        this.syncUI();
      }
    },

    clear() {
      this.items = [];
      this.saveToStorage();
      this.syncUI();
    },

    syncUI() {
      const count = this.items.length;

      // 1. Update Navbar & Menu Badges
      document.querySelectorAll('.wishlist-badge').forEach(elem => {
        elem.textContent = count;
        elem.style.display = count > 0 ? 'inline-flex' : 'none';
        elem.classList.add('pop');
        setTimeout(() => elem.classList.remove('pop'), 200);
      });

      const dot = document.getElementById('hamburgerBadgeDot');
      if (dot) {
        dot.style.display = count > 0 ? 'block' : 'none';
      }

      // 2. Update Subtitle
      if (this.itemCountSubtitle) {
        this.itemCountSubtitle.textContent = `${count} ${count === 1 ? 'event' : 'events'} saved`;
      }

      // 3. Update all Card Like Buttons on the current page
      document.querySelectorAll('.card-like-btn').forEach(btn => {
        const item = this.extractItemData(btn);
        const isLiked = this.hasItem(item.id);

        btn.classList.toggle('liked', isLiked);
        const icon = btn.querySelector('i');
        if (icon) {
          if (isLiked) {
            icon.classList.remove('fa-regular');
            icon.classList.add('fa-solid');
            icon.style.color = 'var(--brand-primary)';
          } else {
            icon.classList.remove('fa-solid');
            icon.classList.add('fa-regular');
            icon.style.color = '';
          }
        }
      });

      // 4. Render Wishlist Items in Drawer
      this.renderDrawer();
    },

    renderDrawer() {
      if (!this.listContainer) return;

      if (this.items.length === 0) {
        this.listContainer.innerHTML = '';
        if (this.emptyState) this.emptyState.style.display = 'flex';
        if (this.totalPriceElem) this.totalPriceElem.textContent = '₹0';
        return;
      }

      if (this.emptyState) this.emptyState.style.display = 'none';

      let totalPrice = 0;
      let html = '';

      this.items.forEach(item => {
        totalPrice += (parseFloat(item.price) || 0);
        html += `
          <div class="wishlist-item-card" data-wishlist-id="${this.escapeHtml(item.id)}">
            <img src="${this.escapeHtml(item.thumbnail)}" alt="${this.escapeHtml(item.title)}" class="wishlist-item-img" onerror="this.src='/static/images/music.jpg'">
            <div class="wishlist-item-info">
              <div>
                <h6 class="wishlist-item-title" title="${this.escapeHtml(item.title)}">${this.escapeHtml(item.title)}</h6>
                <div class="wishlist-item-meta">
                  <span><i class="fa-regular fa-calendar me-1"></i>${this.escapeHtml(item.date)}</span>
                  <span>•</span>
                  <span><i class="fa-solid fa-location-dot me-1"></i>${this.escapeHtml(item.venue)}</span>
                </div>
              </div>
              <div class="wishlist-item-bottom">
                <span class="wishlist-item-price">₹${Math.round(item.price).toLocaleString()}</span>
                <div class="wishlist-item-actions">
                  <button type="button"
                          class="btn-brand wishlist-btn-book"
                          data-book-trigger
                          data-event-id="${this.escapeHtml(item.id)}"
                          data-event-title="${this.escapeHtml(item.title)}"
                          data-event-venue="${this.escapeHtml(item.venue)}"
                          data-event-price="${this.escapeHtml(item.price)}"
                          data-event-date="${this.escapeHtml(item.date)}"
                          data-event-category="${this.escapeHtml(item.category)}">
                    <i class="fa-solid fa-bolt me-1"></i> Book
                  </button>
                  <button type="button"
                          class="wishlist-btn-remove"
                          data-remove-id="${this.escapeHtml(item.id)}"
                          title="Remove from wishlist"
                          aria-label="Remove item">
                    <i class="fa-regular fa-trash-can"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        `;
      });

      this.listContainer.innerHTML = html;

      if (this.totalPriceElem) {
        this.totalPriceElem.textContent = `₹${Math.round(totalPrice).toLocaleString()}`;
      }
    },

    openDrawer() {
      if (this.drawer) this.drawer.classList.add('active');
      if (this.backdrop) this.backdrop.classList.add('active');
      document.body.style.overflow = 'hidden';
      this.syncUI();
    },

    closeDrawer() {
      if (this.drawer) this.drawer.classList.remove('active');
      if (this.backdrop) this.backdrop.classList.remove('active');
      document.body.style.overflow = '';
    },

    isDrawerOpen() {
      return this.drawer && this.drawer.classList.contains('active');
    },

    escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }
  };

  // Initialize on DOM load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => WishlistController.init());
  } else {
    WishlistController.init();
  }

  // Export to window for global access
  window.WishlistController = WishlistController;
  window.Wishlist = WishlistController;
})();
