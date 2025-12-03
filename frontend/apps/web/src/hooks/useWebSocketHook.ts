import { useEffect } from 'react'
import type { RealtimeEvent } from '../api/websocket'
import { useWebSocketStore } from '../stores/websocketStore'

export function useWebSocket() {
  const { isConnected, connect, disconnect, subscribe } = useWebSocketStore()

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return {
    isConnected,
    subscribe,
  }
}

export function useRealtimeSubscription(channel: string, callback: (event: RealtimeEvent) => void) {
  const { subscribe } = useWebSocketStore()

  useEffect(() => {
    const unsubscribe = subscribe(channel, callback)
    return unsubscribe
  }, [channel, callback, subscribe])
}

export function useRealtimeEvents() {
  return useWebSocketStore((state) => state.events)
}

export function useLastRealtimeEvent() {
  return useWebSocketStore((state) => state.lastEvent)
}
