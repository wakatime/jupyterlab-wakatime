import { requestAPI } from './handler'

// let heartHandle: ReturnType<typeof setTimeout> | null = null
let lastBeat = Date.now()
const wakaInterval = 120 * 1000

export type BeatData = {
  filepath: string
  timestamp: number
  iswrite: boolean
}

export const beatHeart = (
  filepath: string,
  type: 'switch' | 'change' | 'write'
) => {
  console.log(type, filepath)
  const now = Date.now()
  if (type === 'change' && now - lastBeat < wakaInterval) {
    return
  }
  const data: BeatData = {
    filepath: filepath,
    timestamp: now / 1e3,
    iswrite: type === 'write'
  }
  lastBeat = now
  requestAPI<any>('heartbeat', {
    body: JSON.stringify(data),
    method: 'POST'
  })
}
