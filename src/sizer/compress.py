import os
from questionary import confirm
from rich.console import Console
from subprocess import run

from rich.progress import Progress

console = Console()

MAX_DPI     = 300
MIN_DPI     = 80
DPI_STEPS   = 50

def compress(
    path: str,
    threshold: int
) -> str:
    """
    compress a local file using `compress_fixed` repeatidly
    until below desired threshold
    """
    
    dest = path.removesuffix(".pdf") + "_compressed.pdf"
    
    dpi = MAX_DPI
    best = path
    i = 0

    while True:
        if os.path.getsize(best) < threshold:
            return best
        if dpi <= MIN_DPI:
            console.print(f"[bold yellow]couldn't compress {path} due to dpi limit (current = {dpi})[/]")
            return best
        
        best = compress_fixed(path, f"{dpi}", dest)
        dpi = dpi - DPI_STEPS
        i = i + 1

def compress_fixed(
    path: str,
    dpi: str,

    dest: str | None = None
) -> str:
    """
    compresses a local file using ghostscript and saves 
    it `{file_base}_compressed.pdf` or the `to` argument.

    returns the path of the compressed file
    """

    if not path.endswith(".pdf"):
        raise Exception("cannot compress a non-pdf file")

    dest = dest or path.removesuffix(".pdf") + "_compressed.pdf"

    run([ "gs",
        "-sDEVICE=pdfwrite", "-dCompatabilityLevel=1.4", "-dPDFSETTINGS=/prepress",
         "-dNOPAUSE", "-dQUIET", "-dBATCH",
         f"-sOutputFile={dest}",
         "-dDownsampleColorImages=true", "-dDownsampleGrayImages=true", "-dDownsampleMonoImages=true",
         f"-dColorImageResolution={dpi}", f"-dGrayImageResolution={dpi}", f"-dMonoImageResolution={dpi}",
        path
    ], check=True)

    return dest

def compress_all (
    files: list[str],
    threshold: int
) -> list[str]:
    """
    compresses all given file paths.

    returns the paths of all compressed files.
    """

    if not confirm(f"compress {len(files)} local files").ask():
        print("alrighty then")
        return []

    paths = []
    with Progress() as progress:
        task = progress.add_task("compressing files", total=len(files))

        for file in files:
            progress.update(task, description=f"compressing {file}")
            paths.append(compress(file, threshold))

            progress.update(task, advance=1)

        progress.update(task, description="compression complete")

    return paths
