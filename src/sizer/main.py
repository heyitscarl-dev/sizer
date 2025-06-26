import os
from googleapiclient.discovery import build
from sizer.download import download, download_all
from sizer.compress import compress
import sizer.auth as auth
import dotenv

from sizer.types import DriveFile

def should_download(file: DriveFile, all: list[DriveFile]) -> bool:
    # ugly
    compressed_base = [
        f["name"].removesuffix("_compressed.pdf")
        for f in all 
        if f["name"].endswith("_compressed.pdf")
    ]

    if file["mimeType"] != "application/pdf":
        return False

    name = file["name"].removesuffix(".pdf")
    if name.endswith("_compressed"):
        return False
    if name in compressed_base:
        return False

    return True

def main():
    dotenv.load_dotenv()

    creds = auth.auth()
    service = build("drive", "v3", credentials=creds)
    id = os.getenv("GD_ID") or exit(1)
    
    paths = download_all({
        "id": id,
        "name": "",
        "mimeType": ""
    }, service, filter=should_download)

    path = paths[0]
    compressed = compress(path, 3 * 1024 * 1024)

    print(path)
    print(compressed)

if __name__ == "__main__":
    main()
