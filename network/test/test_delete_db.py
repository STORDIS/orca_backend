from rest_framework import status

from network.test.test_common import TestORCA


class TestDelete(TestORCA):
    
    def test_delete_device(self):
        
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
        }
                
        ## get discover device
        response=self.get_req("device")
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        
        ## get interfaces list
        response=self.get_req("device_interface_list", {"mgt_ip": device_ip})
        self.assertTrue(response.status_code == status.HTTP_200_OK or response.status_code == status.HTTP_204_NO_CONTENT)
        
        ## get vlan list
        response=self.get_req(
            "vlan_config", {"mgt_ip": device_ip}
        )
        self.assertTrue(response.status_code == status.HTTP_200_OK or response.status_code == status.HTTP_204_NO_CONTENT)
        
        ## get port channel list
        response=self.get_req(
            "device_port_chnl", {"mgt_ip": device_ip}
        )
        self.assertTrue(response.status_code == status.HTTP_200_OK or response.status_code == status.HTTP_204_NO_CONTENT)
        
        ## get port group list
        response=self.get_req(
            "port_groups", {"mgt_ip": device_ip}
        )
        self.assertTrue(response.status_code == status.HTTP_200_OK or response.status_code == status.HTTP_204_NO_CONTENT)
            
        # delete the ip and its related connection from db
        response=self.del_req("del_db", request_body)
        self.assertTrue(response.status_code ==  status.HTTP_200_OK or response.status_code == status.HTTP_204_NO_CONTENT) 
        
        # get discover device
        response=self.get_req("device")
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

        ## get interface list
        response=self.get_req("device_interface_list", {"mgt_ip": device_ip})
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
        
        ## get vlan list
        response=self.get_req(
            "vlan_config", {"mgt_ip": device_ip}
        )
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
        
        ## get  port channel list
        response=self.get_req(
            "device_port_chnl", {"mgt_ip": device_ip}
        )
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
        
        ## get port group list
        response=self.get_req(
            "port_groups", {"mgt_ip": device_ip}
        )
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
        

        

