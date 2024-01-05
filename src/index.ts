import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { requestAPI } from './handler';

/**
 * Initialization data for the waka-jlab extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'waka-jlab:plugin',
  description: 'A JupyterLab WakaTime extension.',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension waka-jlab is activated!');

    requestAPI<any>('get-example')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The waka_jlab server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
