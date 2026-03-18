import unittest

from opencdc.checker import find_cross_domain_nets
from opencdc.parser import load_netlist


class TestChecker(unittest.TestCase):
    def test_counter_example_has_cross_domain(self):
        nl = load_netlist("examples/counter_netlist.json")
        crossings = find_cross_domain_nets(nl)
        # The example design has a fast-domain counter driving a slow-domain register.
        self.assertTrue(len(crossings) >= 1)


if __name__ == "__main__":
    unittest.main()
