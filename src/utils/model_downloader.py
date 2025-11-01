import os
from configparser import ConfigParser
from huggingface_hub import hf_hub_download
from huggingface_hub.errors import EntryNotFoundError
import platform

config = ConfigParser(inline_comment_prefixes=";")

def on_jetson():
    if platform.system() == "Linux":
        if platform.machine() == "aarch64":
            uname_info = platform.uname()
            if "tegra" in uname_info.release.lower() or "tegra" in uname_info.version.lower():
                return True
    
    return False

if on_jetson():
    config.read("config_jetson.ini") # Load config for Jetson
else:
    config.read("config.ini") # Load config for non-Jetson
    
model_path = config["SYSTEM"]["model_path"]

if not os.path.exists(model_path):
    model_name = os.path.basename(model_path)
    print(f"Model not found in folder. Attempting to download {model_name} from repository.")
    try:
        hf_hub_download(
            repo_id="ast-n/cv4gt",
            filename=model_name,
            local_dir="models"
        )
    except EntryNotFoundError as e:
        print("ERROR: Model path in config.ini could not be found in folder or in online repository.")
        exit(1)
    except BaseException as e:
        print("ERROR: Model path in config.ini could not be found in folder and download attempt failed.")
        exit(1)
    
    print("Successfully downloaded model from repository.")
    exit(0)
else:
    exit(0)