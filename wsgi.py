# -*- coding:utf-8 -*-
__author__ = 'ery'

import sys
activate_this = "/".join(sys.executable.split("/")[:-1]) + "/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

import os
from gevent.monkey import patch_all
patch_all()

path = os.path.join(os.path.dirname(__file__), os.pardir)
if path not in sys.path:
    sys.path.append(path)

from manage import app
application = app

if __name__ == "__main__":
    application.run()