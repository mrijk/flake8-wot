# flake8-wot
Flake8 plugin

This plugin warns if you are still importing List, Dict or Tuple (and others) from typing instead of using list, dict,
tuple.

See https://www.python.org/dev/peps/pep-0585/ for more information.

# Example

Running flake on a file test_wot.py with contents:

```python
from typing import List
```

will generate:

```
test_wot.py:1:1: WOT001 don't import type List
```

WOT is an abbreviation of 'Warn about Old school Types'

