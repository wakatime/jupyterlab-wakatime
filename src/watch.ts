import { requestAPI } from './handler'
import type { StatusModel } from './status'

// let heartHandle: ReturnType<typeof setTimeout> | null = null
let lastBeat = Date.now()
const wakaInterval = 120 * 1000

export type BeatData = {
  filepath: string
  timestamp: number
  iswrite: boolean
  debug: boolean
}

export class Heart {
  statusModel: StatusModel
  debug: boolean

  constructor(statusModel: StatusModel, debug: boolean = false) {
    this.statusModel = statusModel
    this.debug = debug
  }
  async beat(
    filepath: string,
    type: 'switch' | 'change' | 'write'
  ) {
    console.log(type, filepath)
    const now = Date.now()
    if (type === 'change' && now - lastBeat < wakaInterval) {
      return
    }
    const data: BeatData = {
      filepath: filepath,
      timestamp: now / 1e3,
      iswrite: type === 'write',
      debug: this.debug,
    }
    lastBeat = now
    const { code } = await requestAPI<{ code: number }>('heartbeat', {
      body: JSON.stringify(data),
      method: 'POST'
    })
    this.statusModel.error = code
  }
}

const immediateInterval = (callback: () => void, ms: number) => {
  callback()
  setInterval(callback, ms)
}

export const pollStatus = (model: StatusModel) => {
  immediateInterval(async () => {
    const { time } = await requestAPI<{ time: string, error: number }>('status')
    model.time = time
  }, 6e4)
}
