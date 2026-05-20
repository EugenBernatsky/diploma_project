<script setup lang="ts">
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="footer">
    <div class="footer__inner">
      <div class="footer__brand-column">
        <div class="footer__brand">
          <span class="footer__brand-mark"></span>
          <span>MediaCompass</span>
        </div>

        <p class="footer__description">
          Your ultimate companion for navigating the vast ocean of books, movies, and TV
          series.
        </p>

        <div class="footer__socials">
          <a href="#" aria-label="Twitter">𝕏</a>
          <a href="#" aria-label="Discord">◎</a>
          <a href="#" aria-label="YouTube">◉</a>
        </div>
      </div>

      <div class="footer__links-grid">
        <div class="footer__column">
          <h3>Explore</h3>
          <a href="/catalog">Catalog</a>
          <a href="/recommendations">Recommendations</a>
          <a href="/forum">Community Forum</a>
        </div>

        <div class="footer__column">
          <h3>Company</h3>
          <a href="#">About Us</a>
          <a href="#">Careers</a>
          <a href="#">Contact</a>
        </div>

        <div class="footer__column">
          <h3>Legal</h3>
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
          <a href="#">Cookie Policy</a>
        </div>
      </div>
    </div>

    <div class="footer__bottom">
      <div class="footer__bottom-inner">
        <p>MediaCompass © {{ currentYear }}. All rights reserved.</p>
        <p>Designed for media enthusiasts worldwide.</p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  margin-top: 12px;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
  background: linear-gradient(180deg, rgba(3, 8, 18, 0.96), rgba(2, 6, 23, 1));
}

.footer__inner {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding: 56px 0 40px;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 48px;
}

.footer__brand-column {
  max-width: 420px;
}

.footer__brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
  color: #ffffff;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.footer__brand-mark {
  width: 18px;
  height: 18px;
  border: 2px solid #f8fafc;
  border-radius: 999px;
  box-shadow: 0 0 0 5px rgba(248, 250, 252, 0.08);
}

.footer__description {
  margin: 0 0 20px;
  color: #94a3b8;
  line-height: 1.8;
}

.footer__socials {
  display: flex;
  gap: 16px;
}

.footer__socials a {
  color: #cbd5e1;
  text-decoration: none;
  font-size: 18px;
}

.footer__links-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
}

.footer__column h3 {
  margin: 0 0 18px;
  color: #ffffff;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.footer__column {
  display: grid;
  align-content: start;
  gap: 12px;
}

.footer__column a {
  color: #94a3b8;
  text-decoration: none;
}

.footer__column a:hover {
  color: #60a5fa;
}

.footer__bottom {
  border-top: 1px solid rgba(148, 163, 184, 0.08);
}

.footer__bottom-inner {
  width: min(1320px, calc(100% - 48px));
  margin: 0 auto;
  padding: 22px 0 28px;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}

.footer__bottom-inner p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

@media (max-width: 900px) {
  .footer__inner,
  .footer__bottom-inner {
    width: min(100%, calc(100% - 32px));
  }

  .footer__inner {
    grid-template-columns: 1fr;
  }

  .footer__links-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 560px) {
  .footer__links-grid {
    grid-template-columns: 1fr;
  }
}
</style>