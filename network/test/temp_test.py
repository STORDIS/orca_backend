from rest_framework import status

from network.test.test_common import TestORCA

class TestTemp(TestORCA):
    
    device_ip = self.device_ips[0]
    
    def test_interface_new_param(self):
        
        response = self.get_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": self.ether_names[2]},
        )
        print('-----', response)