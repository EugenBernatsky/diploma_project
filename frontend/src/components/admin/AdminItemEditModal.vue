<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { updateAdminItem } from '../../services/admin'
import type {
  AdminItemUpdatePayload,
  AdminPurchaseLinkPayload,
} from '../../types/admin'
import type { Category, MediaItem, MediaProviderLink, MediaTrailer } from '../../types/media'

const props = defineProps<{
  open: boolean
  item: MediaItem | null
}>()

const emit = defineEmits<{
  (event: 'close'): void
  (event: 'saved', item: MediaItem): void
}>()

type FormState = {
  title: string
  category: Category
  year: string
  genres: string
  description: string
  poster_url: string
  backdrop_url: string
  runtime: string
  page_count: string
  trailers: string
  watch_links: string
  purchase_links: string
}

const form = reactive<FormState>({
  title: '',
  category: 'movie',
  year: '',
  genres: '',
  description: '',
  poster_url: '',
  backdrop_url: '',
  runtime: '',
  page_count: '',
  trailers: '',
  watch_links: '',
  purchase_links: '',
})

const isSaving = ref(false)
const errorText = ref('')

const modalTitle = computed(() => {
  return props.item ? `Edit: ${props.item.title}` : 'Edit Item'
})

function emptyToNull(value: string): string | null {
  const trimmed = value.trim()
  return trimmed ? trimmed : null
}

function parseRequiredNumber(value: string, label: string): number {
  const trimmed = value.trim()
  const parsed = Number(trimmed)

  if (!trimmed || !Number.isFinite(parsed)) {
    throw new Error(`${label} must be a valid number.`)
  }

  return Math.trunc(parsed)
}

function parseOptionalNumber(value: string, label: string): number | null {
  const trimmed = value.trim()

  if (!trimmed) {
    return null
  }

  const parsed = Number(trimmed)

  if (!Number.isFinite(parsed)) {
    throw new Error(`${label} must be a valid number.`)
  }

  return Math.trunc(parsed)
}

function serializeTrailers(trailers?: MediaTrailer[]): string {
  return (trailers ?? [])
    .map((trailer) => {
      return [
        trailer.name,
        trailer.site,
        trailer.url,
        trailer.language ?? '',
      ].join(' | ')
    })
    .join('\n')
}

function serializeProviderLinks(links?: MediaProviderLink[]): string {
  return (links ?? [])
    .map((link) => {
      return [
        link.provider_name,
        link.provider_type,
        link.region ?? '',
        link.url,
      ].join(' | ')
    })
    .join('\n')
}

function parseTrailers(value: string): MediaTrailer[] {
  const lines = value
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)

  return lines.map((line, index) => {
    const parts = line.split('|').map((part) => part.trim())

    if (parts.length < 3) {
      throw new Error(
        `Trailer line ${index + 1} must use format: name | site | url | language`,
      )
    }

    const [name, site, url, language] = parts

    if (!name || !site || !url) {
      throw new Error(
        `Trailer line ${index + 1} must include name, site and url.`,
      )
    }

    return {
      name,
      site,
      url,
      language: language || null,
    }
  })
}

function parseProviderLinks(value: string, label: string): MediaProviderLink[] {
  const lines = value
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)

  return lines.map((line, index) => {
    const parts = line.split('|').map((part) => part.trim())

    if (parts.length < 4) {
      throw new Error(
        `${label} line ${index + 1} must use format: provider | type | region | url`,
      )
    }

    const [provider_name, provider_type, region, url] = parts

    if (!provider_name || !provider_type || !url) {
      throw new Error(
        `${label} line ${index + 1} must include provider, type and url.`,
      )
    }

    return {
      provider_name,
      provider_type,
      region: region || null,
      url,
    }
  })
}

function parsePurchaseLinks(value: string): AdminPurchaseLinkPayload[] {
  const lines = value
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)

  return lines.map((line, index) => {
    const parts = line.split('|').map((part) => part.trim())

    if (parts.length < 4) {
      throw new Error(
        `Purchase link line ${index + 1} must use format: store | type | region | url`,
      )
    }

    const [store_name, provider_type, region, url] = parts

    if (!store_name || !url) {
      throw new Error(
        `Purchase link line ${index + 1} must include store name and url.`,
      )
    }

    return {
      store_name,
      provider_type: provider_type || null,
      region: region || null,
      url,
    }
  })
}

function resetForm(item: MediaItem) {
  form.title = item.title ?? ''
  form.category = item.category
  form.year = item.year ? String(item.year) : ''
  form.genres = item.genres?.join(', ') ?? ''
  form.description = item.description ?? ''
  form.poster_url = item.poster_url ?? ''
  form.backdrop_url = item.backdrop_url ?? ''
  form.runtime = item.runtime ? String(item.runtime) : ''
  form.page_count = item.page_count ? String(item.page_count) : ''
  form.trailers = serializeTrailers(item.trailers)
  form.watch_links = serializeProviderLinks(item.watch_links)
  form.purchase_links = serializeProviderLinks(item.purchase_links)
  errorText.value = ''
}

function buildPayload(): AdminItemUpdatePayload {
  return {
    title: form.title.trim(),
    category: form.category,
    year: parseRequiredNumber(form.year, 'Year'),
    genres: form.genres
      .split(',')
      .map((genre) => genre.trim())
      .filter(Boolean),
    description: form.description.trim(),
    poster_url: emptyToNull(form.poster_url),
    backdrop_url: emptyToNull(form.backdrop_url),
    runtime: parseOptionalNumber(form.runtime, 'Runtime'),
    page_count: parseOptionalNumber(form.page_count, 'Page count'),
    trailers: parseTrailers(form.trailers),
    watch_links: parseProviderLinks(form.watch_links, 'Watch link'),
    purchase_links: parsePurchaseLinks(form.purchase_links),
  }
}

function closeModal() {
  if (isSaving.value) {
    return
  }

  emit('close')
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.open) {
    closeModal()
  }
}

async function handleSave() {
  if (!props.item) {
    return
  }

  isSaving.value = true
  errorText.value = ''

  try {
    const payload = buildPayload()
    const updatedItem = await updateAdminItem(props.item.id, payload)

    emit('saved', updatedItem)
  } catch (error) {
    errorText.value =
      error instanceof Error ? error.message : 'Failed to update item.'
  } finally {
    isSaving.value = false
  }
}

watch(
  () => [props.open, props.item?.id],
  () => {
    if (props.open && props.item) {
      resetForm(props.item)
    }
  },
)

watch(
  () => props.open,
  (value) => {
    document.body.style.overflow = value ? 'hidden' : ''
  },
)

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)

  if (props.open && props.item) {
    resetForm(props.item)
  }
})

onUnmounted(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open && item"
      class="admin-item-edit"
      @click.self="closeModal"
    >
      <section class="admin-item-edit__dialog">
        <header class="admin-item-edit__header">
          <div>
            <p class="admin-item-edit__eyebrow">Admin Edit</p>
            <h2>{{ modalTitle }}</h2>
            <span>
              Update main item fields, trailers and external provider links.
            </span>
          </div>

          <button
            type="button"
            class="admin-item-edit__close"
            aria-label="Close edit item modal"
            :disabled="isSaving"
            @click="closeModal"
          >
            ✕
          </button>
        </header>

        <div v-if="errorText" class="admin-item-edit__error">
          {{ errorText }}
        </div>

        <div class="admin-item-edit__content">
          <section class="admin-item-edit__section">
            <h3>Main fields</h3>

            <div class="admin-item-edit__grid">
              <label class="admin-item-edit__field">
                <span>Title</span>
                <input v-model="form.title" type="text" />
              </label>

              <label class="admin-item-edit__field">
                <span>Category</span>
                <select v-model="form.category">
                  <option value="movie">Movie</option>
                  <option value="series">Series</option>
                  <option value="book">Book</option>
                </select>
              </label>

              <label class="admin-item-edit__field">
                <span>Year</span>
                <input v-model="form.year" type="number" />
              </label>

              <label class="admin-item-edit__field">
                <span>Genres, comma separated</span>
                <input v-model="form.genres" type="text" placeholder="Drama, Sci-Fi" />
              </label>

              <label class="admin-item-edit__field">
                <span>Runtime, minutes</span>
                <input v-model="form.runtime" type="number" placeholder="120" />
              </label>

              <label class="admin-item-edit__field">
                <span>Page count</span>
                <input v-model="form.page_count" type="number" placeholder="350" />
              </label>
            </div>

            <label class="admin-item-edit__field">
              <span>Description</span>
              <textarea v-model="form.description" rows="5"></textarea>
            </label>
          </section>

          <section class="admin-item-edit__section">
            <h3>Images</h3>

            <div class="admin-item-edit__grid">
              <label class="admin-item-edit__field">
                <span>Poster URL</span>
                <input v-model="form.poster_url" type="url" />
              </label>

              <label class="admin-item-edit__field">
                <span>Backdrop URL</span>
                <input v-model="form.backdrop_url" type="url" />
              </label>
            </div>
          </section>

          <section class="admin-item-edit__section">
            <h3>Trailers</h3>

            <p class="admin-item-edit__hint">
              One trailer per line. Format:
              <strong>name | site | url | language</strong>
            </p>

            <label class="admin-item-edit__field">
              <span>Trailer links</span>
              <textarea
                v-model="form.trailers"
                rows="5"
                placeholder="Official Trailer | YouTube | https://youtube.com/... | en"
              ></textarea>
            </label>
          </section>

          <section class="admin-item-edit__section">
            <h3>Watch links</h3>

            <p class="admin-item-edit__hint">
              One provider per line. Format:
              <strong>provider | type | region | url</strong>
            </p>

            <label class="admin-item-edit__field">
              <span>Watch providers</span>
              <textarea
                v-model="form.watch_links"
                rows="5"
                placeholder="Netflix | stream | US | https://..."
              ></textarea>
            </label>
          </section>

          <section class="admin-item-edit__section">
            <h3>Purchase links</h3>

            <p class="admin-item-edit__hint">
              One provider per line. Format:
              <strong>provider | type | region | url</strong>
            </p>

            <label class="admin-item-edit__field">
              <span>Purchase providers</span>
              <textarea
                v-model="form.purchase_links"
                rows="5"
                placeholder="Amazon | buy | US | https://..."
              ></textarea>
            </label>
          </section>
        </div>

        <footer class="admin-item-edit__footer">
          <button
            type="button"
            class="admin-item-edit__button admin-item-edit__button--ghost"
            :disabled="isSaving"
            @click="closeModal"
          >
            Cancel
          </button>

          <button
            type="button"
            class="admin-item-edit__button"
            :disabled="isSaving"
            @click="handleSave"
          >
            {{ isSaving ? 'Saving...' : 'Save changes' }}
          </button>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.admin-item-edit {
  position: fixed;
  inset: 0;
  z-index: 260;
  padding: 24px;
  background: rgba(2, 6, 23, 0.78);
  display: flex;
  align-items: center;
  justify-content: center;
}

.admin-item-edit__dialog {
  width: min(1100px, 100%);
  max-height: 90vh;
  overflow: hidden;
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr) auto;
  grid-template-areas:
    "header"
    "error"
    "content"
    "footer";
  border-radius: 26px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(8, 14, 24, 0.98);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.42);
}

.admin-item-edit__header {
  grid-area: header;
}

.admin-item-edit__error {
  grid-area: error;
}

.admin-item-edit__content {
  grid-area: content;
}

.admin-item-edit__footer {
  grid-area: footer;
}

.admin-item-edit__header,
.admin-item-edit__footer {
  padding: 22px 24px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

.admin-item-edit__header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: start;
}

.admin-item-edit__footer {
  border-bottom: none;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.admin-item-edit__eyebrow {
  margin: 0 0 8px;
  color: #60a5fa;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.admin-item-edit__header h2 {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 32px;
  line-height: 1;
  letter-spacing: -0.04em;
}

.admin-item-edit__header span,
.admin-item-edit__hint {
  color: #94a3b8;
  line-height: 1.7;
}

.admin-item-edit__close {
  width: 42px;
  height: 42px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.72);
  color: #ffffff;
  font-size: 18px;
  cursor: pointer;
}

.admin-item-edit__error {
  margin: 16px 24px 0;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(239, 68, 68, 0.12);
  color: #fca5a5;
  font-weight: 700;
}

.admin-item-edit__content {
  min-height: 0;
  overflow-y: auto;
  padding: 24px;
  display: grid;
  gap: 18px;
}

.admin-item-edit__section {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.48);
  border: 1px solid rgba(148, 163, 184, 0.08);
}

.admin-item-edit__section h3 {
  margin: 0;
  color: #f8fafc;
  font-size: 20px;
}

.admin-item-edit__hint {
  margin: 0;
  font-size: 13px;
}

.admin-item-edit__hint strong {
  color: #cbd5e1;
}

.admin-item-edit__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.admin-item-edit__field {
  display: grid;
  gap: 8px;
}

.admin-item-edit__field span {
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 800;
}

.admin-item-edit__field input,
.admin-item-edit__field select,
.admin-item-edit__field textarea {
  width: 100%;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  outline: none;
}

.admin-item-edit__field input,
.admin-item-edit__field select {
  min-height: 44px;
}

.admin-item-edit__field textarea {
  min-height: 110px;
  padding-top: 12px;
  resize: vertical;
  line-height: 1.6;
}

.admin-item-edit__field input:focus,
.admin-item-edit__field select:focus,
.admin-item-edit__field textarea:focus {
  border-color: rgba(96, 165, 250, 0.55);
}

.admin-item-edit__button {
  min-height: 42px;
  padding: 0 16px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  color: #ffffff;
  font-weight: 900;
  cursor: pointer;
}

.admin-item-edit__button--ghost {
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.72);
}

.admin-item-edit__button:disabled,
.admin-item-edit__close:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 760px) {
  .admin-item-edit {
    padding: 12px;
  }

  .admin-item-edit__dialog {
    max-height: 94vh;
  }

  .admin-item-edit__header,
  .admin-item-edit__footer {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-item-edit__grid {
    grid-template-columns: 1fr;
  }

  .admin-item-edit__button {
    width: 100%;
  }

  .admin-item-edit__content,
  .admin-item-edit__header,
  .admin-item-edit__footer {
    padding: 16px;
  }
}
</style>