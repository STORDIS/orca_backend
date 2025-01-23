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
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
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
        print(response.json())
        
        assert False