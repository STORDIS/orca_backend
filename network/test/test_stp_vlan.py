from rest_framework import status

from network.test.test_common import TestORCA


class TestSTPVlan(TestORCA):

    def perform_add_stp_global(self, request_body):
        # create stp config
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["enabled_protocol"], response_body["enabled_protocol"])
        self.assertEqual(request_body["bpdu_filter"], response_body["bpdu_filter"])
        self.assertEqual(request_body["hello_time"], response_body["hello_time"])
        self.assertEqual(request_body["max_age"], response_body["max_age"])
        self.assertEqual(request_body["forwarding_delay"], response_body["forwarding_delay"])
        self.assertEqual(request_body["bridge_priority"], response_body["bridge_priority"])

    def perform_delete_stp_global(self, request_body):
        # delete stp config if it exists
        response = self.del_req("stp_config", request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

    def test_stp_vlan_config(self):
        device_ip = list(self.device_ips.keys())[0]
        vlan_1_name = "Vlan3"
        vlan_1_id = 3
        vlan_2_name = "Vlan4"
        vlan_2_id = 4

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
                "description": "Test_Vlan2",
            },
        ]

        response = self.put_req(
            "vlan_config",
            req_payload,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Testing whether vlans are added or not
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlanid"], vlan_1_id)
        self.assertEqual(response.json()["name"], vlan_1_name)
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_2_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlanid"], vlan_2_id)
        self.assertEqual(response.json()["name"], vlan_2_name)

        # adding stp config
        device_ip = list(self.device_ips.keys())[0]
        stp_global_request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096
        }

        # deleting stp global config
        self.perform_delete_stp_global(request_body=stp_global_request_body)

        # adding stp global config
        self.perform_add_stp_global(request_body=stp_global_request_body)

        # adding stp vlan
        request_body = [
            {
                "mgt_ip": device_ip,
                "vlan_id": vlan_1_id,
            },
            {
                "mgt_ip": device_ip,
                "vlan_id": vlan_2_id,
            },
        ]

        response = self.put_req("stp_vlan_config", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # validating stp vlan
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlan_id"], vlan_1_id)

        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_2_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlan_id"], vlan_2_id)

        # clean up

        # deleting vlans
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_2_name}
        )
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_2_name}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # checking stp vlan config
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_2_id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # deleting stp global config
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_vlan_bridge_priority(self):
        device_ip = list(self.device_ips.keys())[0]
        vlan_1_name = "Vlan3"
        vlan_1_id = 3

        req_payload = [
            {
                "mgt_ip": device_ip,
                "name": vlan_1_name,
                "vlanid": vlan_1_id,
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

        # Testing whether vlans are added or not
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlanid"], vlan_1_id)
        self.assertEqual(response.json()["name"], vlan_1_name)

        # adding stp config
        device_ip = list(self.device_ips.keys())[0]
        stp_global_request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096
        }

        # deleting stp global config
        self.perform_delete_stp_global(request_body=stp_global_request_body)

        # adding stp global config
        self.perform_add_stp_global(request_body=stp_global_request_body)

        # adding stp vlan
        request_body = [
            {
                "mgt_ip": device_ip,
                "vlan_id": vlan_1_id,
                "bridge_priority": 4096
            },
        ]

        response = self.put_req("stp_vlan_config", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # validating stp vlan
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlan_id"], vlan_1_id)
        self.assertEqual(response.json()["bridge_priority"], 4096)

        # updating stp vlan

        request_body = [
            {
                "mgt_ip": device_ip,
                "vlan_id": vlan_1_id,
                "bridge_priority": 4096 * 2
            },
        ]

        response = self.put_req("stp_vlan_config", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # validating stp vlan
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlan_id"], vlan_1_id)
        self.assertEqual(response.json()["bridge_priority"], 4096 * 2)

        # clean up

        # deleting vlans
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # checking stp vlan config
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # deleting stp global config
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_vlan_forwarding_delay(self):
        device_ip = list(self.device_ips.keys())[0]
        vlan_1_name = "Vlan3"
        vlan_1_id = 3

        req_payload = [
            {
                "mgt_ip": device_ip,
                "name": vlan_1_name,
                "vlanid": vlan_1_id,
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

        # Testing whether vlans are added or not
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlanid"], vlan_1_id)
        self.assertEqual(response.json()["name"], vlan_1_name)

        # adding stp config
        device_ip = list(self.device_ips.keys())[0]
        stp_global_request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096
        }

        # deleting stp global config
        self.perform_delete_stp_global(request_body=stp_global_request_body)

        # adding stp global config
        self.perform_add_stp_global(request_body=stp_global_request_body)

        # adding stp vlan
        request_body = [
            {
                "mgt_ip": device_ip,
                "vlan_id": vlan_1_id,
                "forwarding_delay": 20
            },
        ]

        response = self.put_req("stp_vlan_config", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # validating stp vlan
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlan_id"], vlan_1_id)
        self.assertEqual(response.json()["forwarding_delay"], 20)

        # updating stp vlan

        request_body = [
            {
                "mgt_ip": device_ip,
                "vlan_id": vlan_1_id,
                "forwarding_delay": 21
            },
        ]

        response = self.put_req("stp_vlan_config", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # validating stp vlan
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlan_id"], vlan_1_id)
        self.assertEqual(response.json()["forwarding_delay"], 21)

        # clean up

        # deleting vlans
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # checking stp vlan config
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # deleting stp global config
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_vlan_hello_time(self):
        device_ip = list(self.device_ips.keys())[0]
        vlan_1_name = "Vlan3"
        vlan_1_id = 3

        req_payload = [
            {
                "mgt_ip": device_ip,
                "name": vlan_1_name,
                "vlanid": vlan_1_id,
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

        # Testing whether vlans are added or not
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlanid"], vlan_1_id)
        self.assertEqual(response.json()["name"], vlan_1_name)

        # adding stp config
        device_ip = list(self.device_ips.keys())[0]
        stp_global_request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096
        }

        # deleting stp global config
        self.perform_delete_stp_global(request_body=stp_global_request_body)

        # adding stp global config
        self.perform_add_stp_global(request_body=stp_global_request_body)

        # adding stp vlan
        request_body = [
            {
                "mgt_ip": device_ip,
                "vlan_id": vlan_1_id,
                "hello_time": 9
            },
        ]

        response = self.put_req("stp_vlan_config", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # validating stp vlan
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlan_id"], vlan_1_id)
        self.assertEqual(response.json()["hello_time"], 9)

        # updating stp vlan

        request_body = [
            {
                "mgt_ip": device_ip,
                "vlan_id": vlan_1_id,
                "hello_time": 2
            },
        ]

        response = self.put_req("stp_vlan_config", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # validating stp vlan
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlan_id"], vlan_1_id)
        self.assertEqual(response.json()["hello_time"], 2)

        # clean up

        # deleting vlans
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # checking stp vlan config
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # deleting stp global config
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_vlan_max_age(self):
        device_ip = list(self.device_ips.keys())[0]
        vlan_1_name = "Vlan3"
        vlan_1_id = 3

        req_payload = [
            {
                "mgt_ip": device_ip,
                "name": vlan_1_name,
                "vlanid": vlan_1_id,
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

        # Testing whether vlans are added or not
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlanid"], vlan_1_id)
        self.assertEqual(response.json()["name"], vlan_1_name)

        # adding stp config
        device_ip = list(self.device_ips.keys())[0]
        stp_global_request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096
        }

        # deleting stp global config
        self.perform_delete_stp_global(request_body=stp_global_request_body)

        # adding stp global config
        self.perform_add_stp_global(request_body=stp_global_request_body)

        # adding stp vlan
        request_body = [
            {
                "mgt_ip": device_ip,
                "vlan_id": vlan_1_id,
                "max_age": 11
            },
        ]

        response = self.put_req("stp_vlan_config", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # validating stp vlan
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlan_id"], vlan_1_id)
        self.assertEqual(response.json()["max_age"], 11)

        # updating stp vlan

        request_body = [
            {
                "mgt_ip": device_ip,
                "vlan_id": vlan_1_id,
                "max_age": 20
            },
        ]

        response = self.put_req("stp_vlan_config", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # validating stp vlan
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlan_id"], vlan_1_id)
        self.assertEqual(response.json()["max_age"], 20)

        # clean up

        # deleting vlans
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # checking stp vlan config
        response = self.get_req("stp_vlan_config", {"mgt_ip": device_ip, "vlan_id": vlan_1_id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # deleting stp global config
        self.perform_delete_stp_global(request_body=stp_global_request_body)