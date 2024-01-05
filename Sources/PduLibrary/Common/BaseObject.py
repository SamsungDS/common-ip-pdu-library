from logging import getLogger

class BaseObject(object):
    def __init__(self):
        super(BaseObject, self).__init__()
        self._Logger = getLogger(type(self).__module__)
