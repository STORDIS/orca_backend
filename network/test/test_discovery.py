from rest_framework import status

from network.test.test_common import TestORCA


class TestDiscovery(TestORCA):
    """
    This class contains tests for the BGP API.
    """

    def test_discover_additional_device(self):
        """
        This function is used to test the discovery of additional devices.

        Parameters:
            self: The object instance.

        Returns:
            None
        """
        ## Clean DB
        response=self.del_req("del_db")
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        response=self.get_req("device")
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
        
        ## Discover only one device
        device_ip = "10.10.229.88"
        request_body = {
            "address": device_ip,
            "discover_from_config": True
        }
        response=self.put_req("discover",request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        response=self.get_req("device")
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(device_ip in [device['mgt_ip'] for device in response.json()])
            
        ## Discover Devices defined in config file
        request_body = {
            "discover_from_config": True
        }
        response=self.put_req("discover",request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        response=self.get_req("device")
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(device_ip and '10.10.229.88' in [device['mgt_ip'] for device in response.json()])
        
        # Clean DB
        response=self.del_req("del_db")
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        response=self.get_req("device")
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
           