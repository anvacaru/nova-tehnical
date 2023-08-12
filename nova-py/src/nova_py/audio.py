import logging
import platform
import subprocess
import time
from subprocess import Popen
from typing import Final

_LOGGER: Final = logging.getLogger(__name__)


def start_audacity() -> Popen[bytes]:
    """
    Start Audacity with ModScriptPipe enabled.
    """

    # Detect the operating system
    os_name = platform.system()
    _LOGGER.debug(f'Operating system name: {os_name}')
    # Depending on the OS, the command to run Audacity may differ.
    if os_name == 'Windows':
        cmd = ['audacity.exe']
    elif os_name == 'Darwin':  # macOS
        # On macOS, you might need to use the full path to the Audacity app, or if it's in Applications, you can use 'open'.
        cmd = ['open', '-a', 'Audacity']
    elif os_name == 'Linux':
        cmd = ['audacity']
    else:
        raise EnvironmentError(f'Unsupported operating system: {os_name}')

    # Start Audacity with the ModScriptPipe module
    _LOGGER.info('Launching Audacity process..')
    pid = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = pid.communicate()
    _LOGGER.debug(f'STDOUT: {out.decode()}')
    _LOGGER.debug(f'STDERR: {err.decode()}')

    _LOGGER.debug(f'Audacity process started successfully with pid: {pid.returncode}')
    # Optional: Give Audacity some time to start and set up the ModScriptPipe.
    time.sleep(3)

    return pid
