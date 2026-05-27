<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    message: string
    confirmLabel?: string
    cancelLabel?: string
    isDanger?: boolean
    isBusy?: boolean
  }>(),
  {
    confirmLabel: 'Confirm',
    cancelLabel: 'Cancel',
    isDanger: true,
    isBusy: false,
  },
)

const emit = defineEmits<{
  (event: 'confirm'): void
  (event: 'cancel'): void
}>()

function handleCancel() {
  if (props.isBusy) {
    return
  }

  emit('cancel')
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.open) {
    handleCancel()
  }
}

watch(
  () => props.open,
  (value) => {
    document.body.style.overflow = value ? 'hidden' : ''
  },
)

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="confirm-modal"
      @click.self="handleCancel"
    >
      <section class="confirm-modal__dialog">
        <div class="confirm-modal__icon" :class="{ 'confirm-modal__icon--danger': isDanger }">
          !
        </div>

        <div class="confirm-modal__content">
          <h2>{{ title }}</h2>
          <p>{{ message }}</p>
        </div>

        <div class="confirm-modal__actions">
          <button
            type="button"
            class="confirm-modal__button confirm-modal__button--ghost"
            :disabled="isBusy"
            @click="handleCancel"
          >
            {{ cancelLabel }}
          </button>

          <button
            type="button"
            class="confirm-modal__button"
            :class="{ 'confirm-modal__button--danger': isDanger }"
            :disabled="isBusy"
            @click="emit('confirm')"
          >
            {{ isBusy ? 'Processing...' : confirmLabel }}
          </button>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.confirm-modal {
  position: fixed;
  inset: 0;
  z-index: 300;
  padding: 24px;
  background: rgba(2, 6, 23, 0.78);
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-modal__dialog {
  width: min(460px, 100%);
  padding: 26px;
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(8, 14, 24, 0.98);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.42);
  display: grid;
  gap: 18px;
}

.confirm-modal__icon {
  width: 54px;
  height: 54px;
  border-radius: 18px;
  background: rgba(96, 165, 250, 0.16);
  color: #bfdbfe;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 900;
}

.confirm-modal__icon--danger {
  background: rgba(239, 68, 68, 0.14);
  color: #fca5a5;
}

.confirm-modal__content h2 {
  margin: 0 0 10px;
  color: #f8fafc;
  font-size: 26px;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.confirm-modal__content p {
  margin: 0;
  color: #94a3b8;
  line-height: 1.7;
}

.confirm-modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.confirm-modal__button {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  font-weight: 900;
  cursor: pointer;
}

.confirm-modal__button--ghost {
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
}

.confirm-modal__button--danger {
  background: linear-gradient(135deg, #dc2626 0%, #f97316 100%);
}

.confirm-modal__button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 560px) {
  .confirm-modal__actions {
    display: grid;
    grid-template-columns: 1fr;
  }

  .confirm-modal__button {
    width: 100%;
  }
}
</style>