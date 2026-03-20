<template>
  <section class="home-page">
    <div class="home-page__inner">
      <section class="hero">
        <p class="hero__tag">MediaCompass</p>
        <h2 class="hero__title">Розумний підбір медіа-контенту в одному просторі</h2>
        <p class="hero__text">
          Тут буде головна сторінка з коротким описом сервісу, нещодавно доданими
          елементами, популярними категоріями та блоком персоналізованих рекомендацій.
        </p>
      </section>

      <section class="section-card">
        <h3 class="section-card__title">Нещодавно додані</h3>
        <div class="carousel-placeholder">
          <div class="carousel-item">Новий фільм</div>
          <div class="carousel-item">Новий серіал</div>
          <div class="carousel-item">Нова книга</div>
        </div>
      </section>

      <section class="section-card">
        <h3 class="section-card__title">Що буде на цій сторінці</h3>
        <ul class="feature-list">
          <li>Карусель нових айтемів</li>
          <li>Короткий опис платформи</li>
          <li>Популярні категорії</li>
          <li>Блок персональних рекомендацій</li>
        </ul>
      </section>
    </div>
  </section>
</template>

<style scoped>
.home-page {
  width: 100%;
  padding: 40px 16px 56px;
}

.home-page__inner {
  width: min(1100px, 100%);
  margin: 0 auto;
  display: grid;
  gap: 24px;
}

.hero,
.section-card {
  padding: 32px;
  border-radius: 24px;
  background: #071533;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
}

.hero__tag {
  margin: 0 0 12px;
  color: #60a5fa;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 14px;
}

.hero__title {
  margin: 0 0 16px;
  font-size: 48px;
  line-height: 1.1;
  color: #f8fafc;
}

.hero__text {
  margin: 0;
  max-width: 760px;
  color: #cbd5e1;
  font-size: 20px;
}

.section-card__title {
  margin: 0 0 18px;
  font-size: 28px;
  color: #f8fafc;
}

.carousel-placeholder {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.carousel-item {
  padding: 24px;
  border-radius: 18px;
  background: #1f2937;
  border: 1px solid #253043;
  color: #e5e7eb;
  font-weight: 600;
  text-align: center;
}

.feature-list {
  margin: 0;
  padding-left: 20px;
  color: #cbd5e1;
  display: grid;
  gap: 10px;
}

@media (max-width: 768px) {
  .hero,
  .section-card {
    padding: 24px;
  }

  .hero__title {
    font-size: 36px;
  }

  .hero__text {
    font-size: 18px;
  }
}
</style>