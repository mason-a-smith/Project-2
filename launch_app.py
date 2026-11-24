"""Launch the final app from a Python Run button and open its browser tab."""
import importlib.util
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser


def command(root, port):
    uv = shutil.which('uv')
    if uv:
        prefix = [uv, 'run', '--locked', '--project', str(root), 'python']
    elif importlib.util.find_spec('streamlit') is not None:
        prefix = [sys.executable]
    else:
        raise RuntimeError('Install uv first, or select the project .venv Python interpreter in VS Code.')
    return prefix + ['-m', 'streamlit', 'run', str(root/'app.py'),
                     '--server.address', '127.0.0.1', '--server.port', str(port),
                     '--server.headless', 'true']


def available_port():
    for port in range(8522, 8543):
        try:
            with socket.socket() as listener:
                listener.bind(('127.0.0.1', port))
            return port
        except OSError:
            continue
    raise RuntimeError('Ports 8522–8542 are busy. Stop an earlier app and retry.')


def open_when_ready(url, finished):
    for _ in range(150):
        if finished.is_set():
            return
        try:
            if urllib.request.urlopen(url+'/_stcore/health', timeout=1).read() == b'ok':
                webbrowser.open(url, new=2)
                return
        except OSError:
            pass
        time.sleep(.2)


def launch():
    root = Path(__file__).resolve().parent
    finished = threading.Event()
    try:
        port = available_port()
        args = command(root, port)
        url = f'http://127.0.0.1:{port}'
        print('Starting Project 2 Final from:', root, flush=True)
        print('The browser will open when ready:', url, flush=True)
        print('Keep this terminal open. Stop the app with Ctrl+C.', flush=True)
        threading.Thread(target=open_when_ready, args=(url, finished), daemon=True).start()
        return subprocess.call(args, cwd=root)
    except KeyboardInterrupt:
        return 0
    except (RuntimeError, OSError) as error:
        print('Unable to start app:', error, file=sys.stderr)
        return 1
    finally:
        finished.set()


if __name__ == '__main__':
    raise SystemExit(launch())
