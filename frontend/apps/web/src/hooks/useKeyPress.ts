import { useEffect, useState } from 'react'

interface KeyPressOptions {
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
  meta?: boolean
}

export function useKeyPress(targetKey: string, options: KeyPressOptions = {}): boolean {
  const [keyPressed, setKeyPressed] = useState(false)

  useEffect(() => {
    const downHandler = (event: KeyboardEvent) => {
      const { ctrl, shift, alt, meta } = options

      const ctrlMatch = ctrl === undefined || event.ctrlKey === ctrl
      const shiftMatch = shift === undefined || event.shiftKey === shift
      const altMatch = alt === undefined || event.altKey === alt
      const metaMatch = meta === undefined || event.metaKey === meta

      if (
        event.key.toLowerCase() === targetKey.toLowerCase() &&
        ctrlMatch &&
        shiftMatch &&
        altMatch &&
        metaMatch
      ) {
        setKeyPressed(true)
      }
    }

    const upHandler = (event: KeyboardEvent) => {
      if (event.key.toLowerCase() === targetKey.toLowerCase()) {
        setKeyPressed(false)
      }
    }

    if (typeof window === 'undefined') {
      return
    }

    window.addEventListener('keydown', downHandler)
    window.addEventListener('keyup', upHandler)

    return () => {
      window.removeEventListener('keydown', downHandler)
      window.removeEventListener('keyup', upHandler)
    }
  }, [targetKey, options])

  return keyPressed
}

export function useKeyboardShortcut(
  key: string,
  callback: () => void,
  options: KeyPressOptions = {}
): void {
  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      const { ctrl, shift, alt, meta } = options

      const ctrlMatch = ctrl === undefined || event.ctrlKey === ctrl
      const shiftMatch = shift === undefined || event.shiftKey === shift
      const altMatch = alt === undefined || event.altKey === alt
      const metaMatch = meta === undefined || event.metaKey === meta

      if (
        event.key.toLowerCase() === key.toLowerCase() &&
        ctrlMatch &&
        shiftMatch &&
        altMatch &&
        metaMatch
      ) {
        event.preventDefault()
        callback()
      }
    }

    if (typeof window === 'undefined') {
      return
    }

    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [key, callback, options])
}
