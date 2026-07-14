export function createDashboardPoller({
  load,
  onData,
  onError,
  onStart,
  onSettled,
  intervalMs = 30000,
  setIntervalImpl = setInterval,
  clearIntervalImpl = clearInterval,
}) {
  let active = true
  let inFlight = false
  const controller = new AbortController()

  const refresh = async () => {
    if (!active || inFlight) {
      return
    }

    inFlight = true
    onStart?.()
    try {
      const data = await load(controller.signal)
      if (active) {
        onData(data)
      }
    } catch (error) {
      if (active && error?.name !== 'AbortError') {
        onError(error)
      }
    } finally {
      inFlight = false
      if (active) {
        onSettled?.()
      }
    }
  }

  const intervalId = setIntervalImpl(() => void refresh(), intervalMs)
  void refresh()

  return {
    refresh,
    stop() {
      if (!active) {
        return
      }
      active = false
      controller.abort()
      clearIntervalImpl(intervalId)
    },
  }
}
