export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')

export const TOKEN_STORAGE_KEY = 'mediacompass_access_token'

type UnauthorizedHandler = () => void

let unauthorizedHandler: UnauthorizedHandler | null = null

export type ApiRequestOptions = RequestInit & {
  auth?: boolean
  skipUnauthorizedHandler?: boolean
  notFoundAsNull?: boolean
}

export function setUnauthorizedHandler(handler: UnauthorizedHandler | null) {
  unauthorizedHandler = handler
}

export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY)
}

export function saveAccessToken(token: string) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token)
}

export function removeAccessToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY)
}

export async function parseApiError(response: Response): Promise<string> {
  try {
    const data = (await response.clone().json()) as unknown

    if (typeof data === 'object' && data !== null && 'detail' in data) {
      const detail = (data as { detail?: unknown }).detail

      if (typeof detail === 'string' && detail.trim()) {
        return detail
      }

        if (Array.isArray(detail)) {
          return detail
            .map((item) => {
              const location = Array.isArray(item.loc)
                ? item.loc.join('.')
                : ''

              const message = typeof item.msg === 'string'
                ? item.msg
                : 'Validation error'

              return location ? `${location}: ${message}` : message
            })
          .join(', ')
        }
    }
  } catch {
    // ignore json parse errors
  }

  try {
    const text = await response.clone().text()

    if (text.trim()) {
      return text
    }
  } catch {
    // ignore text parse errors
  }

  return `HTTP ${response.status}`
}

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
    const {
        auth = true,
        skipUnauthorizedHandler = false,
        notFoundAsNull = false,
        headers: providedHeaders,
        ...fetchOptions
    } = options

  const headers = new Headers(providedHeaders)

  const token = getAccessToken()

  if (auth && token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const hasBody = fetchOptions.body !== undefined && fetchOptions.body !== null
  const isFormData =
    typeof FormData !== 'undefined' && fetchOptions.body instanceof FormData
  const isUrlSearchParams =
    typeof URLSearchParams !== 'undefined' &&
    fetchOptions.body instanceof URLSearchParams

  if (
    hasBody &&
    !headers.has('Content-Type') &&
    !isFormData &&
    !isUrlSearchParams
  ) {
    headers.set('Content-Type', 'application/json')
  }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...fetchOptions,
        headers,
    })

    if (response.status === 401 && !skipUnauthorizedHandler) {
        removeAccessToken()
        unauthorizedHandler?.()
    }

    if (response.status === 404 && notFoundAsNull) {
        return null as T
    }

    if (!response.ok) {
        throw new Error(await parseApiError(response))
    }

  if (response.status === 204) {
    return undefined as T
  }

  const text = await response.text()

  if (!text.trim()) {
    return undefined as T
  }

  return JSON.parse(text) as T
}