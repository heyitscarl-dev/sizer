import io
import os
import shutil

from typing import Callable

from questionary import confirm
from rich.progress import Progress, Task, track
from tempfile import mkdtemp
from googleapiclient.http import MediaIoBaseDownload
from rich.console import Console
from sizer.types import DriveFile

console = Console()

def download(
        file: DriveFile, 
        service, 

        path: str | None = None, 
) -> str:
    """
    downloads a file from GD and saves it to
    either a temporary directory, or a specified
    path.

    returns the path of the downloaded file
    """
    
    path = path or mkdtemp()
    dest = os.path.join(path, file["name"])

    request = service.files().get_media(fileId=file["id"])
    with io.FileIO(dest, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    return dest

def list_all(folder: DriveFile, service) -> list[DriveFile]:
    query = f"'{folder["id"]}' in parents and trashed = false"
    files = []
    page_token = None 

    while True:
        response = service.files().list(
            q=query,
            spaces="drive",
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token
        ).execute()

        files.extend(response.get("files", []))
        page_token = response.get("nextPageToken", None)
        
        if page_token is None:
            return files

def download_all (
        folder: DriveFile, 
        service, 

        path: str | None = None, 
        filter: Callable[[DriveFile, list[DriveFile]], bool] | None = None
) -> list[str]:
    """
    downloads all files from a GD folder and 
    saves them to either a temporary directory, or 
    a specified path

    returns the paths of all downloaded files.
    """

    path = path or mkdtemp()

    with console.status("fetching files"):
        files = list_all(folder, service)

    if filter:
        files = [f for f in files if filter(f, files)]

    if len(files) == 0:
        console.print("[bold yellow] 0 [/][dim]files after filter.[/]")
        return []

    if not confirm(f"download {len(files)} files from Google Drive").ask():
        return []

    paths = []
    with Progress() as progress:
        task = progress.add_task("downloading files", total=len(files))

        for file in files:
            progress.update(task, description=f"downloading {file["name"]}")
            paths.append(download(file, service, path))
            progress.update(task, advance=1)

        progress.update(task, description="download complete")

    return paths
