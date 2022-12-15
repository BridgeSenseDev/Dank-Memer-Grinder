import platform
import subprocess
import sys
import zipfile
import io
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
    (
        "https://github.com/BridgeSenseDev/Dank-Memer-Grinder/releases/download/v"
        f"{version}/Dank-Memer-Grinder-v{version}-Linux-arm64.zip"
    ),
    stream=True,
)
with zipfile.ZipFile(io.BytesIO(r.content)) as z:
    with open("Dank Memer Grinder", "wb") as f:
        f.write(z.read("Dank Memer Grinder"))
subprocess.Popen("./Dank Memer Grinder")
sys.exit(0)
