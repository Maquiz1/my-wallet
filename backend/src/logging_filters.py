import re

class NeutralizePath:
    _ctrl = re.compile(r'[\x00-\x1f\x7f]')

    def filter(self, record):
        req = getattr(record, 'request', None)
        if req and getattr(req, 'path', None):
            req.path = self._ctrl.sub('_', req.path)
        return True
