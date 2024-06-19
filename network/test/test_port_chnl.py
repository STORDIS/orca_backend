"""
This module contains tests for the Interface API.
"""

from rest_framework import status

from network.test.test_common import TestORCA


class TestPortChnl(TestORCA):
    """
    This class contains tests for the Port Channel API.
    """

    def test_port_channel_config(self):
        """
        Test the port channel configuration.

        This function tests the configuration of the port channels. It sends a DELETE
        request to the device's port channel endpoint to remove any existing port
        channels. Then, it sends a series of GET requests to ensure that the port
        channels have been successfully removed. Next, it sends a PUT request to
        create new port channels with specific configurations. Finally, it sends
        additional GET requests to verify the creation and configuration of the
        port channels.

        Parameters:
        - self: The instance of the test class.

        Returns:
        None
        """
        device_ip = self.device_ips[0]

        # First delete mclag, if it exists.
        # port channel deletion will fail if port channel is found to be a member of mclag.
        self.remove_mclag(device_ip)

        request_body = [
            {
                "mgt_ip": device_ip,
                "lag_name": "PortChannel101",
                "mtu": 8000,
                "admin_status": "up",
            },
            {
                "mgt_ip": device_ip,
                "lag_name": "PortChannel102",
                "mtu": 9100,
                "admin_status": "up",
            },
        ]

        ## Better cleanup all port channels first may be there are existing
        # port channels with member interfaces which are of interest of this
        # test case.
        self.perform_del_port_chnl({"mgt_ip": device_ip})

        # Now delete port channels
        self.perform_del_add_del_port_chnl(request_body)

    def test_port_chnl_mem_config(self):
        """
        Test the configuration of port channel members.
        """
        device_ip = self.device_ips[0]

        ## Better cleanup all port channels first, may be there are existing
        # port channels with the member interfaces which are of interest of this
        # test case.
        self.perform_del_port_chnl({"mgt_ip": device_ip})

        ether_1 = self.ether_names[0]
        ether_2 = self.ether_names[1]
        ether_3 = self.ether_names[2]
        ether_4 = self.ether_names[3]
        mtu = 9100
        # First set same mtu on member interfaces as port channel.
        itf_request_body = [
            {
                "mgt_ip": device_ip,
                "name": ether_1,
                "mtu": mtu,
            },
            {
                "mgt_ip": device_ip,
                "name": ether_2,
                "mtu": mtu,
            },
            {
                "mgt_ip": device_ip,
                "name": ether_3,
                "mtu": mtu,
            },
            {
                "mgt_ip": device_ip,
                "name": ether_4,
                "mtu": mtu,
            },
        ]

        self.assert_with_timeout_retry(
            lambda path, payload: self.put_req(path, payload),
            self.assertEqual,
            "device_interface_list",
            itf_request_body,
            status=status.HTTP_200_OK,
        )

        ## Members of a port channel members should have same speed.
        request_body = [
            {"mgt_ip": device_ip, "name": ether_1, "speed": ""},
            {"mgt_ip": device_ip, "name": ether_2, "speed": ""},
            {"mgt_ip": device_ip, "name": ether_3, "speed": ""},
            {"mgt_ip": device_ip, "name": ether_4, "speed": ""},
        ]
        for req in request_body:
            response_1 = self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                self.assertEqual,
                "device_interface_list",
                {"mgt_ip": device_ip, "name": req["name"]},
                status=status.HTTP_200_OK,
            )

            speed_1 = response_1.json()["speed"]
            req["speed"] = self.get_common_speed_to_set(speed_1)

            self.assert_with_timeout_retry(
                lambda path, payload: self.put_req(path, payload),
                self.assertEqual,
                "device_interface_list",
                req,
                status=status.HTTP_200_OK,
            )

            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                self.assertEqual,
                "device_interface_list",
                req,
                status=status.HTTP_200_OK,
                speed=req["speed"],
            )

        request_body = [
            {
                "mgt_ip": device_ip,
                "lag_name": "PortChannel101",
                "mtu": mtu,
                "admin_status": "up",
                "members": [ether_1, ether_2],
            },
            {
                "mgt_ip": device_ip,
                "lag_name": "PortChannel102",
                "mtu": mtu,
                "admin_status": "up",
                "members": [ether_3, ether_4],
            },
        ]

        # delete mclag, if it exists.
        # port channel deletion will fail if port channel is found to be a member of mclag.
        self.remove_mclag(device_ip)

        # Now delete port channels
        request_body_2 = [
            {"mgt_ip": device_ip, "lag_name": "PortChannel101"},
            {"mgt_ip": device_ip, "lag_name": "PortChannel102"},
        ]

        ## If any portchannel member interface is also a member of vlan it wont be added to portchannel
        ## So better remove all vlans from Interfaces first.
        for req in request_body:
            for mem in req["members"]:
                response = self.del_req(
                    "device_interface_list", {"mgt_ip": device_ip, "name": mem}
                )
                self.assertTrue(
                    response.status_code == status.HTTP_200_OK
                    or any(
                        "resource not found" in res.get("message", "").lower()
                        for res in response.json()["result"]
                        if res != "\n"
                    )
                )
        ## Delete MCLAG if exists, because if the port channel being deleted in the next steps is being used in MCLAG,
        # deletion will fail.
        response = self.del_req("device_mclag_list", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
                if res != "\n"
            )
        )
        self.perform_del_port_chnl(request_body_2)
        self.perform_add_port_chnl(request_body)
        self.perform_del_port_chnl(request_body)
        self.perform_del_port_chnl(request_body_2)

    def test_port_chnl_addtional_attributes(self):
        device_ip = self.device_ips[0]
        self.remove_mclag(device_ip)
        request_body = {
            "mgt_ip": device_ip,
            "lag_name": "PortChannel103",
            "mtu": 9100,
            "admin_status": "up",
            "static": False,
            "min_links": 4,
            "fast_rate": False,
            "description": "test description channel 103",
            "fallback": False,
            "graceful_shutdown_mode": "Enable"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip})
        self.perform_add_port_chnl([request_body])
        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            self.assertEqual,
            "device_port_chnl",
            request_body,
            status=status.HTTP_200_OK,
            static=False,
            min_links=4,
            fast_rate=False,
            description="test description channel 103",
            fallback=False,
            graceful_shutdown_mode="Enable".upper()
        )
        self.perform_del_port_chnl({"mgt_ip": device_ip})

    def test_port_channel_ip(self):
        device_ip = self.device_ips[0]
        self.remove_mclag(device_ip)
        ip_address = "192.10.10.9/24"
        request_body = {
            "mgt_ip": device_ip,
            "lag_name": "PortChannel103",
            "mtu": 9100,
            "admin_status": "up",
            "ip_address": ip_address
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip})
        self.perform_add_port_chnl([request_body])
        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            self.assertEqual,
            "device_port_chnl",
            request_body,
            status=status.HTTP_200_OK,
            ip_address=ip_address
        )
        del_resp = self.del_req("port_channel_ip_remove", {
            "mgt_ip": device_ip, "lag_name": "PortChannel103", "ip_address": ip_address
        })
        self.assertEqual(del_resp.status_code, status.HTTP_200_OK)
        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            self.assertEqual,
            "device_port_chnl",
            {"mgt_ip": device_ip, "lag_name": "PortChannel103"},
            status=status.HTTP_200_OK,
            ip_address=None
        )
        self.perform_del_port_chnl({"mgt_ip": device_ip})

    def test_port_channel_vlan_members(self):
        # Creating vlan for testing
        device_ip = self.device_ips[0]
        vlan_1_name = "Vlan4"
        vlan_1_id = 4
        vlan_2_name = "Vlan5"
        vlan_2_id = 5
        req_payload = [
            {
                "mgt_ip": device_ip,
                "name": vlan_1_name,
                "vlanid": vlan_1_id,
                "mtu": 9000,
                "enabled": False,
                "description": "Test_Vlan1",
            },
            {
                "mgt_ip": device_ip,
                "name": vlan_2_name,
                "vlanid": vlan_2_id,
                "mtu": 9000,
                "enabled": False,
                "description": "Test_Vlan1",
            },
        ]

        response = self.put_req(
            "vlan_config",
            req_payload,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        request_body = {
            "mgt_ip": device_ip,
            "lag_name": "PortChannel103",
            "mtu": 9100,
            "admin_status": "up",
            "vlan_members": {
                "trunk_vlans": [vlan_1_id],
                "access_valn": vlan_2_id
            }
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip})
        self.perform_add_port_chnl([request_body])

        get_response = self.get_req("device_port_chnl", request_body, )
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        members = get_response.json().get("vlan_members")
        self.assertEqual(members.get("trunk_vlans"), [vlan_1_id])
        self.assertEqual(members.get("access_vlan"), vlan_2_id)

        #deleting portchannel vlan members
        member_delete_response = self.del_req("port_chnl_vlan_member_remove", req_json=request_body)
        print(member_delete_response.content)
        self.assertEqual(member_delete_response.status_code, status.HTTP_200_OK)

        get_response = self.get_req("device_port_chnl", request_body, )
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        members = get_response.json().get("vlan_members")
        self.assertEqual(members, {})

        self.perform_del_port_chnl({"mgt_ip": device_ip})
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_2_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
