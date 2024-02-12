import React from 'react'
import { VDomModel, VDomRenderer } from '@jupyterlab/ui-components'
import { LabIcon } from '@jupyterlab/ui-components'
import { GroupItem, TextItem } from '@jupyterlab/statusbar'

import wakatimeSVG from '../style/icons/wakatime.svg'

export const wakatimeIcon = new LabIcon({
  name: 'jupyterlab-wakatime:wakatime',
  svgstr: wakatimeSVG
})

export class StatusModel extends VDomModel {
  private _time: string
  private _error: number

  constructor() {
    super()
    this._time = 'WakaTime'
    this._error = 200
  }

  get time() {
    return this._time
  }

  get error() {
    return this._error
  }

  get errorMsg() {
    switch (this._error) {
      // extension-defined error codes
      case 0:
        return 'WakaTime is working'
      case 200:
        return 'WakaTime is initializing'
      case 127:
        return 'wakatime-cli not found'
      case 400:
        return 'Plugin error'
      // wakatime-cli error codes
      case 112:
        return 'Rate limited'
      case 102:
        return 'API or network error'
      case 104:
        return 'Invalid API key'
      case 103:
        return 'Config file parse error'
      case 110:
        return 'Config file read error'
      case 111:
        return 'Config file write error'
      default:
        return 'Unknown error'
    }
  }

  set time(time: string) {
    if (time) {
      this._time = time
      this.stateChanged.emit()
    }
  }

  set error(error: number) {
    this._error = error
    this.stateChanged.emit()
  }
}

export class WakaTimeStatus extends VDomRenderer<StatusModel> {
  constructor(model: StatusModel) {
    super(model)
    this.addClass('jp-wakatime-status')
  }

  render() {
    return (
      <GroupItem
        spacing={4}
        title={this.model.errorMsg}
        data-error={this.model.error || undefined}
      >
        <wakatimeIcon.react top="2px" left="1px" stylesheet={'statusBar'} />
        <TextItem source={this.model.time} />
      </GroupItem>
    )
  }
}
