- Indent 4 spaces
- When function has up to 2 arguments, let them on one line if they are not too long
-> When two arguments are too long, format them like this:
```
def function_name(
    argument_too_long1: str, argument_too_long2: int
) -> str | None:
    pass
```
- When function has 3 or more arguments, put each on new line **ALWAYS** like this:
```
def function_name(
    argument1: str,
    argument2: int,
    argument3: bool
) -> str | None:
    pass
```
- When importing 4 or more modules from **library**, put each import on new line **ALWAYS** like this:
```
from module import (
    function_1,
    function_2,
    function_3,
    function_4
)
```
- But when importing from project files, then you have to do this formatting for 3 or more imports:
```
from backend.app.config.settings import (
    get_settings,
    get_settings_from_env,
    Settings
)
```
- REMEMBER that all depends. You can import 4 files that are very short, then you can leave them on one line or you can import 2 files that are long and put them on new line.
- When making edits or patches, **NEVER** change formatting, indentation or new lines unless asked

