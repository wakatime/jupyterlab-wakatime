import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application'
import { INotebookTracker } from '@jupyterlab/notebook'

import { beatHeart } from './watch'

/**
 * Initialization data for the waka-jlab extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'waka-jlab:plugin',
  description: 'A JupyterLab WakaTime extension.',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, notebooks: INotebookTracker) => {
    console.log('JupyterLab extension waka-jlab is activated!')
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
  }
}

export default plugin
