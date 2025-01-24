from network.test.test_common import TestORCA
from rest_framework import status

class TestIpPolling(TestORCA):
    
    def test_ip_range(self):
        ip_range = "127.0.0.0 - 127.0.0.10"
        
        # adding ip range
        response = self.put_req("ip_range", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # validate ip range added
        response = self.get_req("ip_range")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ip_range, [i["range"] for i in response.data])
        
        # delete ip range
        response = self.del_req("ip_range", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # validate ip range deleted
        response = self.get_req("ip_range")
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])
        self.assertNotIn(ip_range, [i["range"] for i in response.data])
        
        
    def test_ip_availability(self):
        ip_range = "127.0.0.0 - 127.0.0.10"
        
        # adding ip range
        response = self.put_req("ip_range", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # validate ip range added
        response = self.get_req("ip_range")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ip_range, [i["range"] for i in response.data])
        
        # validating ip availability
        response = self.get_req("all_ips", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in response.json():
            self.assertIn(ip_range, i["range"])
        
        # delete ip range
        response = self.del_req("ip_range", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # validate ip range deleted
        response = self.get_req("ip_range")
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])
        
        # validating ip availability
        response = self.get_req("all_ips", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT) 
        
    def test_overlap_ip_range(self):
        ip_range1 = "127.0.0.0 - 127.0.0.10"
        ip_range2 = "127.0.0.5 - 127.0.0.15"
        
        # adding ip range
        response = self.put_req("ip_range", {"range": ip_range1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.put_req("ip_range", {"range": ip_range2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # validate ip range added
        response = self.get_req("ip_range")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ip_range1, [i["range"] for i in response.data])
        self.assertIn(ip_range2, [i["range"] for i in response.data])
        
        # validating ip availability
        response = self.get_req("all_ips", {"range": ip_range1})
        range1_ips = [i["ip"] for i in response.json()]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in response.json():
            self.assertIn(ip_range1, i["range"])
        
        response = self.get_req("all_ips", {"range": ip_range2})
        range2_ips = [i["ip"] for i in response.json()]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in response.json():
            self.assertIn(ip_range2, i["range"])
    
        # validating ip a
        response = self.get_req("all_ips")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(set(range1_ips + range2_ips)), len([i["ip"] for i in response.json()]))
        
        # delete ip range 1
        response = self.del_req("ip_range", {"range": ip_range1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # validate ip range deleted
        response = self.get_req("ip_range")
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])
        self.assertNotIn(ip_range1, [i["range"] for i in response.data])
        
        # validating only range 1 is deleted
        response = self.get_req("all_ips", {"range": ip_range1})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT) 
        
        # validating no ips of range 2 are not deleted
        response = self.get_req("all_ips", {"range": ip_range2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(range2_ips), len([i["ip"] for i in response.json()]))
        for i in response.json():
            self.assertIn(ip_range2, i["range"])
        
        
        
        
    def test_ip_usage_in_interface(self):
        ip_range = "10.10.10.0 - 10.10.10.10"
        
        # adding ip range
        response = self.put_req("ip_range", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # validating ip availability
        response = self.get_req("all_ips", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in response.json():
            self.assertIn(ip_range, i["range"])
            
        # adding ip to interface
        device_ip = list(self.device_ips.keys())[0]
        ether_name = self.device_ips[device_ip]["interfaces"][0]
        ip = "10.10.10.4"
        prefix_len = 24
        response = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "name": ether_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        request_body = {
            "mgt_ip": device_ip,
            "name": ether_name,
            "ip_address": f"{ip}/{prefix_len}",
        }
        self.assert_with_timeout_retry(
            lambda path, data: self.put_req(path, data),
            "device_interface_list",
            request_body,
            status=status.HTTP_200_OK,
        )

        # verifying the ip_address value
        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        if isinstance(response_body, list):
            self.assertTrue(any([i["ip_address"] == ip for i in response_body]))
        else:
            self.assertEqual(response_body["ip_address"], ip)
        
        # validating ip availability
        response = self.get_req("available_ips")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(ip, response.json())
        
        response = self.del_req("subinterface", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verifying the ip_address deletion
        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # validating ip availability
        response = self.get_req("available_ips")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ip, response.json())
            
        # delete ip range
        response = self.del_req("ip_range", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # validate ip range deleted
        response = self.get_req("ip_range")
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])
        
        # validating ip availability
        response = self.get_req("all_ips", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    
    def test_ip_usage_in_port_channel(self):
        ip_range = "10.10.10.0 - 10.10.10.10"
        
        # adding ip range
        response = self.put_req("ip_range", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # validating ip availability
        response = self.get_req("all_ips", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in response.json():
            self.assertIn(ip_range, i["range"])
            
        # adding ip to port channel
        device_ip = list(self.device_ips.keys())[0]
        self.remove_mclag(device_ip)
        
        ip = "10.10.10.4"
        prefix_len = 24
        port_channel = "PortChannel103"
        # Test ip_address attribute on port channel creation
        request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel,
            "mtu": 9100,
            "admin_status": "up",
            "ip_address": f"{ip}/{prefix_len}",
        }

        # cleaning up port channel if it exists
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel})

        # adding port channel
        self.perform_add_port_chnl([request_body])
        response = self.get_req(
            "device_port_chnl", {"mgt_ip": device_ip, "lag_name": port_channel}
        )
        self.assertEqual(response.json()["ip_address"], f"{ip}/{prefix_len}")
        
        # validating ip availability
        response = self.get_req("available_ips")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(ip, response.json())
        
        # deleting port channel
        del_resp = self.del_req(
            "port_channel_ip_remove",
            {"mgt_ip": device_ip, "lag_name": port_channel, "ip_address": f"{ip}/{prefix_len}"},
        )
        self.assertEqual(del_resp.status_code, status.HTTP_200_OK)
        response = self.get_req(
            "device_port_chnl", {"mgt_ip": device_ip, "lag_name": port_channel}
        )
        self.assertEqual(response.json()["ip_address"], None)
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel})
        
        # validating ip availability
        response = self.get_req("available_ips")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ip, response.json())
        
        # delete ip range
        response = self.del_req("ip_range", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # validate ip range deleted
        response = self.get_req("ip_range")
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])
        
        # validating ip availability
        response = self.get_req("all_ips", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        
    def test_ip_usage_in_vlan(self):
        ip_range = "10.10.10.0 - 10.10.10.10"
        
        # adding ip range
        response = self.put_req("ip_range", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # validating ip range added
        response = self.get_req("ip_range")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ip_range, [i["range"] for i in response.data])
        
        # validating ip availability
        response = self.get_req("all_ips", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in response.json():
            self.assertIn(ip_range, i["range"])
            
            
        # adding ip to vlan
        
        device_ip = list(self.device_ips.keys())[0]
        vlan_name = "Vlan4"
        ip = "10.10.10.4"
        prefix_len = 24

        # create Vlan
        req_payload = {
            "mgt_ip": device_ip,
            "name": vlan_name,
            "vlanid": 4,
            "mtu": 9000,
            "enabled": False,
            "description": "Test_Vlan1",
            "ip_address": f"{ip}/{prefix_len}",
            "autostate": "enable",
        }
        self.create_vlan(req_payload)
        
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": req_payload["name"]}
        )
        self.assertEqual(response.json()["name"], req_payload["name"])
        self.assertEqual(response.json()["vlanid"], req_payload["vlanid"])
        self.assertEqual(response.json()["mtu"], req_payload["mtu"])
        self.assertEqual(response.json()["enabled"], req_payload["enabled"])
        self.assertEqual(response.json()["description"], req_payload["description"])
        self.assertEqual(response.json()["autostate"], req_payload["autostate"])
        self.assertEqual(
            response.json()["ip_address"], req_payload["ip_address"]
        )
        
        # validating ip availability
        response = self.get_req("available_ips")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(ip, response.json())
        
        # remove ip_address
        req_payload_remove_ip = {
            "mgt_ip": device_ip,
            "name": vlan_name,
        }
        response = self.del_req("vlan_ip_remove", req_payload_remove_ip)

        # after deletion check if ip is deleted and other params are unchanged
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": req_payload["name"]}
        )
        self.assertEqual(response.json()["name"], req_payload["name"])
        self.assertEqual(response.json()["vlanid"], req_payload["vlanid"])
        self.assertEqual(response.json()["mtu"], req_payload["mtu"])
        self.assertEqual(response.json()["enabled"], req_payload["enabled"])
        self.assertEqual(response.json()["description"], req_payload["description"])
        self.assertEqual(response.json()["autostate"], req_payload["autostate"])
        self.assertFalse(response.json().get("ip_address"))

        #clean up
        self.delete_vlan(req_payload)
        
        # validating ip availability
        response = self.get_req("available_ips")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ip, response.json())
        
        # delete ip range
        response = self.del_req("ip_range", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # validate ip range deleted
        response = self.get_req("ip_range")
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])
        
        # validating ip availability
        response = self.get_req("all_ips", {"range": ip_range})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)