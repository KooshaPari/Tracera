const CLIENT_ID_ERROR =
  'VITE_WORKOS_CLIENT_ID is required and must be a WorkOS client ID beginning with client_'
const API_HOSTNAME_ERROR =
  'VITE_WORKOS_API_HOSTNAME must be an exact https origin, for example https://auth.example.com'

export function normalizeWorkOsClientId(value) {
  const clientId = value?.trim() || ''
  if (!clientId.startsWith('client_') || /\s/.test(clientId)) {
    throw new Error(CLIENT_ID_ERROR)
  }
  return clientId
}

export function normalizeWorkOsApiHostname(value) {
  const apiHostname = value?.trim() || ''
  if (!apiHostname) {
    return undefined
  }

  try {
    const url = new URL(apiHostname)
    if (url.protocol === 'https:' && url.origin === apiHostname) {
      return apiHostname
    }
  } catch {
    // The stable diagnostic below is more useful than the URL parser error.
  }

  throw new Error(API_HOSTNAME_ERROR)
}

export function resolveAuthConfiguration(clientIdValue, apiHostnameValue) {
  try {
    return {
      clientId: normalizeWorkOsClientId(clientIdValue),
      apiHostname: normalizeWorkOsApiHostname(apiHostnameValue),
      error: null,
    }
  } catch (error) {
    return {
      clientId: '',
      apiHostname: undefined,
      error: error instanceof Error ? error.message : String(error),
    }
  }
}
