import subprocess


def method(command):
    result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
    return result.stdout+'\n'+result.stderr