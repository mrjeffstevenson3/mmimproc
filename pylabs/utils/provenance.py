"""
The ProvenanceWrapper class can stand in as niprov.ProvenanceContext;
    - this module attempts to import niprov,
    - if it cannot be imported, 
    - or niprov has been turned off using the `useNiprov` flag,
the ProvenanceWrapper will not use niprov and instead just print
its calls and forward record() calls to subprocess.

"""
import subprocess
try:
    import niprov
except:
    niprov = None

useNiprov = False  ## Change this to False to turn off niprov usage


class ProvenanceWrapper(object):

    def __init__(self):
        if niprov and useNiprov:
            self.context = niprov.ProvenanceContext()
        else:
            self.context = None

    def __getattr__(self, name):
        if self.context:
            return getattr(self.context, name)
        else:
            def dummymethod(*args, **kwargs):
                msg = 'Niprov method [{}] called but niprov switched off.'
                print(msg.format(name))
                if name == 'record':
                    if isinstance(args[0], (list, tuple)):
                        subprocess.check_call(args[0])
                    else:
                        m = 'Cannot run python with ProvenanceWrapper.record()'
                        raise ValueError(m)
                if name == 'get':
                    raise TypeError('Cannot use get() without niprov.')
            return dummymethod
