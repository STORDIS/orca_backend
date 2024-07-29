from rest_framework import status

from network.test.test_common import TestORCA


class TestSTP(TestORCA):
    """
    This module contains tests for the STP API.
    """

    def test_stp_global_config(self):
        """
        Test stp global config on device.
        """
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096
        }

        # delete stp config if it exists
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

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

        # testing updated values
        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": False,
            "forwarding_delay": 5,
            "hello_time": 5,
            "max_age": 20,
            "bridge_priority": 4096 * 2
        }

        # update stp config
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

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

    def test_stp_global_additional_parm_rootguard_timeout_test(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096,
            "rootguard_timeout": 10
        }

        # delete stp config if it exists
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

        # create stp config
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["rootguard_timeout"], response_body["rootguard_timeout"])
        self.assertEqual(request_body["enabled_protocol"], response_body["enabled_protocol"])
        self.assertEqual(request_body["bpdu_filter"], response_body["bpdu_filter"])
        self.assertEqual(request_body["hello_time"], response_body["hello_time"])
        self.assertEqual(request_body["max_age"], response_body["max_age"])
        self.assertEqual(request_body["forwarding_delay"], response_body["forwarding_delay"])
        self.assertEqual(request_body["bridge_priority"], response_body["bridge_priority"])

        # updating rootguard timeout config

        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096,
            "rootguard_timeout": 20
        }

        # update stp config
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["rootguard_timeout"], response_body["rootguard_timeout"])

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

    def test_stp_global_additional_parm_port_fast_test(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096,
            "portfast": True
        }

        # delete stp config if it exists
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

        # create stp config
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["portfast"], response_body["portfast"])
        self.assertEqual(request_body["enabled_protocol"], response_body["enabled_protocol"])
        self.assertEqual(request_body["bpdu_filter"], response_body["bpdu_filter"])
        self.assertEqual(request_body["hello_time"], response_body["hello_time"])
        self.assertEqual(request_body["max_age"], response_body["max_age"])
        self.assertEqual(request_body["forwarding_delay"], response_body["forwarding_delay"])
        self.assertEqual(request_body["bridge_priority"], response_body["bridge_priority"])

        # updating port fast config

        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096,
            "portfast": False
        }

        # update stp config
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["portfast"], response_body["portfast"])

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

    def test_stp_global_additional_parm_loop_guard_test(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["MSTP"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096,
            "loop_guard": False
        }

        # delete stp config if it exists
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

        # create stp config
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["loop_guard"], response_body["loop_guard"])
        self.assertEqual(request_body["enabled_protocol"], response_body["enabled_protocol"])
        self.assertEqual(request_body["bpdu_filter"], response_body["bpdu_filter"])
        self.assertEqual(request_body["hello_time"], response_body["hello_time"])
        self.assertEqual(request_body["max_age"], response_body["max_age"])
        self.assertEqual(request_body["forwarding_delay"], response_body["forwarding_delay"])
        self.assertEqual(request_body["bridge_priority"], response_body["bridge_priority"])

        # updating loop guard config

        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["MSTP"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096,
            "loop_guard": True
        }

        # update stp config
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["loop_guard"], response_body["loop_guard"])

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

    def test_stp_global_additional_parm_disabled_vlans_test(self):
        device_ip = self.device_ips[0]

        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "disabled_vlans": [100, 200],
            "bridge_priority": 4096
        }

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

        # create stp config
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["disabled_vlans"], response_body["disabled_vlans"])
        self.assertEqual(request_body["enabled_protocol"], response_body["enabled_protocol"])
        self.assertEqual(request_body["bpdu_filter"], response_body["bpdu_filter"])
        self.assertEqual(request_body["hello_time"], response_body["hello_time"])
        self.assertEqual(request_body["max_age"], response_body["max_age"])
        self.assertEqual(request_body["forwarding_delay"], response_body["forwarding_delay"])
        self.assertEqual(request_body["bridge_priority"], response_body["bridge_priority"])

        # updating disabled vlans

        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "disabled_vlans": [300],
            "bridge_priority": 4096
        }

        # update stp config
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertTrue(300 in response_body["disabled_vlans"])

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

    def test_stp_global_deleted_disabled_vlans(self):
        device_ip = self.device_ips[0]
        vlan_1_name = "Vlan3"
        vlan_1_id = 3
        vlan_2_name = "Vlan4"
        vlan_2_id = 4
        vlan_3_name = "Vlan5"
        vlan_3_id = 5

        # deleting vlans from device to test disabled vlans.
        # vlan not in device can be added as disabled vlans
        response = self.del_req("vlan_config", {"mgt_ip": device_ip, "name": vlan_2_name})
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req("vlan_config", {"mgt_ip": device_ip, "name": vlan_2_name})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.del_req("vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name})
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req("vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.del_req("vlan_config", {"mgt_ip": device_ip, "name": vlan_3_name})
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )
        response = self.get_req("vlan_config", {"mgt_ip": device_ip, "name": vlan_3_name})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "disabled_vlans": [vlan_1_id, vlan_2_id, vlan_3_id],
            "bridge_priority": 4096
        }

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

        # create stp config
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["disabled_vlans"], response_body["disabled_vlans"])
        self.assertEqual(request_body["enabled_protocol"], response_body["enabled_protocol"])
        self.assertEqual(request_body["bpdu_filter"], response_body["bpdu_filter"])
        self.assertEqual(request_body["hello_time"], response_body["hello_time"])
        self.assertEqual(request_body["max_age"], response_body["max_age"])
        self.assertEqual(request_body["forwarding_delay"], response_body["forwarding_delay"])
        self.assertEqual(request_body["bridge_priority"], response_body["bridge_priority"])

        # configuring disabled vlans to delete disabled vlans
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
            }
        ]

        response = self.put_req(
            "vlan_config",
            req_payload,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Testing whether vlans are added or not
        response = self.get_req("vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlanid"], vlan_1_id)
        self.assertEqual(response.json()["name"], vlan_1_name)
        response = self.get_req("vlan_config", {"mgt_ip": device_ip, "name": vlan_2_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["vlanid"], vlan_2_id)
        self.assertEqual(response.json()["name"], vlan_2_name)

        response_body = {
            "mgt_ip": device_ip,
            "disabled_vlans": [vlan_1_id, vlan_2_id],
        }

        # Test deleting diabled_vlans
        response = self.del_req("stp_delete_disabled_vlans", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", response_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response_body = response.json()[0]
        self.assertTrue(vlan_3_id in response_body["disabled_vlans"])
        self.assertTrue(vlan_1_id not in response_body["disabled_vlans"])
        self.assertTrue(vlan_2_id not in response_body["disabled_vlans"])

        # clean up
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_2_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req("vlan_config", {"mgt_ip": device_ip, "name": vlan_2_name})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.get_req("vlan_config", {"mgt_ip": device_ip, "name": vlan_1_name})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

    def test_stp_global_bpdu_filter(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096
        }

        # delete stp config if it exists
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

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

        # update bpdu filter to false
        request_body["bpdu_filter"] = False
        request_body = {
            "mgt_ip": device_ip,
            "bpdu_filter": False,
        }
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["bpdu_filter"], response_body["bpdu_filter"])

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

    def test_stp_global_bridge_priority(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096
        }

        # delete stp config if it exists
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

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

        # update bridge priority to 4096*2
        request_body = {
            "mgt_ip": device_ip,
            "bridge_priority": 4096 * 2,
        }
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]

        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["bridge_priority"], response_body["bridge_priority"])

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

    def test_stp_global_max_age(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096
        }

        # delete stp config if it exists
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

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

        # update max age to 20
        request_body = {
            "mgt_ip": device_ip,
            "max_age": 20,
        }
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]

        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["max_age"], response_body["max_age"])

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

    def test_stp_gloabl_hello_time(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096
        }

        # delete stp config if it exists
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

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

        # update hello time to 6
        request_body = {
            "mgt_ip": device_ip,
            "hello_time": 6,
        }
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]

        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["hello_time"], response_body["hello_time"])

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

    def test_stp_global_forwarding_delay(self):
        device_ip = self.device_ips[0]
        request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["PVST"],
            "bpdu_filter": True,
            "forwarding_delay": 10,
            "hello_time": 10,
            "max_age": 10,
            "bridge_priority": 4096
        }

        # delete stp config if it exists
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)

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

        # update forwarding delay to 25
        request_body = {
            "mgt_ip": device_ip,
            "forwarding_delay": 25,
        }
        response = self.put_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        response = self.get_req("stp_config", request_body)
        response_body = response.json()[0]

        self.assertTrue(response.status_code == status.HTTP_200_OK)
        self.assertEqual(request_body["forwarding_delay"], response_body["forwarding_delay"])

        # delete stp config
        response = self.del_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)

        # get stp config
        response = self.get_req("stp_config", request_body)
        self.assertTrue(response.status_code == status.HTTP_204_NO_CONTENT)
