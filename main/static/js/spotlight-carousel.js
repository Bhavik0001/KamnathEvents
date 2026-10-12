/**
 * ==========================================================================
 * HERO SPOTLIGHT EVENT CAROUSEL (Production-Grade ES6 Module)
 * Smooth cross-fade animation, dot pagination, slide counter,
 * keyboard accessibility, touch swipe detection, and pause-on-hover.
 * ==========================================================================
 */

(function () {
  'use strict';

  const SpotlightCarousel = {
    container: null,
    slides: [],
    dots: [],
    prevBtn: null,
    nextBtn: null,
    counter: null,
    dotsContainer: null,
    currentIndex: 0,
    timer: null,
    interval: 5000,
    touchStartX: 0,
    touchStartY: 0,
    touchEndX: 0,
    touchEndY: 0,

    init() {
      this.container = document.querySelector('.hero-spotlight-carousel');
      if (!this.container) return;

      this.slides = Array.from(this.container.querySelectorAll('.spotlight-slide'));
      if (this.slides.length === 0) return;

      this.prevBtn = this.container.querySelector('.spotlight-nav-btn.prev');
      this.nextBtn = this.container.querySelector('.spotlight-nav-btn.next');
      this.counter = this.container.querySelector('.spotlight-counter, #spotlightCounter');
      this.dotsContainer = this.container.querySelector('.spotlight-dots-bar');

      // Handle single-slide edge case
      if (this.slides.length <= 1) {
        this.container.classList.add('single-slide');
        if (this.prevBtn) this.prevBtn.disabled = true;
        if (this.nextBtn) this.nextBtn.disabled = true;
        this.updateCounter();
        return;
      }

      this.container.classList.remove('single-slide');
      this.syncDots();
      this.bindEvents();
      this.updateCounter();
      this.startAutoPlay();
    },

    syncDots() {
      if (!this.dotsContainer) return;

      // Existing dots check
      this.dots = Array.from(this.dotsContainer.querySelectorAll('.spotlight-dot'));

      // If dots do not match slides count, rebuild dots
      if (this.dots.length !== this.slides.length) {
        this.dotsContainer.innerHTML = '';
        this.dots = this.slides.map((_, idx) => {
          const dot = document.createElement('button');
          dot.type = 'button';
          dot.className = `spotlight-dot ${idx === this.currentIndex ? 'active' : ''}`;
          dot.setAttribute('data-index', idx);
          dot.setAttribute('aria-label', `Go to slide ${idx + 1}`);
          this.dotsContainer.appendChild(dot);
          return dot;
        });
      } else {
        this.dots.forEach((dot, idx) => {
          dot.classList.toggle('active', idx === this.currentIndex);
        });
      }
    },

    updateCounter() {
      if (this.counter && this.slides.length > 0) {
        this.counter.textContent = `${this.currentIndex + 1} / ${this.slides.length}`;
      }
    },

    goTo(index) {
      if (this.slides.length <= 1) return;

      const previousIndex = this.currentIndex;
      this.currentIndex = (index + this.slides.length) % this.slides.length;

      if (previousIndex === this.currentIndex) return;

      // Deactivate current slide and dot
      if (this.slides[previousIndex]) {
        this.slides[previousIndex].classList.remove('active');
        this.slides[previousIndex].setAttribute('aria-hidden', 'true');
      }
      if (this.dots[previousIndex]) {
        this.dots[previousIndex].classList.remove('active');
      }

      // Activate target slide and dot
      if (this.slides[this.currentIndex]) {
        this.slides[this.currentIndex].classList.add('active');
        this.slides[this.currentIndex].setAttribute('aria-hidden', 'false');
      }
      if (this.dots[this.currentIndex]) {
        this.dots[this.currentIndex].classList.add('active');
      }

      this.updateCounter();
    },

    next() {
      this.goTo(this.currentIndex + 1);
    },

    prev() {
      this.goTo(this.currentIndex - 1);
    },

    bindEvents() {
      if (this.nextBtn) {
        this.nextBtn.addEventListener('click', (e) => {
          e.preventDefault();
          this.next();
          this.restartAutoPlay();
        });
      }

      if (this.prevBtn) {
        this.prevBtn.addEventListener('click', (e) => {
          e.preventDefault();
          this.prev();
          this.restartAutoPlay();
        });
      }

      if (this.dotsContainer) {
        this.dotsContainer.addEventListener('click', (e) => {
          const dot = e.target.closest('.spotlight-dot');
          if (dot) {
            e.preventDefault();
            const targetIdx = parseInt(dot.getAttribute('data-index'), 10);
            if (!isNaN(targetIdx)) {
              this.goTo(targetIdx);
              this.restartAutoPlay();
            }
          }
        });
      }

      // Pause on hover
      this.container.addEventListener('mouseenter', () => this.stopAutoPlay());
      this.container.addEventListener('mouseleave', () => this.startAutoPlay());

      // Keyboard navigation
      this.container.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight') {
          e.preventDefault();
          this.next();
          this.restartAutoPlay();
        } else if (e.key === 'ArrowLeft') {
          e.preventDefault();
          this.prev();
          this.restartAutoPlay();
        }
      });

      // Touch swipe gestures
      this.container.addEventListener('touchstart', (e) => {
        if (e.touches && e.touches.length > 0) {
          this.touchStartX = e.touches[0].clientX;
          this.touchStartY = e.touches[0].clientY;
        }
      }, { passive: true });

      this.container.addEventListener('touchend', (e) => {
        if (e.changedTouches && e.changedTouches.length > 0) {
          this.touchEndX = e.changedTouches[0].clientX;
          this.touchEndY = e.changedTouches[0].clientY;
          this.handleSwipeGesture();
        }
      }, { passive: true });
    },

    handleSwipeGesture() {
      const deltaX = this.touchStartX - this.touchEndX;
      const deltaY = this.touchStartY - this.touchEndY;

      // Ensure horizontal swipe is dominant and exceeds minimum threshold
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 40) {
        if (deltaX > 0) {
          this.next();
        } else {
          this.prev();
        }
        this.restartAutoPlay();
      }
    },

    startAutoPlay() {
      if (this.slides.length <= 1) return;
      if (this.timer) clearInterval(this.timer);
      this.timer = setInterval(() => this.next(), this.interval);
    },

    stopAutoPlay() {
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }
    },

    restartAutoPlay() {
      this.stopAutoPlay();
      this.startAutoPlay();
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => SpotlightCarousel.init());
  } else {
    SpotlightCarousel.init();
  }

  window.SpotlightCarousel = SpotlightCarousel;
})();
