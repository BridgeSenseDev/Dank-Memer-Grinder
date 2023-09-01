import io
import os
import subprocess
import sys
import zipfile

import requests
from halo import Halo

version = requests.get(
    "https://raw.githubusercontent.com/BridgeSenseDev/Dank-Memer-Grinder/main/"
    "resources/version.txt"
).text.partition("\n")[0]

spinner = Halo(
    text=f"Downloading new version {version} from github...",
    spinner={
        "interval": 100,
        "frames": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    },
)
spinner.start()

r = requests.get(
    "https://github.com/BridgeSenseDev/Dank-Memer-Grinder/releases/download/v"
    f"{version}/Dank-Memer-Grinder-v{version}-Windows-amd64.zip",
    stream=True,
)

with zipfile.ZipFile(io.BytesIO(r.content)) as z:
    with open(f"Dank Memer Grinder.exe", "wb") as f:
        f.write(z.read("Dank Memer Grinder.exe"))

subprocess.Popen(f"Dank Memer Grinder.exe")
sys.exit(os._exit(0))
