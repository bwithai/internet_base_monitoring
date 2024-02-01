import ctypes
import subprocess


def run_as_admin(command):
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            subprocess.run(command, shell=True)
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "python", " ".join(command), None, 1)
    except Exception as e:
        print("Error:", e)


# Enable the OpenSSH server with elevated privileges
run_as_admin('powershell Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0')

# Start the OpenSSH server with elevated privileges
run_as_admin('powershell Start-Service sshd')
