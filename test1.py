import ctypes
import sys


print(ctypes.windll.shell32.IsUserAnAdmin())

print(sys.executable)