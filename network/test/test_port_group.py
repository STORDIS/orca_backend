"""
This module contains tests for the BGP API.
"""

from rest_framework import status

from network.test.test_common import TestORCA


class TestPortGroup(TestORCA):
    """
    Test class for the BGP API.
    """
    vlan_name = "Vlan2"

    def test_port_group_speed_config(self):
        """
        Test port group speed configuration.
        """
        for device_ip in self.device_ips.keys():

            # skip test if no port groups exist
            response = self.get_req("port_groups", {"mgt_ip": device_ip})
            if response.status_code == status.HTTP_204_NO_CONTENT:
                print("No port groups exist on device %s" % device_ip)
                continue

            request_body = {"mgt_ip": device_ip, "port_group_id": "1", "speed": "SPEED_10G"}

            ## Delete MCLAG because if the port channel being deleted in the next step is being used in MCLAG, deletion will fail.
            response = self.del_req("device_mclag_list", {"mgt_ip": device_ip})

            self.assertTrue(
                response.status_code == status.HTTP_200_OK
                or any(
                    "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
                    if res != "\n"
                )
            )

            ## Delete VLANs then delete port channels in next steps.
            response = self.del_req(
                "vlan_ip_remove", {"mgt_ip": device_ip, "name": self.vlan_name}
            )
            response = self.del_req(
                "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
            )
            self.assertTrue(
                response.status_code == status.HTTP_200_OK
                or any("not found" in res.get("message", "").lower() for res in response.json()["result"]
                       if res != "\n")
            )

            ## Simply delete all port channels as if an interface which is member of a port channel as well,
            # speed config will fail.
            self.perform_del_port_chnl({"mgt_ip": device_ip})

            # Get current speed
            response = self.get_req("port_groups", request_body)
            self.assertTrue(response.status_code == status.HTTP_200_OK)
            orig_speed = response.json().get("speed")
            request_body["speed"] = self.get_speed_to_set(orig_speed)

            self.assert_with_timeout_retry(
                lambda path, data: self.put_req(path, data),
                "port_groups",
                request_body,
                status=status.HTTP_200_OK,
            )
            # confirm port group change
            self.assert_with_timeout_retry(
                lambda path, data: self.get_req(path, data),
                "port_groups",
                request_body,
                status=status.HTTP_200_OK,
                speed=request_body["speed"],
            )
            # Confirm speed changes on all member interfaces
            for mem_if in response.json().get("mem_intfs"):
                self.assert_with_timeout_retry(
                    lambda path, data: self.get_req(path, data),
                    "device_interface_list",
                    {"mgt_ip": device_ip, "name": mem_if},
                    status=status.HTTP_200_OK,
                    speed=request_body["speed"],
                )

            # Restore speed
            request_body["speed"] = orig_speed
            self.assert_with_timeout_retry(
                lambda path, data: self.put_req(path, data),
                "port_groups",
                request_body,
                status=status.HTTP_200_OK,
            )
            # Confirm port group change
            self.assert_with_timeout_retry(
                lambda path, data: self.get_req(path, data),
                "port_groups",
                request_body,
                status=status.HTTP_200_OK,
                speed=request_body["speed"],
            )
            # Confirm speed changes on all member interfaces
            for mem_if in response.json().get("mem_intfs"):
                self.assert_with_timeout_retry(
                    lambda path, data: self.get_req(path, data),
                    "device_interface_list",
                    {"mgt_ip": device_ip, "name": mem_if},
                    status=status.HTTP_200_OK,
                    speed=request_body["speed"],
                )

    def test_multiple_port_group_speed_config(self):
        """
        Test multiple port group speed configuration.
        """
        for device_ip in self.device_ips.keys():

            # skip test if no port groups exist
            response = self.get_req("port_groups", {"mgt_ip": device_ip})
            if response.status_code == status.HTTP_204_NO_CONTENT:
                print("No port groups exist on device %s" % device_ip)
                continue

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
            self.assert_with_timeout_retry(
                lambda path, data: self.put_req(path, data),
                "port_groups",
                port_groups_1,
                status=status.HTTP_200_OK,
            )

            response = self.get_req("port_groups", request_body)
            self.assertTrue(response.status_code == status.HTTP_200_OK)
            port_groups_2 = response.json()
            for pg_2 in port_groups_2:
                for pg_1 in port_groups_1:
                    # Confirm changes
                    if pg_1["port_group_id"] == pg_2["port_group_id"]:
                        # confirm port group change
                        self.assert_with_timeout_retry(
                            lambda path, data: self.get_req(path, data),
                            "port_groups",
                            {"mgt_ip": device_ip, "port_group_id": pg_1["port_group_id"]},
                            status=status.HTTP_200_OK,
                            speed=pg_2["speed"],
                        )

            # Restore speed
            for pg in port_groups_1:
                pg["speed"] = pg["orig_speed"]

            self.assert_with_timeout_retry(
                lambda path, data: self.put_req(path, data),
                "port_groups",
                port_groups_1,
                status=status.HTTP_200_OK,
            )

            response = self.get_req("port_groups", request_body)
            self.assertTrue(response.status_code == status.HTTP_200_OK)
            port_groups_2 = response.json()
            for pg_2 in port_groups_2:
                for pg_1 in port_groups_1:
                    # Confirm changes
                    self.assert_with_timeout_retry(
                        lambda path, data: self.get_req(path, data),
                        "port_groups",
                        {"mgt_ip": device_ip, "port_group_id": pg_1["port_group_id"]},
                        status=status.HTTP_200_OK,
                        speed=pg_1["speed"],
                    )

    def test_port_group_interfaces_valid_speed_update(self):
        """
        Test port group interfaces valid speed update.
        - This testcase tests that valid speeds are updated on all interfaces when port group speed is changed/updated.
        """
        for device_ip in self.device_ips.keys():

            # skip test if no port groups exist
            response = self.get_req("port_groups", {"mgt_ip": device_ip})
            if response.status_code == status.HTTP_204_NO_CONTENT:
                print("No port groups exist on device %s" % device_ip)
                continue

            request_body = {"mgt_ip": device_ip, "port_group_id": "1"}

            ## Simply delete all port channels as if an interface which is member of a port channel as well,
            # speed config will fail.
            self.perform_del_port_chnl({"mgt_ip": device_ip})

            # Get current speed
            response = self.get_req("port_groups", request_body)
            self.assertTrue(response.status_code == status.HTTP_200_OK)
            member_ifs=response.json().get("mem_intfs")

            request_body["speed"] = self.get_speed_to_set(response.json()["speed"])

            ## Necessary to do with timeout retry because if only this test is ran, or another test case removed this device or unsubscribed it,
            # may be device is not ready to receive the notifs and put request is made immediately, this may cause test failure.
            self.assert_with_timeout_retry(
                lambda path, data: self.put_req(path, data),
                "port_groups",
                request_body,
                status=status.HTTP_200_OK,
            )

            # Confirm port group change
            self.assert_with_timeout_retry(
                lambda path, data: self.get_req(path, data),
                "port_groups",
                request_body,
                status=status.HTTP_200_OK,
                speed=request_body["speed"],
            )
            # Confirm speed changes on all member interfaces
            for mem_if in member_ifs:
                self.assert_with_timeout_retry(
                    lambda path, data: self.get_req(path, data),
                    "device_interface_list",
                    {"mgt_ip": device_ip, "name": mem_if},
                    status=status.HTTP_200_OK,
                    speed=request_body["speed"],
                    valid_speeds=self.get_valid_speeds(request_body["speed"])
                )


            ## Change speed once again
            response = self.get_req("port_groups", request_body)
            self.assertTrue(response.status_code == status.HTTP_200_OK)
            request_body["speed"] = self.get_speed_to_set(response.json()["speed"])
            response = self.put_req("port_groups", request_body)
            self.assertTrue(
                response.status_code == status.HTTP_200_OK
                or any(
                    "resource not found" in res.get("message", "").lower()
                    for res in response.json()["result"]
                    if res != "\n"
                )
            )
            # Confirm port group change
            self.assert_with_timeout_retry(
                lambda path, data: self.get_req(path, data),
                "port_groups",
                request_body,
                status=status.HTTP_200_OK,
                speed=request_body["speed"],
            )
            # Confirm speed changes on all member interfaces
            for mem_if in member_ifs:
                self.assert_with_timeout_retry(
                    lambda path, data: self.get_req(path, data),
                    "device_interface_list",
                    {"mgt_ip": device_ip, "name": mem_if},
                    status=status.HTTP_200_OK,
                    speed=request_body["speed"],
                    valid_speeds=self.get_valid_speeds(request_body["speed"])
                )

    def test_get_port_group_details_from_intfc_name(self):
        """
        Test get port group details from interface name.
        """
        for device_ip in self.device_ips.keys():
            port_group_id = 1

            # skip test if no port groups exist
            response = self.get_req("port_groups", {"mgt_ip": device_ip})
            if response.status_code == status.HTTP_204_NO_CONTENT:
                print("No port groups exist on device %s" % device_ip)
                continue

            request_body = {"mgt_ip": device_ip, "port_group_id": port_group_id}

            ## Simply delete all port channels as if an interface which is member of a port channel as well,
            # speed config will fail.
            self.perform_del_port_chnl({"mgt_ip": device_ip})

            # port group details by id
            response = self.get_req("port_groups", request_body)
            self.assertTrue(response.status_code == status.HTTP_200_OK)

            # get port group details by intfc name
            interfaces = response.json().get("mem_intfs")
            for interface in interfaces:
                request_body = {"mgt_ip": device_ip, "intf_name": interface}
                response = self.get_req(
                    "group_from_intfc", req_json=request_body
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                # Confirm port group details
                self.assertEqual(port_group_id, int(response.json().get("port_group_id")))

