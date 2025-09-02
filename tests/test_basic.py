import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lims.app import create_app


def test_config():
    app = create_app({'TESTING': True})
    assert app.config['TESTING']
