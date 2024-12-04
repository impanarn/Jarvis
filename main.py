import os
import eel

from engine.features import *
from v2 import *
# Initialize the 'www' folder
eel.init("www")

playAssistantSound()

# Launch Microsoft Edge in app mode
try:
    os.system('start msedge.exe --app="http://localhost:8000/index.html"')
except Exception as e:
    print(f"Error starting Edge: {e}")

# Start Eel to serve the app
eel.start('index.html', mode=None, host='localhost', port=8000, block=True)
