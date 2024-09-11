from rest_framework import status

from network.test.test_common import TestORCA


class TestDelete(TestORCA):

    def test_delete_device(self):

        # Note : ensure that there are atleast 2 devices will be dicovered
        count_before_delete = 0
        count_after_delete = 0
        count_after_rediscovery = 0

        # get discover device before deleting
        response = self.get_req("device")
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # storing count in variable for compaction
        count_before_delete = len(response.json())

        device_ips = list(self.device_ips.keys())
        # delete the one device
        request_body = {
            "mgt_ip": device_ips[0],
        }
        response = self.del_req("del_db", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get device after deletion
        response = self.get_req("device")
        self.assertTrue(
            response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )  # After deleting a device there might be device remained in the DB (200_OK)
        ## or there might be 0 devices left(204_NO_CONTENT) as the deleted device was the only one in the DB.

        # storing count in variable for compaction
        count_after_delete = len(response.data)

        # checking if the counts are correct
        # i. e device before deletion must be one grater than device after deletion
        self.assertEqual(count_after_delete, count_before_delete - 1)

        # re discovering the deleted device
        request_body = {"address": device_ips[0], "discover_from_config": False}
        response = self.put_req("discover", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get discover device after  re discovering
        response = self.get_req("device")
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # storing count in variable for compaction
        count_after_rediscovery = len(response.json())

        # checking if the counts are correct after re discovering
        self.assertEqual(count_before_delete, count_after_rediscovery)
