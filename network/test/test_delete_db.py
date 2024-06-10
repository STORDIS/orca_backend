from rest_framework import status

from network.test.test_common import TestORCA


class TestDelete(TestORCA):
    
    def test_delete_device(self):
        
        # Note : ensure that there are atleast 2 devices will be dicovered
        count_before_delete  = 0
        count_after_delete  = 0
        count_after_rediscovery  = 0
        
        # get discover device before deleting
        response=self.get_req("device")
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        
        # storing count in variable for compaction
        for device in response.json():
            count_before_delete += 1

        # delete the one device 
        request_body = {
            "mgt_ip": self.device_ips[0],
        }
        response=self.del_req("del_db", request_body)
        self.assertTrue(response.status_code ==  status.HTTP_200_OK) 
        
        # get discover device after deletion
        response=self.get_req("device")
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        
        # storing count in variable for compaction
        for device in response.json():
            count_after_delete += 1
        
        # checking if the counts are correct 
        # i. e device before deletion must be one grater than device after deletion
        self.assertEqual(count_before_delete, count_after_delete + 1)
        
        # re discovering the deleted device
        request_body = {
            "address": self.device_ips[0],
            "discover_from_config": True
        }
        response=self.put_req("discover",request_body)
        self.assertTrue(response.status_code == status.HTTP_100_CONTINUE)

        # get discover device after  re discovering
        response=self.get_req("device")
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        
        # storing count in variable for compaction
        for device in response.json():
            count_after_rediscovery += 1
            
        # checking if the counts are correct after re discovering
        self.assertEqual(count_before_delete, count_after_rediscovery)
