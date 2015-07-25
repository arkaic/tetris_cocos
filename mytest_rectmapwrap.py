from test_layer_classes import TestRectMapLayerWrapper
from cocos.director import director
director.init(resizable=True)
r = TestRectMapLayerWrapper('tetris.xml')
r.run()