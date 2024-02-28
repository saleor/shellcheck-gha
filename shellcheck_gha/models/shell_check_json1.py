from pydantic import BaseModel


class ShellCheckReplacementSuggestion(BaseModel):
    line: int
    endLine: int
    precedence: int
    insertionPoint: str
    column: int
    endColumn: int
    replacement: str


class ShellCheckReplacementSuggestionList(BaseModel):
    replacements: list[ShellCheckReplacementSuggestion]


class ShellCheckComment(BaseModel):
    file: str
    line: int
    endLine: int
    column: int
    endColumn: int
    level: str
    code: int
    message: str
    fix: ShellCheckReplacementSuggestionList | None


class ShellCheckOutput(BaseModel):
    comments: list[ShellCheckComment]
