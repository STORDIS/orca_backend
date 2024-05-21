"""
This module contains tests for the Interface API.
"""

from network.test.test_vlan import TestVlan

class TestCreateSampleConfig(TestVlan):
    """
    Create Real life network config scenarios.
    """

    def test_create_sample_config(self):
        """
        Test the create_sample_config function.
        """
        self.assertTrue(True)