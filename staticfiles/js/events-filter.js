/**
 * ==========================================================================
 * EVENT FILTER, SEARCH & DISCOVERY ENGINE (ES6 Modular Standard)
 * Features: Debounced Search, Category Chips, City Filter, Price Sort,
 *           Empty State Management, Dynamic Card Counter, URL Sync
 * ==========================================================================
 */

(function () {
  'use strict';

  const EventFilterEngine = {
    cards: [],
    searchInput: null,
    categoryChips: [],
    categorySelect: null,
    cityFilter: 'All Cities',
    dateChips: [],
    sortSelect: null,
    resultsCounter: null,
    resetBtn: null,
    emptyState: null,

    state: {
      search: '',
      category: 'all',
      city: 'All Cities',
      date: 'all',
      sort: 'featured'
    },

    init() {
      // 1. Read URL query param ?category=... and ?city=...
      const urlParams = new URLSearchParams(window.location.search);
      const categoryFromUrl = urlParams.get('category');
      if (categoryFromUrl && categoryFromUrl.toLowerCase() !== 'all') {
        this.state.category = categoryFromUrl.toLowerCase().trim();
      } else {
        this.state.category = 'all';
      }

      const cityFromUrl = urlParams.get('city');
      if (cityFromUrl && cityFromUrl.toLowerCase() !== 'all' && cityFromUrl.toLowerCase() !== 'all cities') {
        this.state.city = cityFromUrl.trim();
      } else {
        // ALWAYS default to All Cities on catalog page so all events are visible
        this.state.city = 'All Cities';
        try {
          localStorage.setItem('eventhub_city', 'All Cities');
        } catch (e) {}
      }

      // Sync header city label if on All Cities
      const currentCityLabel = document.getElementById('currentCityLabel');
      if (currentCityLabel && this.state.city === 'All Cities') {
        currentCityLabel.textContent = 'All Cities';
      }
      const cityCards = document.querySelectorAll('.city-card-item');
      if (cityCards.length && this.state.city === 'All Cities') {
        cityCards.forEach(c => {
          c.classList.toggle('selected', (c.getAttribute('data-city') || '') === 'All Cities');
        });
      }

      this.categoryChips = document.querySelectorAll('.category-chip');
      const container = document.getElementById('eventsContainer');

      // If on a page without events container (e.g. About, Contact), clicking a category chip navigates to /events/
      if (!container) {
        this.categoryChips.forEach(chip => {
          chip.addEventListener('click', (e) => {
            e.preventDefault();
            const cat = chip.getAttribute('data-category') || 'all';
            window.location.href = `/events/?category=${encodeURIComponent(cat)}`;
          });
        });
        return;
      }

      this.cards = Array.from(container.querySelectorAll('.event-card-wrapper'));
      this.searchInput = document.querySelector('.search-input');
      this.categorySelect = document.getElementById('categoryFilterSelect');
      this.dateChips = document.querySelectorAll('.date-chip-btn');
      this.sortSelect = document.getElementById('sortFilterSelect');
      this.resultsCounter = document.getElementById('resultsCounter');
      this.resetBtn = document.getElementById('resetFiltersBtn');
      this.emptyState = document.getElementById('emptyStateContainer');

      // Sync active state on category chips based on initial category
      this.syncActiveCategoryChips();

      // Sync select dropdown if initial category is set
      if (this.categorySelect && this.state.category !== 'all') {
        Array.from(this.categorySelect.options).forEach(opt => {
          if (this.checkCategoryMatch(opt.value, this.state.category)) {
            this.categorySelect.value = opt.value;
          }
        });
      }

      this.bindEvents();
      this.bindLikes();
      this.applyFilters();
    },

    syncActiveCategoryChips() {
      this.categoryChips.forEach(c => {
        const cCat = (c.getAttribute('data-category') || 'all').toLowerCase().trim();
        if (this.state.category === 'all') {
          c.classList.toggle('active', cCat === 'all');
        } else {
          c.classList.toggle('active', cCat !== 'all' && this.checkCategoryMatch(cCat, this.state.category));
        }
      });
    },

    bindEvents() {
      // Debounced search input
      if (this.searchInput) {
        let timeout = null;
        this.searchInput.addEventListener('input', (e) => {
          clearTimeout(timeout);
          timeout = setTimeout(() => {
            this.state.search = e.target.value.trim().toLowerCase();
            this.applyFilters();
          }, 200);
        });
      }

      // Category chips (subnav & in-page chips)
      this.categoryChips.forEach(chip => {
        chip.addEventListener('click', (e) => {
          e.preventDefault();
          const category = (chip.getAttribute('data-category') || 'all').toLowerCase().trim();
          this.state.category = category;

          this.syncActiveCategoryChips();

          // Sync category select dropdown if present
          if (this.categorySelect) {
            let matched = false;
            Array.from(this.categorySelect.options).forEach(opt => {
              if (this.checkCategoryMatch(opt.value, category)) {
                this.categorySelect.value = opt.value;
                matched = true;
              }
            });
            if (!matched && category === 'all') {
              this.categorySelect.value = 'all';
            }
          }

          this.applyFilters();
        });
      });

      // Category select dropdown
      if (this.categorySelect) {
        this.categorySelect.addEventListener('change', (e) => {
          this.state.category = e.target.value.toLowerCase().trim();
          this.syncActiveCategoryChips();
          this.applyFilters();
        });
      }

      // Date chips
      this.dateChips.forEach(chip => {
        chip.addEventListener('click', () => {
          this.dateChips.forEach(c => c.classList.remove('active'));
          chip.classList.add('active');
          this.state.date = chip.getAttribute('data-date') || 'all';
          this.applyFilters();
        });
      });

      // Sort Select
      if (this.sortSelect) {
        this.sortSelect.addEventListener('change', (e) => {
          this.state.sort = e.target.value;
          this.applySort();
        });
      }

      // Reset filters button
      if (this.resetBtn) {
        this.resetBtn.addEventListener('click', () => {
          this.resetFilters();
        });
      }

      // Listen for city change event from CityManager
      window.addEventListener('cityChanged', (e) => {
        this.state.city = e.detail.city;
        this.applyFilters();
      });
    },

    checkCategoryMatch(cardCategory, targetCategory) {
      if (!targetCategory || targetCategory === 'all') return true;
      if (!cardCategory) return false;

      const cardCat = cardCategory.toLowerCase().trim();
      const targetCat = targetCategory.toLowerCase().trim();

      if (cardCat === targetCat) return true;
      if (cardCat.includes(targetCat) || targetCat.includes(cardCat)) return true;

      // Handle common spelling variations & synonyms
      // Comedy / Commedy
      const isComedyCard = cardCat === 'comedy' || cardCat === 'commedy';
      const isComedyTarget = targetCat === 'comedy' || targetCat === 'commedy';
      if (isComedyCard && isComedyTarget) return true;

      // Music / Concert / Concerts
      const isMusicCard = cardCat === 'music' || cardCat === 'concert' || cardCat === 'concerts';
      const isMusicTarget = targetCat === 'music' || targetCat === 'concert' || targetCat === 'concerts';
      if (isMusicCard && isMusicTarget) return true;

      // Business / Conferences / Busines
      const isBizCard = cardCat === 'business' || cardCat === 'busines' || cardCat === 'conferences' || cardCat === 'conference';
      const isBizTarget = targetCat === 'business' || targetCat === 'busines' || targetCat === 'conferences' || targetCat === 'conference';
      if (isBizCard && isBizTarget) return true;

      // Workshop / Workshops
      const isWorkshopCard = cardCat === 'workshop' || cardCat === 'workshops';
      const isWorkshopTarget = targetCat === 'workshop' || targetCat === 'workshops';
      if (isWorkshopCard && isWorkshopTarget) return true;

      // Fashion
      if (cardCat.startsWith('fashion') && targetCat.startsWith('fashion')) return true;

      return false;
    },

    applyFilters() {
      let visibleCount = 0;
      const isFilterActive = (this.state.search !== '' && this.state.search !== null) ||
                             (this.state.category !== 'all' && this.state.category !== '') ||
                             (this.state.city !== 'All Cities' && this.state.city !== 'All' && this.state.city !== '') ||
                             (this.state.date !== 'all' && this.state.date !== '');

      if (this.resetBtn) {
        this.resetBtn.classList.toggle('show', Boolean(isFilterActive));
      }

      this.cards.forEach(wrapper => {
        const card = wrapper.querySelector('.event-card');
        if (!card) return;

        const title = card.getAttribute('data-title')?.toLowerCase() || '';
        const venue = card.getAttribute('data-venue')?.toLowerCase() || '';
        const category = card.getAttribute('data-category')?.toLowerCase() || '';
        const city = card.getAttribute('data-city')?.toLowerCase() || '';
        const dateStr = card.getAttribute('data-date') || '';

        // Search Match
        const matchesSearch = !this.state.search ||
          title.includes(this.state.search) ||
          venue.includes(this.state.search) ||
          this.checkCategoryMatch(category, this.state.search);

        // Category Match
        const matchesCategory = this.state.category === 'all' ||
          this.checkCategoryMatch(category, this.state.category);

        // City Match
        const selectedCity = (this.state.city || '').toLowerCase().trim();
        const matchesCity = !selectedCity ||
          selectedCity === 'all cities' ||
          selectedCity === 'all' ||
          city.includes(selectedCity) ||
          venue.includes(selectedCity) ||
          (selectedCity.includes('vadod') && (city.includes('vadod') || venue.includes('vadod'))) ||
          ((selectedCity.includes('gandhi') || selectedCity.includes('ghandhi')) && 
           (city.includes('gandhi') || venue.includes('gandhi') || city.includes('ghandhi') || venue.includes('ghandhi')));

        // Date Match
        let matchesDate = true;
        if (this.state.date === 'today') {
          const today = new Date().toISOString().split('T')[0];
          matchesDate = dateStr === today;
        } else if (this.state.date === 'weekend') {
          const d = new Date(dateStr);
          const day = d.getDay();
          matchesDate = day === 0 || day === 6;
        }

        if (matchesSearch && matchesCategory && matchesCity && matchesDate) {
          wrapper.style.display = '';
          visibleCount++;
        } else {
          wrapper.style.display = 'none';
        }
      });

      // Update Result Counter
      if (this.resultsCounter) {
        this.resultsCounter.textContent = `Showing ${visibleCount} of ${this.cards.length} events`;
      }

      // Empty State Display
      if (this.emptyState) {
        this.emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
      }

      this.applySort();
    },

    applySort() {
      const container = document.getElementById('eventsContainer');
      if (!container) return;

      const visibleWrappers = this.cards.filter(w => w.style.display !== 'none');

      visibleWrappers.sort((a, b) => {
        const cardA = a.querySelector('.event-card');
        const cardB = b.querySelector('.event-card');
        const priceA = parseFloat(cardA?.getAttribute('data-price') || 0);
        const priceB = parseFloat(cardB?.getAttribute('data-price') || 0);
        const dateA = cardA?.getAttribute('data-date') || '';
        const dateB = cardB?.getAttribute('data-date') || '';

        if (this.state.sort === 'price-low') {
          return priceA - priceB;
        } else if (this.state.sort === 'price-high') {
          return priceB - priceA;
        } else if (this.state.sort === 'date-asc') {
          return dateA.localeCompare(dateB);
        } else if (this.state.sort === 'date-desc') {
          return dateB.localeCompare(dateA);
        }
        return 0; // Default order
      });

      visibleWrappers.forEach(wrapper => container.appendChild(wrapper));
    },

    resetFilters() {
      this.state.search = '';
      this.state.category = 'all';
      this.state.city = 'All Cities';
      this.state.date = 'all';
      this.state.sort = 'featured';

      if (this.searchInput) this.searchInput.value = '';
      if (this.categorySelect) this.categorySelect.value = 'all';
      if (this.sortSelect) this.sortSelect.value = 'featured';

      // Clear query params from URL so refreshing will not re-apply filters
      if (window.history && window.history.replaceState) {
        window.history.replaceState({}, document.title, window.location.pathname);
      }

      // Reset stored city and header label
      try {
        localStorage.setItem('eventhub_city', 'All Cities');
      } catch (e) {}

      const currentCityLabel = document.getElementById('currentCityLabel');
      if (currentCityLabel) {
        currentCityLabel.textContent = 'All Cities';
      }

      // Reset city modal active items
      const cityItems = document.querySelectorAll('.city-card-item');
      cityItems.forEach(i => {
        const c = i.getAttribute('data-city');
        i.classList.toggle('selected', c === 'All Cities');
      });

      this.syncActiveCategoryChips();

      this.dateChips.forEach(c => {
        c.classList.toggle('active', c.getAttribute('data-date') === 'all');
      });

      if (this.resetBtn) {
        this.resetBtn.classList.remove('show');
      }

      this.applyFilters();

      if (window.AppToast) {
        window.AppToast.show('All filters reset', 'success', 2000);
      }
    },

    bindLikes() {
      // Delegated to window.Wishlist controller for persistent storage and drawer integration
      if (window.Wishlist && typeof window.Wishlist.syncUI === 'function') {
        window.Wishlist.syncUI();
      }
    }
  };

  document.addEventListener('DOMContentLoaded', () => {
    EventFilterEngine.init();
  });

  window.EventFilterEngine = EventFilterEngine;
})();
