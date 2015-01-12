from unittest import TestCase
from fusedwind.plant_flow.generate_fake_vt import generate_random_wt_layout

__author__ = 'pire'


class TestGenerateFakeVT(TestCase):
    def test_generate_random_WTLayout(self):
        wtl = generate_random_wt_layout(nwt=5)

        # TODO: add some tests
        # [ ] wtl isn't empty
        # [ ] inputs of generate_random_WTLayout(...) are propagated to the WTLayout object

