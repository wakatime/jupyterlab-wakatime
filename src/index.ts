import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application'
import { INotebookTracker } from '@jupyterlab/notebook'
import { IEditorTracker } from '@jupyterlab/fileeditor'

import { beatHeart } from './watch'

/**
 * Initialization data for the jupyterlab-wakatime extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-wakatime:plugin',
  description: 'A JupyterLab WakaTime extension.',
  autoStart: true,
  requires: [INotebookTracker, IEditorTracker],
  activate: (
    app: JupyterFrontEnd,
    notebooks: INotebookTracker,
    editors: IEditorTracker
  ) => {
    console.log('JupyterLab extension jupyterlab-wakatime is activated!')
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
  }
}

export default plugin
