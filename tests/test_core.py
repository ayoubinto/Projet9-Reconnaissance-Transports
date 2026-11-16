import unittest
import numpy as np
from src.prepare import box_from_line
from src.vision import crop,preprocess,route_candidates,edit_distance

class CoreTests(unittest.TestCase):
    def test_polygon(self): self.assertEqual(box_from_line('0 0.1 0.2 0.9 0.2 0.9 0.8 0.1 0.8',1),(0,.5,.5,.8,.6000000000000001))
    def test_invalid(self):
        for s in ['2 .5 .5 .2 .2','0 nan .5 .2 .2','0 .5 .5 -.1 .2','0 .1 .1 .8 .8','0 .1 .2 .3']:
            with self.assertRaises(ValueError): box_from_line(s,1)
    def test_crop_clipped(self): self.assertEqual(crop(np.zeros((20,30,3),np.uint8),[-5,-5,40,30]).shape,(20,30,3))
    def test_crop_empty(self):
        with self.assertRaises(ValueError): crop(np.zeros((20,30,3),np.uint8),[10,10,9,9])
    def test_image(self):
        out=preprocess(np.zeros((32,32,3),np.uint8));self.assertEqual(out['histogram'].sum(),1024);self.assertEqual(out['edges'].shape,(32,32))
    def test_routes(self): self.assertEqual(route_candidates('Ligne A12 vers 004B CENTRE'),['A12','004B'])
    def test_cer(self): self.assertEqual(edit_distance('123','13'),1)

if __name__=='__main__': unittest.main()
