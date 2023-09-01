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
    f"{version}/Dank-Memer-Grinder-v{version}-Linux-amd64.zip",
    stream=True,
)

with zipfile.ZipFile(io.BytesIO(r.content)) as z:
    with open("Dank Memer Grinder", "wb") as f:
        f.write(z.read("Dank Memer Grinder"))
os.chmod("Dank Memer Grinder", os.stat("Dank Memer Grinder").st_mode | 0o111)

subprocess.Popen(f"{os.getcwd()}/Dank Memer Grinder")
sys.exit(os._exit(0))
