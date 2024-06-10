"""
This module contains tests for the Interface API.
"""

import unittest
from rest_framework import status
from network.test.test_common import TestORCA


class TestInterface(TestORCA):
    """
    This class contains tests for the Interface API.
    """

    def test_interface_enable_config(self):

        device_ip = self.device_ips[0]
        ether_name = self.ether_names[1]
        response = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "name": ether_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        enb = response.json()["enabled"]

        request_body = [
            {"mgt_ip": device_ip, "name": ether_name, "enabled": not enb},
            {"mgt_ip": device_ip, "name": ether_name, "enabled": enb},
        ]
        for data in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.put_and_wait(path, payload),
                self.assertEqual,
                "device_interface_list",
                data,
                status=status.HTTP_200_OK,
            )
            # Call with timeout because subscription response isn't recevied in time.
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                self.assertEqual,
                "device_interface_list",
                data,
                enabled=data["enabled"],
                status=status.HTTP_200_OK,
            )

    def test_interface_mtu_config(self):
        device_ip = self.device_ips[0]
        ether_name = self.ether_names[1]
        response = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "name": ether_name}
        )
        mtu = response.json()["mtu"]
        request_body = [
            {"mgt_ip": device_ip, "name": ether_name, "mtu": mtu - 1},
            {"mgt_ip": device_ip, "name": ether_name, "mtu": mtu},
        ]
        for data in request_body:

            self.assert_with_timeout_retry(
                lambda path, payload: self.put_and_wait(path, payload),
                self.assertEqual,
                "device_interface_list",
                data,
                status=status.HTTP_200_OK,
            )
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                self.assertEqual,
                "device_interface_list",
                data,
                mtu=data["mtu"],
                status=status.HTTP_200_OK,
            )

    def test_interface_description_config(self):
        device_ip = self.device_ips[0]
        ether_name = self.ether_names[1]
        request_body = [
            {"mgt_ip": device_ip, "name": ether_name, "description": "TestPort_1"},
            {"mgt_ip": device_ip, "name": ether_name, "description": "TestPort_2"},
        ]
        for data in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.put_and_wait(path, payload),
                self.assertEqual,
                "device_interface_list",
                data,
                status=status.HTTP_200_OK,
            )
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                self.assertEqual,
                "device_interface_list",
                data,
                description=data["description"],
                status=status.HTTP_200_OK,
            )

    def test_interface_speed_config(self):
        device_ip = self.device_ips[0]
        response_1 = self.get_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": self.ether_names[0]},
        )
        speed_1 = response_1.json()["speed"]
        speed_to_set_1 = self.get_speed_to_set(speed_1)

        response_2 = self.get_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": self.ether_names[1]},
        )
        speed_2 = response_2.json()["speed"]
        speed_to_set_2 = self.get_speed_to_set(speed_2)

        response_3 = self.get_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": self.ether_names[2]},
        )
        speed_3 = response_3.json()["speed"]
        speed_to_set_3 = self.get_speed_to_set(speed_3)

        request_body = [
            {"mgt_ip": device_ip, "name": self.ether_names[0], "speed": speed_to_set_1},
            {"mgt_ip": device_ip, "name": self.ether_names[0], "speed": speed_1},
            {"mgt_ip": device_ip, "name": self.ether_names[1], "speed": speed_to_set_2},
            {"mgt_ip": device_ip, "name": self.ether_names[1], "speed": speed_2},
            {"mgt_ip": device_ip, "name": self.ether_names[2], "speed": speed_to_set_3},
            {"mgt_ip": device_ip, "name": self.ether_names[2], "speed": speed_3},
        ]
        for data in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.put_and_wait(path, payload),
                self.assertEqual,
                "device_interface_list",
                data,
                status=status.HTTP_200_OK,
            )

            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                self.assertEqual,
                "device_interface_list",
                data,
                speed=data["speed"],
                status=status.HTTP_200_OK,
            )

            ## Also confirm the speed of respective port-group (if supported) has been updates as well.
            response = self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                self.assertEqual,
                "interface_pg",
                {"mgt_ip": device_ip, "name": data["name"]},
                speed=data["speed"],
                status=[
                    status.HTTP_204_NO_CONTENT,
                    status.HTTP_200_OK,
                ],  # If port-group is not supported, 204 is returned else 200
            )
            ## If port group is supported then the speed of other member interfaces of the port-group should be updated as well.
            if response.status_code == status.HTTP_200_OK and (
                pg_id := response.json().get("port_group_id")
            ):
                response = self.assert_with_timeout_retry(
                    lambda path, payload: self.get_req(path, payload),
                    self.assertEqual,
                    "port_group_members",
                    {"mgt_ip": device_ip, "port_group_id": pg_id},
                    status=status.HTTP_200_OK,
                )

                for mem_if in response.json() or []:
                    self.assert_with_timeout_retry(
                        lambda path, payload: self.get_req(path, payload),
                        self.assertEqual,
                        "device_interface_list",
                        {"mgt_ip": device_ip, "name": mem_if["name"]},
                        speed=data["speed"],
                        status=status.HTTP_200_OK,
                    )

    def test_interface_fec_config(self):
        """
        Test the FEC configuration of the interface.
        """
        device_ip = self.device_ips[0]
        ether_name = self.ether_names[1]
        response = self.get_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name},
        )
        fec = response.json()["fec"]

        if fec == "FEC_DISABLED":
            fec_to_set = "FEC_AUTO"
        elif fec == "FEC_AUTO":
            fec_to_set = "FEC_RS"
        elif fec == "FEC_RS":
            fec_to_set = "FEC_DISABLED"
        else:
            fec_to_set = "FEC_AUTO"

        request_body = [
            {"mgt_ip": device_ip, "name": ether_name, "fec": fec_to_set},
            {"mgt_ip": device_ip, "name": ether_name, "fec": fec},
        ]
        for data in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.put_and_wait(path, payload),
                self.assertEqual,
                "device_interface_list",
                data,
                status=status.HTTP_200_OK,
            )
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                self.assertEqual,
                "device_interface_list",
                data,
                fec=data["fec"],
                status=status.HTTP_200_OK,
            )

    def test_interface_autoneg_config(self):
        device_ip = self.device_ips[0]
        ether_name = self.ether_names[1]

        # getting details of a single interface for a particular ip
        response_1 = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "name": ether_name}
        )

        # storing the auto-negotiate and advertised-speed
        pre_autoneg = response_1.json()["autoneg"]
        adv_speeds = response_1.json()["valid_speeds"]

        # setting the auto-negotiate to on or off with respective to previous auto-negotiate value
        # and creating request body
        set_autoneg = "on" if pre_autoneg == "off" else "off"
        request_body = (
            {
                "mgt_ip": device_ip,
                "name": ether_name,
                "autoneg": set_autoneg,
                "adv_speeds": adv_speeds,
            },
        )

        # changing the interface auto-negotiate and advertised-speed value
        response = self.put_req("device_interface_list", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # verifying the auto-negotiate and advertised-speed value after changing the auto-negotiate value
        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            self.assertEqual,
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name},
            autoneg=set_autoneg,
            status=status.HTTP_200_OK,
        )

        # creating request to set the auto-negotiate and advertised-speed value to default
        request_body = (
            {
                "mgt_ip": device_ip,
                "name": ether_name,
                "autoneg": pre_autoneg,
                "adv_speeds": adv_speeds,
            },
        )
        response = self.put_req("device_interface_list", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        
        # verifying the auto-negotiate and advertised-speed value has set to default value
        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            self.assertEqual,
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name},
            autoneg=pre_autoneg,
            status=status.HTTP_200_OK,
        )
        

    @unittest.skip("Randomly fails, to be debugged")
    def test_multiple_interfaces_config(self):
        """
        Test the configuration of multiple interfaces.
        This function retrieves the device IP address and the names of two Ethernet interfaces. It then sends GET requests to the API to retrieve the current configuration of each interface, including whether it is enabled, the MTU size, the description, and the speed. The function then modifies the configuration of each interface by creating a request body with updated values for each parameter. It sends a PUT request to the API to update the configuration of both interfaces. Finally, it sends GET requests to the API again to verify that the configuration has been updated successfully.

        Parameters:
            None

        Returns:
            None
        """
        device_ip = self.device_ips[0]
        ether_name_1 = self.ether_names[1]
        ether_name_2 = self.ether_names[2]

        response1 = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "name": ether_name_1}
        )
        enb1 = response1.json()["enabled"]
        mtu1 = response1.json()["mtu"]
        desc1 = response1.json()["description"]
        speed1 = response1.json()["speed"]

        response2 = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "name": ether_name_2}
        )
        enb2 = response2.json()["enabled"]
        mtu2 = response2.json()["mtu"]
        desc2 = response2.json()["description"]
        speed2 = response2.json()["speed"]

        request_body = [
            {
                "mgt_ip": device_ip,
                "name": ether_name_1,
                "enabled": not enb1,
                "mtu": mtu1 - 1,
                "speed": self.get_speed_to_set(speed1),
                "description": "Sample Description",
            },
            {
                "mgt_ip": device_ip,
                "name": ether_name_2,
                "enabled": not enb2,
                "mtu": mtu2 - 1,
                "speed": self.get_speed_to_set(speed2),
                "description": "Sample Description",
            },
        ]
        
        self.assertTrue(self.put_and_wait("device_interface_list", request_body).status_code == status.HTTP_200_OK)
        
        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            self.assertEqual,
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name_1},
            enabled=not enb1,
            description="Sample Description",
            mtu=mtu1 - 1,
            speed=self.get_speed_to_set(speed1),
            status=status.HTTP_200_OK,
        )

        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            self.assertEqual,
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name_2},
            enabled=not enb2,
            description="Sample Description",
            mtu=mtu2 - 1,
            speed=self.get_speed_to_set(speed2),
            status=status.HTTP_200_OK,
        )
        ## Revert config
        request_body = [
            {
                "mgt_ip": device_ip,
                "name": ether_name_1,
                "enabled": enb1,
                "mtu": mtu1,
                "speed": speed1,
                "description": desc1,
            },
            {
                "mgt_ip": device_ip,
                "name": ether_name_2,
                "enabled": enb2,
                "mtu": mtu2,
                "speed": speed2,
                "description": desc2,
            },
        ]

        self.assertTrue(self.put_and_wait("device_interface_list", request_body).status_code == status.HTTP_200_OK)

        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            self.assertEqual,
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name_1},
            enabled=enb1,
            description=desc1,
            mtu=mtu1,
            speed=speed1,
            status=status.HTTP_200_OK,
        )

        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            self.assertEqual,
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name_2},
            enabled=enb2,
            description=desc2,
            mtu=mtu2,
            speed=speed2,
            status=status.HTTP_200_OK,
        )
