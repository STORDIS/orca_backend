"""
This module contains tests for the Interface API.
"""

from rest_framework import status

from network.test.test_common import ORCATest


class InterfaceTest(ORCATest):
    """
    This class contains tests for the Interface API.
    """

    def test_interface_enable_config(self):
        """
        Test the enable configuration for the interface.

        This function tests the enable configuration for the interface by performing the following steps:
        1. Retrieve the device IP and Ethernet name using the 'retrieve_device' function.
        2. Send a GET request to the 'device_interface_list' endpoint with the device IP and Ethernet name as parameters.
        3. Extract the 'enabled' value from the response JSON.
        4. Create a request body with two dictionaries:
           a. The first dictionary has the device IP, Ethernet name, and the negation of the 'enabled' value.
           b. The second dictionary has the device IP, Ethernet name, and the 'enabled' value.
        5. Iterate over the request body and perform the following steps for each dictionary:
           a. Send a PUT request to the 'device_interface_list' endpoint with the dictionary as data.
           b. Send a GET request to the 'device_interface_list' endpoint with the device IP and Ethernet name as parameters.
           c. Assert that the 'enabled' value in the response JSON is equal to the 'enabled' value in the dictionary.

        This function does not have any parameters.

        This function does not return any values.
        """
        device_ip = self.device_ips[0]
        ether_name = self.ether_names[1]
        response = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "intfc_name": ether_name}
        )
        enb = response.json()["enabled"]

        request_body = [
            {"mgt_ip": device_ip, "name": ether_name, "enabled": not enb},
            {"mgt_ip": device_ip, "name": ether_name, "enabled": enb},
        ]
        for data in request_body:
            response = self.put_req("device_interface_list", data)
            response = self.get_req(
                "device_interface_list",
                {"mgt_ip": device_ip, "intfc_name": ether_name},
            )
            self.assertEqual(response.json()["enabled"], data["enabled"])

    def test_interface_mtu_config(self):
        """
        Test the interface MTU configuration.

        This function retrieves the device IP and interface name from the `retrieve_device` method.
        It then sends a GET request to the `device_interface_list` endpoint, passing the device IP and interface name as parameters.
        The response is expected to contain the MTU value, which is extracted from the JSON response.

        The function creates a request body with two entries. Each entry contains the device IP, interface name, and a modified MTU value.
        The first entry has the MTU value decreased by 1, while the second entry has the original MTU value.

        The function iterates through the request body and sends a PUT request to the `device_interface_list` endpoint for each entry.
        After each PUT request, it sends a GET request to the same endpoint to retrieve the updated MTU value.
        The updated MTU value is then compared with the expected value from the request body using the `self.assertEqual` method.

        This function does not have any parameters and does not return any value.
        """
        device_ip = self.device_ips[0]
        ether_name = self.ether_names[1]
        response = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "intfc_name": ether_name}
        )
        mtu = response.json()["mtu"]
        request_body = [
            {"mgt_ip": device_ip, "name": ether_name, "mtu": mtu - 1},
            {"mgt_ip": device_ip, "name": ether_name, "mtu": mtu},
        ]
        for data in request_body:
            response = self.put_req("device_interface_list", data)
            response = self.get_req(
                "device_interface_list", {"mgt_ip": device_ip, "intfc_name": ether_name}
            )
            self.assertEqual(response.json()["mtu"], data["mtu"])

    def test_interface_description_config(self):
        """
        Test the interface description configuration.

        This function retrieves the device IP and Ethernet name from the 'retrieve_device' method.
        Then, it sends a GET request to the 'device_interface_list' endpoint with the retrieved device IP and Ethernet name as query parameters.
        The response is expected to contain a JSON object, from which the 'description' field is extracted.
        The function then constructs a request body with the retrieved device IP, Ethernet name, and the extracted description.
        It sends a PUT request to the 'device_interface_list' endpoint with each item in the request body.
        After each PUT request, the function sends a GET request to the 'device_interface_list' endpoint with the retrieved device IP and Ethernet name as query parameters.
        The response is expected to contain a JSON object, from which the 'description' field is extracted.
        The extracted description is compared with the 'description' field in the request body using the 'assertEqual' method.

        Parameters:
        - self: The instance of the test class.

        Returns:
        - None
        """
        device_ip = self.device_ips[0]
        ether_name = self.ether_names[1]
        response = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "intfc_name": ether_name}
        )
        desc = response.json()["description"]
        request_body = [
            {"mgt_ip": device_ip, "name": ether_name, "description": "SamplePort"},
            {"mgt_ip": device_ip, "name": ether_name, "description": desc},
        ]
        for data in request_body:
            response = self.put_req("device_interface_list", data)
            response = self.get_req(
                "device_interface_list", {"mgt_ip": device_ip, "intfc_name": ether_name}
            )
            self.assertEqual(response.json()["description"], data["description"])

    def get_speed_to_set(self, speed):
        """
        Get the speed to set based on the given speed.

        Args:
            speed (str): The current speed.

        Returns:
            str: The speed to set.

        Raises:
            None
        """
        if speed == "SPEED_40GB":
            speed_to_set = "SPEED_100GB"
        elif speed == "SPEED_100GB":
            speed_to_set = "SPEED_40GB"
        elif speed == "SPEED_10GB":
            speed_to_set = "SPEED_25GB"
        elif speed == "SPEED_25GB":
            speed_to_set = "SPEED_10GB"
        else:
            speed_to_set = "SPEED_25GB"
        return speed_to_set

    def test_interface_speed_config(self):
        """
        Test the speed configuration of the interface.

        This function tests the speed configuration of the interface by performing the following steps:
        1. Retrieve the device IP and interface name using the `retrieve_device` method.
        2. Send a GET request to the `device_interface_list` endpoint with the device IP and interface name as parameters.
        3. Retrieve the speed value from the response JSON.
        4. Get the speed to set using the `get_speed_to_set` method.
        5. Create a request body with the device IP, interface name, and both the set speed and original speed.
        6. Iterate over the request body and perform the following steps for each data:
            - Send a PUT request to the `device_interface_list` endpoint with the data as the request body.
            - Send a GET request to the `device_interface_list` endpoint with the device IP and interface name as parameters.
            - Assert that the speed in the response JSON matches the speed in the data.

        This function does not have any parameters.

        This function does not return any values.
        """
        device_ip = self.device_ips[0]
        ether_name = self.ether_names[1]
        response = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "intfc_name": ether_name}
        )
        speed = response.json()["speed"]
        speed_to_set = self.get_speed_to_set(speed)
        request_body = [
            {"mgt_ip": device_ip, "name": ether_name, "speed": speed_to_set},
            {"mgt_ip": device_ip, "name": ether_name, "speed": speed},
        ]
        for data in request_body:
            response = self.put_req("device_interface_list", data)
            response = self.get_req(
                "device_interface_list", {"mgt_ip": device_ip, "intfc_name": ether_name}
            )
            self.assertEqual(response.json()["speed"], data["speed"])

    def test_interface_fec_config(self):
        """
        Test the FEC configuration of the interface.
        """
        device_ip = self.device_ips[0]
        ether_name = self.ether_names[1]
        response = self.get_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "intfc_name": ether_name},
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
            response = self.put_req("device_interface_list", data)
            response = self.get_req(
                "device_interface_list", {"mgt_ip": device_ip, "intfc_name": ether_name}
            )
            self.assertEqual(response.json()["fec"], data["fec"])

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
            "device_interface_list", {"mgt_ip": device_ip, "intfc_name": ether_name_1}
        )
        enb1 = response1.json()["enabled"]
        mtu1 = response1.json()["mtu"]
        desc1 = response1.json()["description"]
        speed1 = response1.json()["speed"]

        response2 = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "intfc_name": ether_name_2}
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
        response = self.put_req("device_interface_list", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response1 = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "intfc_name": ether_name_1}
        )
        self.assertEqual(response1.json()["enabled"], enb1)
        self.assertEqual(response1.json()["mtu"], mtu1)
        self.assertEqual(response1.json()["description"], desc1)
        self.assertEqual(response1.json()["speed"], speed1)

        response2 = self.get_req(
            "device_interface_list", {"mgt_ip": device_ip, "intfc_name": ether_name_2}
        )
        self.assertEqual(response2.json()["enabled"], enb2)
        self.assertEqual(response2.json()["mtu"], mtu2)
        self.assertEqual(response2.json()["description"], desc2)
        self.assertEqual(response2.json()["speed"], speed2)
