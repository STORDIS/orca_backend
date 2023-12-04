"""
This module contains tests for the BGP API.
"""

from rest_framework import status

from network.test.test_common import ORCATest


class PortGroupTest(ORCATest):
    """
    Test class for the BGP API.
    """

    def test_port_group_speed_config(self):
        """
        Test port group speed configuration.
        """
        device_ip = self.device_ips[0]
        request_body = {"mgt_ip": device_ip, "port_group_id": "1", "speed": "SPEED_10G"}

        ## Simply delete all port channels as if an interfacce which is member of a port channel as well, 
        # speed config will fail.
        
        self.perform_del_port_chnl( {"mgt_ip": device_ip})

        # Get current speed
        response = self.get_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        orig_speed = response.json().get("speed")
        request_body["speed"] = self.get_speed_to_set(orig_speed)
        # Update speed
        response = self.put_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        # Confirm changes
        response = self.get_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["speed"], response.json().get("speed"))
        # Confirm speed changes on all member interfaces
        for mem_if in response.json().get("mem_intfs"):
            response = self.get_req(
                "device_interface_list", {"mgt_ip": device_ip, "intfc_name": mem_if}
            )
            self.assertEqual(request_body["speed"], response.json().get("speed"))

        # Restore speed
        request_body["speed"] = orig_speed
        response = self.put_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        # Confirm changes
        response = self.get_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["speed"], response.json().get("speed"))
        # Confirm speed changes on all member interfaces
        for mem_if in response.json().get("mem_intfs"):
            response = self.get_req(
                "device_interface_list", {"mgt_ip": device_ip, "intfc_name": mem_if}
            )
            self.assertEqual(request_body["speed"], response.json().get("speed"))

    def test_multiple_port_group_speed_config(self):
        """
        Test multiple port group speed configuration.
        """
        device_ip = self.device_ips[0]
        request_body = {"mgt_ip": device_ip}
        
        ## Simply delete all port channels as if an interfacce which is member of a port channel as well, 
        # speed config will fail.
        
        self.perform_del_port_chnl({"mgt_ip": device_ip})

        # Get current speed
        response = self.get_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        port_groups_1 = response.json()
        for pg in port_groups_1:
            pg["mgt_ip"] = device_ip
            pg["orig_speed"] = pg.get("speed")
            pg["speed"] = self.get_speed_to_set(pg["orig_speed"])

        # Update speed on all port groups
        response = self.put_req("port_groups", port_groups_1)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        port_groups_2 = response.json()
        for pg_2 in port_groups_2:
            for pg_1 in port_groups_1:
                # Confirm changes
                if pg_1["port_group_id"] == pg_2["port_group_id"]:
                    self.assertEqual(pg_1["speed"], pg_2["speed"])

        # Restore speed
        for pg in port_groups_1:
            pg["speed"] = pg["orig_speed"]
        response = self.put_req("port_groups", port_groups_1)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("port_groups", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        port_groups_2 = response.json()
        for pg_2 in port_groups_2:
            for pg_1 in port_groups_1:
                # Confirm changes
                if pg_1["port_group_id"] == pg_2["port_group_id"]:
                    self.assertEqual(pg_1["speed"], pg_2["speed"])
