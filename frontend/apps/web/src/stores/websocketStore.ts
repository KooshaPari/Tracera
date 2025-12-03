import { create } from 'zustand'
import { getWebSocketManager, type RealtimeEvent } from '../api/websocket'

interface WebSocketState {
  // Connection state
  isConnected: boolean
  reconnectAttempts: number
  lastEvent: RealtimeEvent | null
  events: RealtimeEvent[]

  // Subscriptions
  activeChannels: Set<string>

  // Actions
  connect: () => void
  disconnect: () => void
  subscribe: (channel: string, callback: (event: RealtimeEvent) => void) => () => void
  addEvent: (event: RealtimeEvent) => void
  clearEvents: () => void
  setConnectionStatus: (isConnected: boolean) => void
}

export const useWebSocketStore = create<WebSocketState>((set, get) => ({
  // Initial state
  isConnected: false,
  reconnectAttempts: 0,
  lastEvent: null,
  events: [],
  activeChannels: new Set(),

  // Actions
  connect: () => {
    const wsManager = getWebSocketManager()
    wsManager.connect()

    // Monitor connection status
    const checkConnection = setInterval(() => {
      set({ isConnected: wsManager.connected })
    }, 1000)

    // Store interval ID for cleanup
    if (typeof globalThis.window !== 'undefined') {
      ;(globalThis.window as any).__wsCheckInterval = checkConnection
    }
  },

  disconnect: () => {
    const wsManager = getWebSocketManager()
    wsManager.disconnect()
    set({ isConnected: false })

    // Clear connection check interval
    if (typeof globalThis.window !== 'undefined' && (globalThis.window as any).__wsCheckInterval) {
      clearInterval((globalThis.window as any).__wsCheckInterval)
    }
  },

  subscribe: (channel, callback) => {
    const wsManager = getWebSocketManager()
    const unsubscribe = wsManager.subscribe(channel, (event) => {
      get().addEvent(event)
      callback(event)
    })

    set((state) => {
      const newChannels = new Set(state.activeChannels)
      newChannels.add(channel)
      return { activeChannels: newChannels }
    })

    // Return enhanced unsubscribe function
    return () => {
      unsubscribe()
      set((state) => {
        const newChannels = new Set(state.activeChannels)
        newChannels.delete(channel)
        return { activeChannels: newChannels }
      })
    }
  },

  addEvent: (event) => {
    set((state) => ({
      lastEvent: event,
      events: [event, ...state.events].slice(0, 100), // Keep last 100 events
    }))
  },

  clearEvents: () => {
    set({ events: [], lastEvent: null })
  },

  setConnectionStatus: (isConnected) => {
    set({ isConnected })
  },
}))
