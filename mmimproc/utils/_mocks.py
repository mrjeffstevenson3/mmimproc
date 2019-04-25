import fnmatch

class MockShell(object):

    def __init__(self):
        self.calls = []

    def run(self, cmd):
        self.calls.append(cmd)

    def assert_ran_command_matching(self, needle):
        matchingCalls = fnmatch.filter(self.calls, needle)
        if not matchingCalls:
            raise AssertionError(
                'No shell calls matching ['+needle+']:\n'+str(self.calls))
