from typing import TypedDict


"""
this class represents a generic dictionary
returned by the Google Drive API. since (in
this project) all I care about is the id, name 
and type of the file, these options will be 
enough.
"""

class DriveFile(TypedDict):
    id: str
    name: str
    mimeType: str
