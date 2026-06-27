from dataclasses import dataclass

@dataclass(frozen=True)
class SrcFile:
    filepath: str
    code: str

    def __post_init__(self):
        if self.filepath == "":
            raise ValueError("file name is blank")
        if self.code == "":
            raise ValueError(f"code is blank: {self.filepath}")

