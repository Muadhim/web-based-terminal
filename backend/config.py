import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", 8000))
SHELL = os.getenv("SHELL", "/bin/bash")
