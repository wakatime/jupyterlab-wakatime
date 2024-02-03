import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application'
import { INotebookTracker } from '@jupyterlab/notebook'
import { IEditorTracker } from '@jupyterlab/fileeditor'
import { ISettingRegistry } from '@jupyterlab/settingregistry'
import { IStatusBar } from '@jupyterlab/statusbar'

import { createHeart, pollStatus } from './watch'
import { StatusModel, WakaTimeStatus } from './status'

/**
 * Initialization data for the jupyterlab-wakatime extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-wakatime:plugin',
  description: 'A JupyterLab WakaTime extension.',
  autoStart: true,
  requires: [INotebookTracker, IEditorTracker],
  optional: [ISettingRegistry, IStatusBar],
  activate: (
    app: JupyterFrontEnd,
    notebooks: INotebookTracker,
    editors: IEditorTracker,
    settingRegistry: ISettingRegistry | null,
    statusBar: IStatusBar | null,
  ) => {
    console.log('JupyterLab extension jupyterlab-wakatime is activated!')
    const statusModel = new StatusModel()
    const beatHeart = createHeart(statusModel)

    notebooks.widgetAdded.connect((_, notebook) => {
      const filepath = notebook.sessionContext.path
      notebook.content.model?.contentChanged.connect(() => {
        beatHeart(filepath, 'change')
      })
      notebook.content.model?.stateChanged.connect((_, change) => {
        if (change.name === 'dirty' && change.oldValue) {
          beatHeart(filepath, 'write')
        }
      })
    })
    notebooks.currentChanged.connect((_, notebook) => {
      if (notebook === null) {
        return
      }
      beatHeart(notebook.sessionContext.path, 'switch')
    })
    editors.widgetAdded.connect((_, editor) => {
      editor.context.fileChanged.connect(ctx => {
        beatHeart(ctx.path, 'change')
      })
      editor.context.saveState.connect((ctx, state) => {
        if (state === 'completed') {
          beatHeart(ctx.path, 'write')
        }
      })
    })
    editors.currentChanged.connect((_, editor) => {
      if (editor !== null) {
        beatHeart(editor.context.path, 'switch')
      }
    })
    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          if (settings.get('status').composite && statusBar) {
            const wakatimeStatus = new WakaTimeStatus(statusModel)
            statusBar.registerStatusItem('wakatime-status', {
              item: wakatimeStatus,
              align: 'right',
            })
            pollStatus(statusModel)
          }
        })
        .catch(reason => {
          console.error(
            'Failed to load settings for jupyterlab-wakatime.',
            reason
          )
        })
    }
  }
}

export default plugin
