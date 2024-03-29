class TestDriverCrashDetected(Exception):
    def __init__(self, error_message):
        self.message = error_message