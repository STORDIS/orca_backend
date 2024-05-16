"""
This module contains tests for the Interface API.
"""
from network.test.test_vlan import TestVlan



class TestCreateSampleConfig(TestVlan):
    def test_create_sample_config(self):
        self.create_sample_vlan_and_member_config(self.get_req_body())