import logging
import os
import platform
import subprocess
import time
from subprocess import Popen
from typing import TYPE_CHECKING, Final, List

if TYPE_CHECKING:
    from typing import Optional, IO

import psutil

_LOGGER: Final = logging.getLogger(__name__)


class AudacityController:
    def __init__(self) -> None:
        os_name = platform.system()
        _LOGGER.info(f'Operating system name: {os_name}')

        self._TOFILE: Optional[IO[str]] = None
        self._FROMFILE: Optional[IO[str]] = None
        self._TONAME: str
        self._FROMNAME: str
        self._EOL: str
        self._CMD: List[str]

        if os_name == 'Windows':
            self._TONAME = '\\\\.\\pipe\\ToSrvPipe'
            self._FROMNAME = '\\\\.\\pipe\\FromSrvPipe'
            self._EOL = '\r\n\0'
            self._CMD = ['audacity.exe']
        elif os_name == 'Darwin':
            self._TONAME = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
            self._FROMNAME = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
            self._EOL = '\n'
            self._CMD = ['open', '-a', 'Audacity']
        elif os_name == 'Linux':
            self._TONAME = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
            self._FROMNAME = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
            self._EOL = '\n'
            self._CMD = ['audacity']
        else:
            raise EnvironmentError(f'Unsupported operating system: {os_name}')

    def _is_process_running(self, process_name: str) -> bool:
        for process in psutil.process_iter():
            try:
                if process_name.lower() in process.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def start_audacity(self) -> Popen[bytes] | None:
        _LOGGER.info('Checking if Audacity is running.')
        if self._is_process_running('audacity'):
            _LOGGER.warning('Audacity is already running.')
            return None

        _LOGGER.info('Launching Audacity process..')
        process = subprocess.Popen(self._CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        _LOGGER.debug(f'STDOUT: {out.decode()}')
        _LOGGER.debug(f'STDERR: {err.decode()}')

        _LOGGER.debug(f'Audacity process started successfully with pid: {process.pid}')
        time.sleep(3)  # Give Audacity some time to start and set up the ModScriptPipe.

        return process

    def quick_test(self) -> None:
        self.do_command('Help: Command=Help')
        self.do_command('Help: Command="GetInfo"')
        self.stop_audacity()

    def open_pipes(self) -> None:
        self.close_pipes()
        if not os.path.exists(self._TONAME):
            _LOGGER.error(f'{self._TONAME} does not exist. Ensure Audacity is running with mod-script-pipe.')
            raise FileNotFoundError(f'{self._TONAME} not found.')

        if not os.path.exists(self._FROMNAME):
            _LOGGER.error(f'{self._FROMNAME} does not exist. Ensure Audacity is running with mod-script-pipe.')
            raise FileNotFoundError(f'{self._FROMNAME} not found.')

        self._TOFILE = open(self._TONAME, 'w')
        self._FROMFILE = open(self._FROMNAME, 'rt')
        _LOGGER.info('Communication pipes with Audacity opened successfully.')

    def _send_command(self, command: str) -> None:
        if not self._TOFILE:
            _LOGGER.error('Communication pipe to Audacity not opened. Call open_pipes() first.')
            raise Exception('Pipe to Audacity not opened.')

        _LOGGER.debug(f'Sending command to Audacity: {command}')
        self._TOFILE.write(command + self._EOL)
        self._TOFILE.flush()

    def _get_response(self) -> str:
        if not self._FROMFILE:
            _LOGGER.error('Communication pipe from Audacity not opened. Call open_pipes() first.')
            raise RuntimeError('Pipe to Audacity not opened.')

        result = ''
        line = ''
        while True:
            result += line
            line = self._FROMFILE.readline()
            if line == self._EOL and len(result) > 0:
                break
        return result.strip()

    def do_command(self, command: str) -> str:
        self._send_command(command)
        response = self._get_response()
        _LOGGER.debug(f'Received response from Audacity: {response}')
        return response

    def stop_audacity(self) -> None:
        self._send_command('Exit')
        self.close_pipes()

    def close_pipes(self) -> None:
        if self._TOFILE is not None:
            self._TOFILE.close()
        if self._FROMFILE is not None:
            self._FROMFILE.close()
        _LOGGER.info('Communication pipes with Audacity closed successfully.')
