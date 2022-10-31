
from gameoflife.config import Config

def testConfig():
    conf = Config()
    assert conf.cfg
    assert conf.get('screen.width') == 1200
    assert conf.get('screen.height') == 800
    assert conf.get('cell.width') == 10
    assert conf.get('cell.height') == 10
    assert conf.get('fps') == 30
    assert conf.get('fps', default=60) == 30
    assert conf.get('doesntexist', default=True) == True