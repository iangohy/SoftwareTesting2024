# 50.053 Software Testing and Verification

## Development Notes
### Logging
Please use the python logger instead of `print` statements in code. Basic logging code to add to each file:
```
import logging

logger = logging.getLogger(__name__)
```