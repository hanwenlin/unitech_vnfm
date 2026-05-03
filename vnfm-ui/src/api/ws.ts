let ws: WebSocket | null = null

export function connectWebSocket(onMessage: (data: any) => void) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const url = `${protocol}//${window.location.host}/api/v1/ws/events`

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

  ws.onclose = () => {
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
