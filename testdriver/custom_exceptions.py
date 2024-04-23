class TestDriverCrashDetected(Exception):
    def __init__(self, error_message, code=None):
        self.message = error_message
        self.code = code