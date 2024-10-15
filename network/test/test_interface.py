"""
This module contains tests for the Interface API.
"""

from rest_framework import status
from network.test.test_common import TestORCA
from orca_nw_lib.utils import get_if_alias


class TestInterface(TestORCA):
    """
    This class contains tests for the Interface API.
    """

    def test_interface_enable_config(self):
        device_ip = list(self.device_ips.keys())[0]
        ether_name = self.device_ips[device_ip]["interfaces"][1]
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
                lambda path, payload: self.put_req(path, payload),
                "device_interface_list",
                data,
                status=status.HTTP_200_OK,
            )
            # Call with timeout because subscription response isn't recevied in time.
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "device_interface_list",
                data,
                enabled=data["enabled"],
                status=status.HTTP_200_OK,
            )

    def test_interface_mtu_config(self):
        device_ip = list(self.device_ips.keys())[0]
        ether_name = self.device_ips[device_ip]["interfaces"][1]
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
                lambda path, payload: self.put_req(path, payload),
                "device_interface_list",
                data,
                status=status.HTTP_200_OK,
            )
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "device_interface_list",
                data,
                mtu=data["mtu"],
                status=status.HTTP_200_OK,
            )

    def test_interface_description_config(self):
        device_ip = list(self.device_ips.keys())[0]
        ether_name = self.device_ips[device_ip]["interfaces"][1]
        request_body = [
            {"mgt_ip": device_ip, "name": ether_name, "description": "TestPort_1"},
            {"mgt_ip": device_ip, "name": ether_name, "description": "TestPort_2"},
        ]
        for data in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.put_req(path, payload),
                "device_interface_list",
                data,
                status=status.HTTP_200_OK,
            )
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "device_interface_list",
                data,
                description=data["description"],
                status=status.HTTP_200_OK,
            )

    def test_interface_speed_config(self):
        device_ip = list(self.device_ips.keys())[0]
        response_1 = self.get_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": self.device_ips[device_ip]["interfaces"][0]},
        )
        speed_1 = response_1.json()["speed"]
        speed_to_set_1 = self.get_speed_to_set(speed_1)

        response_2 = self.get_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": self.device_ips[device_ip]["interfaces"][1]},
        )
        speed_2 = response_2.json()["speed"]
        speed_to_set_2 = self.get_speed_to_set(speed_2)

        response_3 = self.get_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": self.device_ips[device_ip]["interfaces"][2]},
        )
        speed_3 = response_3.json()["speed"]
        speed_to_set_3 = self.get_speed_to_set(speed_3)

        request_body = [
            {"mgt_ip": device_ip, "name": self.device_ips[device_ip]["interfaces"][0], "speed": speed_to_set_1},
            {"mgt_ip": device_ip, "name": self.device_ips[device_ip]["interfaces"][0], "speed": speed_1},
            {"mgt_ip": device_ip, "name": self.device_ips[device_ip]["interfaces"][1], "speed": speed_to_set_2},
            {"mgt_ip": device_ip, "name": self.device_ips[device_ip]["interfaces"][1], "speed": speed_2},
            {"mgt_ip": device_ip, "name": self.device_ips[device_ip]["interfaces"][2], "speed": speed_to_set_3},
            {"mgt_ip": device_ip, "name": self.device_ips[device_ip]["interfaces"][2], "speed": speed_3},
        ]
        for data in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.put_req(path, payload),
                "device_interface_list",
                data,
                status=status.HTTP_200_OK,
            )

            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "device_interface_list",
                data,
                speed=data["speed"],
                status=status.HTTP_200_OK,
            )

            ## Also confirm the speed of respective port-group (if supported) has been updates as well.
            response = self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
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
                    "port_group_members",
                    {"mgt_ip": device_ip, "port_group_id": pg_id},
                    status=status.HTTP_200_OK,
                )

                for mem_if in response.json() or []:
                    self.assert_with_timeout_retry(
                        lambda path, payload: self.get_req(path, payload),
                        "device_interface_list",
                        {"mgt_ip": device_ip, "name": mem_if["name"]},
                        speed=data["speed"],
                        status=status.HTTP_200_OK,
                    )

    def test_interface_fec_config(self):
        """
        Test the FEC configuration of the interface.
        """
        device_ip = list(self.device_ips.keys())[0]
        ether_name = self.device_ips[device_ip]["interfaces"][1]
        response = self.get_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name},
        )
        fec = response.json()["fec"]

        if fec == "FEC_DISABLED":
            fec_to_set = "FEC_AUTO"
        elif fec == "FEC_AUTO":
            # FEC_AUTO change to FEC_RS is not supported on all interfaces.
            fec_to_set = "FEC_DISABLED"
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
                lambda path, payload: self.put_req(path, payload),
                "device_interface_list",
                data,
                status=status.HTTP_200_OK,
            )
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "device_interface_list",
                data,
                fec=data["fec"],
                status=status.HTTP_200_OK,
            )

    def test_interface_autoneg_config(self):
        device_ip = list(self.device_ips.keys())[0]
        ether_name = self.device_ips[device_ip]["interfaces"][1]

        # getting details of a single interface for a particular ip
        response_1 = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "name": ether_name}
        )

        # storing the auto-negotiate and advertised-speed
        pre_autoneg = response_1.json()["autoneg"]

        # setting the auto-negotiate to on or off with respective to previous auto-negotiate value
        # and creating request body
        set_autoneg = "on" if pre_autoneg == "off" else "off"
        request_body = (
            {
                "mgt_ip": device_ip,
                "name": ether_name,
                "autoneg": set_autoneg,
            },
        )

        # changing the interface auto-negotiate and advertised-speed value
        response = self.put_req("device_interface_list", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # verifying the auto-negotiate and advertised-speed value after changing the auto-negotiate value
        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
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
            },
        )
        response = self.put_req("device_interface_list", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # verifying the auto-negotiate and advertised-speed value has set to default value
        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name},
            autoneg=pre_autoneg,
            status=status.HTTP_200_OK,
        )

    def test_interface_training_link_config(self):
        device_ip = list(self.device_ips.keys())[0]
        ether_name = self.device_ips[device_ip]["interfaces"][1]

        # getting details of a single interface for a particular ip
        response_1 = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "name": ether_name}
        )

        # storing the lvariables and creating request body
        pre_link_training = response_1.json()["link_training"]

        set_link_training = "on" if pre_link_training == "off" else "off"
        request_body = (
            {
                "mgt_ip": device_ip,
                "name": ether_name,
                "link_training": set_link_training,
            },
        )

        # changing the interface link training value to new value
        response = self.put_req("device_interface_list", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # verifying the link training value after changing the link training value
        response_2 = self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name},
            link_training=set_link_training,
            status=status.HTTP_200_OK,
        )

        # creating request to set the link training value to default value
        request_body = (
            {
                "mgt_ip": device_ip,
                "name": ether_name,
                "link_training": pre_link_training,
            },
        )

        # changing the interface link training value to default value
        response = self.put_req("device_interface_list", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # verifying the link training value has set to default value
        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name},
            link_training=pre_link_training,
            status=status.HTTP_200_OK,
        )

    def test_interface_adv_speed_config(self):
        device_ip = list(self.device_ips.keys())[0]
        ether_name = self.device_ips[device_ip]["interfaces"][1]

        # getting details of a single interface for a particular ip
        response_1 = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "name": ether_name}
        )

        # crating variables to set the values
        adv_speeds = response_1.json()["adv_speeds"]
        valid_speeds = response_1.json()["valid_speeds"]

        if adv_speeds == "all":
            set_adv_speed = valid_speeds
        else:
            set_adv_speed = ""

        request_body = (
            {
                "mgt_ip": device_ip,
                "name": ether_name,
                "adv_speeds": set_adv_speed,
            },
        )

        # setting the and advertised-speed value with changed values
        response = self.put_req("device_interface_list", request_body)
        ## Assert with timeout retry because subscription response isn't recevied in time, and orca is not yet ready to receive the subscription notifications.
        self.assert_with_timeout_retry(
            lambda path, payload: self.put_req(path, payload),
            "device_interface_list",
            request_body,
            status=status.HTTP_200_OK,
        )

        # verifying the advertised-speed value after changing the advertised-speed with changed values
        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name},
            adv_speeds=set_adv_speed,
            status=status.HTTP_200_OK,
        )

        # variable to set back the advertised-speed to previous value
        if adv_speeds == "all":
            set_adv_speed = ""
        else:
            set_adv_speed = valid_speeds

        request_body = (
            {
                "mgt_ip": device_ip,
                "name": ether_name,
                "adv_speeds": set_adv_speed,
            },
        )

        # setting the and advertised-speed value with default values
        response = self.put_req("device_interface_list", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # checking the advertised-speed value after changing the advertised-speed with default values
        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_name},
            adv_speeds=set_adv_speed,
            status=status.HTTP_200_OK,
        )

    # @unittest.skip("Randomly fails, to be debugged")
    def test_multiple_interfaces_config(self):
        """
        Test the configuration of multiple interfaces.
        This function retrieves the device IP address and the names of two Ethernet interfaces. It then sends GET requests to the API to retrieve the current configuration of each interface, including whether it is enabled, the MTU size, the description, and the speed. The function then modifies the configuration of each interface by creating a request body with updated values for each parameter. It sends a PUT request to the API to update the configuration of both interfaces. Finally, it sends GET requests to the API again to verify that the configuration has been updated successfully.

        Parameters:
            None

        Returns:
            None
        """
        device_ip = list(self.device_ips.keys())[0]
        for eth in self.device_ips[device_ip]["interfaces"]:
            resp = self.get_req(
                "device_interface_list", {"mgt_ip": device_ip, "name": eth}
            ).json()
            request_body = {
                "mgt_ip": device_ip,
                "name": eth,
                "enabled": not resp["enabled"],  # Toggle value
                "mtu": (9101 if resp["mtu"] <= 9100 else 9100),
                "speed": self.get_speed_to_set(resp["speed"]),
                "description": f'{eth}_{resp.get("enabled")}_{resp.get("mtu")}',
            }
            self.assert_with_timeout_retry(
                lambda path, data: self.put_req(path, data),
                "device_interface_list",
                request_body,
                status=status.HTTP_200_OK,
            )
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "device_interface_list",
                request_body,
                enabled=request_body.get("enabled"),
                description=request_body.get("description"),
                mtu=request_body.get("mtu"),
                speed=request_body.get("speed"),
                status=status.HTTP_200_OK,
            )

    def test_interface_breakout_speed(self):
        for device_ip in self.device_ips.keys():

            eth = self.device_ips[device_ip]["breakouts"][0]
            response = self.get_req("device", {"mgt_ip": device_ip})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            device = response.json()
            if "kvm" in device["platform"]:
                print("KVM device not supported in this test.")
                continue

            # adding interface member
            interface = self.get_req("device_interface_list", {"mgt_ip": device_ip, "name": eth})
            interface_alias = get_if_alias(interface.json()["alias"])
            no_of_lanes = str(interface.json()["lanes"]).split(",")

            # adding breakout configuration
            request_body = {
                "mgt_ip": device_ip,
                "if_alias": interface_alias,
                "breakout_mode": f"{len(no_of_lanes)}xSPEED_10GB",
            }

            # delete existing breakout configuration
            self.assert_response_status(
                self.del_req("breakout", request_body),
                status.HTTP_200_OK,
                "No change in port breakout mode",
            )

            response = self.put_req("breakout", request_body)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            interface = self.get_req("device_interface_list", {"mgt_ip": device_ip, "name": eth})

            self.assertEqual(interface.json()["breakout_mode"], request_body["breakout_mode"])
            self.assertTrue(interface_alias in interface.json()["alias"])
            self.assertTrue(interface.json()["breakout_status"] in ["InProgress", "Completed"])
            self.assertFalse(interface.json()["breakout_supported"])

            eth_names = int(eth.replace("Ethernet", ""))
            for i in range(eth_names, eth_names + 3):
                interface = self.get_req("device_interface_list", {"mgt_ip": device_ip, "name": f"Ethernet{i}"})
                self.assertEqual(interface.json()["breakout_mode"], request_body["breakout_mode"])
                self.assertTrue(interface_alias in interface.json()["alias"])
                self.assertTrue(interface.json()["breakout_status"] in ["InProgress", "Completed"])
                self.assertFalse(interface.json()["breakout_supported"])

            # updating breakout configuration
            request_body = {
                "mgt_ip": device_ip,
                "if_name": eth,
                "if_alias": interface_alias,
                "breakout_mode": f"{len(no_of_lanes)}xSPEED_25GB",
            }
            self.assert_response_status(
                self.put_req("breakout", request_body),
                status.HTTP_200_OK,
                "Port breakout is in progress.",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            interface = self.get_req("device_interface_list", {"mgt_ip": device_ip, "name": eth})
            self.assertEqual(interface.json()["breakout_mode"], request_body["breakout_mode"])
            self.assertTrue(interface_alias in interface.json()["alias"])
            self.assertTrue(interface.json()["breakout_status"] in ["InProgress", "Completed"])

            # deleting breakout configuration
            self.assert_response_status(
                self.del_req("breakout", request_body),
                status.HTTP_200_OK,
                "Port breakout is in progress.",
            )
            eth_names = int(eth.replace("Ethernet", ""))
            for i in range(eth_names, eth_names + 3):
                response = self.get_req("device_interface_list", {"mgt_ip": device_ip, "name": f"Ethernet{i}"})
                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

            interface = self.get_req("device_interface_list", {"mgt_ip": device_ip, "name": eth})
            self.assertEqual(interface.json()["breakout_mode"], None)
            self.assertTrue(interface_alias in interface.json()["alias"])

    def test_interface_ip_config(self):
        device_ip = list(self.device_ips.keys())[0]
        ether_name = self.device_ips[device_ip]["interfaces"][0]
        ip = "10.10.100.1"
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

        # updating the ip_address with new url
        ip = "10.10.121.11"
        request_body["ip_address"] = f"{ip}/{prefix_len}"

        self.assert_with_timeout_retry(
            lambda path, data: self.put_req(path, data),
            "subinterface",
            request_body,
            status=status.HTTP_200_OK,
        )

        # verifying the ip_address value after changing the ip_address with changed values
        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        if isinstance(response_body, list):
            self.assertTrue(any([i["ip_address"] == ip for i in response_body]))
        else:
            self.assertEqual(response_body["ip_address"], ip)

        # removing the ip_address with new url
        response = self.del_req("subinterface", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verifying the ip_address deletion
        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_secondary_ip(self):
        device_ip = list(self.device_ips.keys())[0]
        ether_name = self.device_ips[device_ip]["interfaces"][0]
        ip = "10.10.100.1"
        prefix_len = 24

        # adding primary ip first then secondary
        request_body = {
            "mgt_ip": device_ip,
            "name": ether_name,
            "ip_address": f"{ip}/{prefix_len}",
            "secondary": False
        }
        self.assert_with_timeout_retry(
            lambda path, data: self.put_req(path, data),
            "device_interface_list",
            request_body,
            status=status.HTTP_200_OK,
        )

        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        if isinstance(response_body, list):
            self.assertTrue(
                any([i["ip_address"] == ip and i["secondary"] is False for i in response_body])
            )
        else:
            self.assertEqual(response_body["ip_address"], ip)
            self.assertFalse(response_body["secondary"])

        secondary_ip = "10.10.100.2"
        request_body = {
            "mgt_ip": device_ip,
            "name": ether_name,
            "ip_address": f"{secondary_ip}/{prefix_len}",
            "secondary": True
        }
        self.assert_with_timeout_retry(
            lambda path, data: self.put_req(path, data),
            "device_interface_list",
            request_body,
        )

        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        if isinstance(response_body, list):
            self.assertTrue(
                any([i["ip_address"] == secondary_ip and i["secondary"] is True
                     for i in response_body])
            )
        else:
            self.assertEqual(response_body["ip_address"], secondary_ip)
            self.assertTrue(response_body["secondary"])

        # removing the ip_address with new url
        response = self.del_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verifying the ip_address deletion
        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_ip_address_deletion(self):
        device_ip = list(self.device_ips.keys())[0]
        ether_name = self.device_ips[device_ip]["interfaces"][0]
        ip_1 = "10.10.100.1"
        ip_2 = "10.10.100.2"
        prefix_len = 24

        # delete all ip addresses
        request_body = {
            "mgt_ip": device_ip,
            "name": ether_name
        }
        response = self.del_req("subinterface", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # adding primary ip
        request_body = {
            "mgt_ip": device_ip,
            "name": ether_name,
            "ip_address": f"{ip_1}/{prefix_len}",
            "secondary": False
        }
        self.put_req("subinterface", request_body)

        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        if isinstance(response_body, list):
            self.assertTrue(any([i["ip_address"] == ip_1 for i in response_body]))
        else:
            self.assertEqual(response_body["ip_address"], ip_2)

        # adding secondary ip
        request_body = {
            "mgt_ip": device_ip,
            "name": ether_name,
            "ip_address": f"{ip_2}/{prefix_len}",
            "secondary": True
        }
        self.put_req("subinterface", request_body)

        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        print(response_body)
        if isinstance(response_body, list):
            self.assertTrue(any([i["ip_address"] == ip_2 for i in response_body]))
        else:
            self.assertEqual(response_body["ip_address"], ip_2)

        # removing the secondary ip
        response = self.del_req("subinterface", {
            "mgt_ip": device_ip, "name": ether_name, "ip_address": ip_2, "secondary": True
        })
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verifying the ip_address deletion
        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_body = response.json()
        self.assertTrue(all([i["ip_address"] != ip_2 for i in response_body]))

        # removing the primary ip
        response = self.del_req("subinterface", {
            "mgt_ip": device_ip, "name": ether_name, "ip_address": ip_1, "secondary": False
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verifying the ip_address deletion
        response = self.get_req("subinterface", {"mgt_ip": device_ip, "name": ether_name})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
