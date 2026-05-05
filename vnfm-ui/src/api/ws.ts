import { useAuthStore } from '../store/auth'

let ws: WebSocket | null = null

export function connectWebSocket(onMessage: (data: any) => void) {
  const auth = useAuthStore()
  if (!auth.token) {
    console.warn('WebSocket connect skipped: no auth token')
    return
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const url = `${protocol}//${window.location.host}/api/v1/ws/events?token=${encodeURIComponent(auth.token)}`

  ws = new WebSocket(url)

  ws.onopen = () => {
    console.log('WebSocket connected')
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch (e) {
      console.error('WebSocket message parse error', e)
    }
  }

  ws.onclose = (ev) => {
    if (ev.code === 1008) {
      console.warn('WebSocket closed by server: policy violation (auth failed). Will not reconnect.')
      return
    }
    console.log('WebSocket closed, reconnecting in 3s...')
    setTimeout(() => connectWebSocket(onMessage), 3000)
  }

  ws.onerror = (err) => {
    console.error('WebSocket error', err)
  }
}

export function disconnectWebSocket() {
  if (ws) {
    ws.close()
    ws = null
  }
}
