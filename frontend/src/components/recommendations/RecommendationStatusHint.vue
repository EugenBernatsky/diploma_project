<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
}>()

const statusMessages: Record<string, string> = {
  personalized: 'Recommendations are based on your activity.',
  available: '',
  cold_start_fallback:
    'Rate, save or open more items to improve your personal recommendations.',
  personalized_fallback:
    'We need a bit more positive activity to make this section more accurate.',
  waiting_for_more_user_data:
    'This section will improve after more users rate media items.',
  model_not_trained: 'Recommendations are temporarily unavailable.',
  unavailable: 'No recommendations available right now.',
}

const message = computed(() => {
  return statusMessages[props.status] ?? ''
})
</script>

<template>
  <p v-if="message" class="recommendation-status-hint">
    {{ message }}
  </p>
</template>

<style scoped>
.recommendation-status-hint {
  margin: 0;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(37, 99, 235, 0.12);
  border: 1px solid rgba(96, 165, 250, 0.14);
  color: #bfdbfe;
  font-size: 14px;
  line-height: 1.6;
}
</style>