<template>
  <footer class="footer">
    <div class="footer__inner">
      <div>
        <p class="footer__brand">MediaCompass</p>
        <p class="footer__text">
          Веб-портал для підбору медіа-контенту на основі гібридної моделі рекомендацій.
        </p>
      </div>

      <div class="footer__links">
        <a href="#" class="footer__link">GitHub</a>
        <a href="#" class="footer__link">LinkedIn</a>
        <a href="#" class="footer__link">Контакти</a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  width: 100%;
  border-top: 1px solid #1f2937;
  background: #020617;
}

.footer__inner {
  width: min(1200px, calc(100% - 32px));
  margin: 0 auto;
  padding: 24px 0;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}

.footer__brand {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 700;
  color: #f8fafc;
}

.footer__text {
  margin: 0;
  max-width: 560px;
  color: #94a3b8;
}

.footer__links {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: center;
}

.footer__link {
  color: #cbd5e1;
  text-decoration: none;
  font-weight: 600;
}

.footer__link:hover {
  color: #60a5fa;
}
</style>