import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application'
import { INotebookTracker } from '@jupyterlab/notebook'
import { IEditorTracker } from '@jupyterlab/fileeditor'
import { ISettingRegistry } from '@jupyterlab/settingregistry'
import { IStatusBar } from '@jupyterlab/statusbar'

import { Heart, pollStatus } from './watch'
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
    const heart = new Heart(statusModel)

    notebooks.widgetAdded.connect((_, notebook) => {
      const filepath = notebook.sessionContext.path
      notebook.content.model?.contentChanged.connect(() => {
        heart.beat(filepath, 'change')
      })
      notebook.content.model?.stateChanged.connect((_, change) => {
        if (change.name === 'dirty' && change.oldValue) {
          heart.beat(filepath, 'write')
        }
      })
    })
    notebooks.currentChanged.connect((_, notebook) => {
      if (notebook !== null) {
        heart.beat(notebook.sessionContext.path, 'switch')
      }
    })
    editors.widgetAdded.connect((_, editor) => {
      editor.context.fileChanged.connect(ctx => {
        heart.beat(ctx.path, 'change')
      })
      editor.context.saveState.connect((ctx, state) => {
        if (state === 'completed') {
          heart.beat(ctx.path, 'write')
        }
      })
    })
    editors.currentChanged.connect((_, editor) => {
      if (editor !== null) {
        heart.beat(editor.context.path, 'switch')
      }
    })
    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          if (settings.get('debug').composite) {
            heart.debug = true
          }
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
