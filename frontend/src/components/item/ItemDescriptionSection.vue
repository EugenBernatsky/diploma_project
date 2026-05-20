<script setup lang="ts">
defineProps<{
  title: string
  description: string
}>()
</script>

<template>
  <section class="item-description">
    <h2 class="item-description__title">{{ title }}</h2>
    <p class="item-description__text">
      {{ description }}
    </p>
  </section>
</template>

<style scoped>
.item-description {
  padding: 28px 30px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(8, 14, 24, 0.9);
}

.item-description__title {
  margin: 0 0 18px;
  color: #f8fafc;
  font-size: 34px;
  line-height: 1;
  letter-spacing: -0.03em;
}

.item-description__text {
  margin: 0;
  color: #cbd5e1;
  font-size: 18px;
  line-height: 1.9;
}
</style>