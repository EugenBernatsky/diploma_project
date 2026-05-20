<template>
  <section class="forum-cta">
    <h2 class="forum-cta__title">Can’t find what you’re looking for?</h2>
    <p class="forum-cta__text">
      Start a new discussion and get the conversation moving. Your community can
      help with recommendations, theories, and feedback.
    </p>

    <button type="button" class="forum-cta__button">
      + Create New Topic
    </button>
  </section>
</template>

<style scoped>
.forum-cta {
  padding: 40px 24px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background:
    radial-gradient(circle at center, rgba(37, 99, 235, 0.16), transparent 40%),
    rgba(8, 14, 24, 0.9);
  text-align: center;
}

.forum-cta__title {
  margin: 0 0 12px;
  color: #f8fafc;
  font-size: 34px;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.forum-cta__text {
  max-width: 760px;
  margin: 0 auto 22px;
  color: #94a3b8;
  line-height: 1.8;
  font-size: 16px;
}

.forum-cta__button {
  min-height: 48px;
  padding: 0 18px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
}
</style>