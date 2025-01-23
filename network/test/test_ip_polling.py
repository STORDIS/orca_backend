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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in response.json():
            self.assertIn(ip_range1, i["range"])
        
        response = self.get_req("all_ips", {"range": ip_range2})
        range2_ips = [i["ip"] for i in response.json()]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in response.json():
            self.assertIn(ip_range2, i["range"])
        
        
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
        response = self.get_req("all_ips", {"range": ip_range1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual()
        for i in response.json():
            self.assertIn(ip_range2, i["range"])
        
        
        
    def test_ip_usage(self):
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
        