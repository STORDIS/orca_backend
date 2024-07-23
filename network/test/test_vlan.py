"""
This module contains tests for the Interface API.
"""

from rest_framework import status
from network.test.test_common import TestORCA
from orca_nw_lib.common import IFMode


class TestVlan(TestORCA):
    """
    Test the VLAN API.
    """

    vlan_id = 1
    vlan_name = "Vlan1"
    portchnl_1 = "PortChannel101"
    portchnl_2 = "PortChannel102"


    def test_vlan_ip_config(self):
        
        device_ip = self.device_ips[0]

        # create Vlan
        req_payload = {
            "mgt_ip": device_ip,
            "name": self.vlan_name,
            "vlanid": self.vlan_id,
            "mtu": 9000,
            "enabled": False,
            "description": "Test_Vlan1",
            "ip_address": "202.20.20.20/24",
            "autostate": "enable",
        }

        self.create_vlan(req_payload)
        
        # update ip address
        req_payload_update_ip = {
            "mgt_ip": device_ip,
            "name": self.vlan_name,
            "ip_address": "101.10.10.10/10",
        }
        response = self.put_req("vlan_config", req_payload_update_ip)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check updated ip and other fields
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": req_payload["name"]}
        )
        self.assertEqual(response.json()["name"], req_payload["name"])
        self.assertEqual(response.json()["vlanid"], req_payload["vlanid"])
        self.assertEqual(response.json()["mtu"], req_payload["mtu"])
        self.assertEqual(response.json()["enabled"], req_payload["enabled"])
        self.assertEqual(response.json()["description"], req_payload["description"])
        self.assertEqual(response.json()["autostate"], req_payload["autostate"])
        self.assertEqual(
            response.json()["ip_address"], req_payload_update_ip["ip_address"]
        )

        ## remove ip_address
        req_payload_remove_ip = {
            "mgt_ip": device_ip,
            "name": self.vlan_name,
        }
        response = self.del_req("vlan_ip_remove", req_payload_remove_ip)

        # after deletion check if ip is deleted and other params are unchanged
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": req_payload["name"]}
        )
        self.assertEqual(response.json()["name"], req_payload["name"])
        self.assertEqual(response.json()["vlanid"], req_payload["vlanid"])
        self.assertEqual(response.json()["mtu"], req_payload["mtu"])
        self.assertEqual(response.json()["enabled"], req_payload["enabled"])
        self.assertEqual(response.json()["description"], req_payload["description"])
        self.assertEqual(response.json()["autostate"], req_payload["autostate"])
        self.assertFalse(response.json().get("ip_address"))

        #clean up
        self.delete_vlan(req_payload)
    def test_vlan_sag_ip_config(self):
        device_ip = self.device_ips[0]

        # create Vlan
        req_payload = {
            "mgt_ip": device_ip,
            "name": self.vlan_name,
            "vlanid": self.vlan_id,
            "mtu": 9000,
            "enabled": False,
            "description": "Test_Vlan1",
            "autostate": "enable",
        }
        self.create_vlan(req_payload)
        
        sag_ip_1 = "101.10.10.10/10"
        sag_ip_2 = "201.20.20.20/20"
        sag_ip_3 = "202.30.30.30/30"
        # Now assign sag_ip
        req_payload_assign_ip = {
            "mgt_ip": device_ip,
            "name": self.vlan_name,
            "sag_ip_address": [sag_ip_1],
        }
        response = self.put_req("vlan_config", req_payload_assign_ip)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ## Verify sag_ip_address
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.json()["name"], self.vlan_name)
        self.assertEqual(response.json()["vlanid"], self.vlan_id)
        self.assertEqual(response.json()["sag_ip_address"], [sag_ip_1])
        self.assertEqual(response.json()["mtu"], req_payload["mtu"])
        self.assertEqual(response.json()["enabled"], req_payload["enabled"])
        self.assertEqual(response.json()["description"], req_payload["description"])
        self.assertEqual(response.json()["autostate"], req_payload["autostate"])

        # update sag ip
        req_payload_update_assign_ip = {
            "mgt_ip": device_ip,
            "name": self.vlan_name,
            "sag_ip_address": [sag_ip_2, sag_ip_3],
        }
        response = self.put_req("vlan_config", req_payload_update_assign_ip)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ## Verify sag_ip_address
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": req_payload["name"]}
        )
        self.assertEqual(response.json()["name"], req_payload["name"])
        self.assertEqual(response.json()["vlanid"], req_payload["vlanid"])
        self.assertEqual(
            response.json()["sag_ip_address"], [sag_ip_1, sag_ip_2, sag_ip_3]
        )
        self.assertEqual(response.json()["mtu"], req_payload["mtu"])
        self.assertEqual(response.json()["enabled"], req_payload["enabled"])
        self.assertEqual(response.json()["description"], req_payload["description"])
        self.assertEqual(response.json()["autostate"], req_payload["autostate"])

        # remove sag_ip
        req_payload_remove_sag_ip = {
            "mgt_ip": device_ip,
            "name": self.vlan_name,
            "sag_ip_address": [sag_ip_1,sag_ip_2, sag_ip_3],
        }
        response = self.del_req("vlan_ip_remove", req_payload_remove_sag_ip)

        # after deletion checking other params and sag ip is removed
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": req_payload["name"]}
        )
        self.assertEqual(response.json()["name"], req_payload["name"])
        self.assertEqual(response.json()["vlanid"], req_payload["vlanid"])
        self.assertEqual(response.json()["mtu"], req_payload["mtu"])
        self.assertEqual(response.json()["enabled"], req_payload["enabled"])
        self.assertEqual(response.json()["description"], req_payload["description"])
        self.assertEqual(response.json()["autostate"], req_payload["autostate"])
        self.assertFalse(response.json()["sag_ip_address"])

        # remove all sag_ip
        req_payload_remove_sag_ip_all = {
            "mgt_ip": device_ip,
            "name": self.vlan_name,
        }
        response = self.del_req("vlan_ip_remove", req_payload_remove_sag_ip_all)

        # after deletion checking other params and sag ip is removed
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": req_payload["name"]}
        )
        self.assertEqual(response.json()["name"], req_payload["name"])
        self.assertEqual(response.json()["vlanid"], req_payload["vlanid"])
        self.assertFalse(response.json()["sag_ip_address"])
        self.assertEqual(response.json()["mtu"], req_payload["mtu"])
        self.assertEqual(response.json()["enabled"], req_payload["enabled"])
        self.assertEqual(response.json()["description"], req_payload["description"])
        self.assertEqual(response.json()["autostate"], req_payload["autostate"])

        #clean up
        self.delete_vlan(req_payload)
    def test_vlan_description(self):
        device_ip = self.device_ips[0]

        # create Vlan
        req_payload = {
            "mgt_ip": device_ip,
            "name": self.vlan_name,
            "vlanid": self.vlan_id,
            "mtu": 9000,
            "enabled": False,
            "description": "Test_Vlan1",
            "ip_address": "20.20.20.20/24",
            "autostate": "enable",
        }
        self.create_vlan(req_payload)
        
        # remove description
        req_payload_remove_description = {
            "mgt_ip": device_ip,
            "name": self.vlan_name,
            "description": "",
        }

        response = self.put_req(
            "vlan_config",
            req_payload_remove_description,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check if description is "" and other values are un altered
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.json()["name"], self.vlan_name)
        self.assertEqual(response.json()["vlanid"], self.vlan_id)
        self.assertEqual(response.json()["mtu"], req_payload["mtu"])
        self.assertEqual(response.json()["enabled"], req_payload["enabled"])
        self.assertEqual(response.json()["description"], None)
        self.assertEqual(response.json()["autostate"], req_payload["autostate"])
        
         #clean up
        self.delete_vlan(req_payload)
        
    def test_vlan_mem_config(self):
        """
        Test the VLAN memory configuration.

        This function performs a series of tests on the VLAN memory configuration. It verifies
        that the configuration can be deleted, retrieved, modified, and deleted again without
        any errors or inconsistencies.

        Parameters:
            self (object): The instance of the test class.

        Returns:
            None
        """
        self.create_sample_vlan_and_member_config(self.get_req_body())
        self.cleanup_vlan_mem_and_config(self.get_req_body())

    def cleanup_vlan_mem_and_config(self, request_body):
        device_ip = request_body["mgt_ip"]
        # Delete VLAN members.
        response = self.del_req("vlan_mem_delete", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Confirm deletion of VLAN members.
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            set(response.json()["mem_ifs"]) & set(request_body["mem_ifs"].keys())
        )

        ## Delete VLAN
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )

        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

    def create_sample_vlan_and_member_config(self, request_body):
        """
        Almost similar to other test cases just that this test ase doesn't cleanup the config.
        """
        device_ip = request_body["mgt_ip"]
        ether_1 = list(request_body.get("mem_ifs").keys())[0]
        ether_2 = list(request_body.get("mem_ifs").keys())[1]

        # Remove Vlan from Interfaces.
        self.del_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_1, "ifmode": "ACCESS"},
        )
        self.del_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_1, "ifmode": "TRUNK"},
        )
        self.del_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_2, "ifmode": "ACCESS"},
        )
        self.del_req(
            "device_interface_list",
            {"mgt_ip": device_ip, "name": ether_2, "ifmode": "TRUNK"},
        )

        # Delete VLAN members.
        response = self.del_req("vlan_mem_delete", request_body)

        self.assertTrue(
            response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )
        # Confirm deletion of VLAN members.
        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertTrue(
            response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )

        # Now delete VLAN
        response = self.del_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )

        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in response.json()["result"]
                if res != "\n"
            )
        )

        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(response.data)

        ## Now cleanup port channels as well
        # Bur before First delete mclag, if it exists.
        # port channel deletion will fail if port channel is found to be a member of mclag.
        self.remove_mclag(device_ip)
        ## Now actually delete portchannel
        request_body_port_chnl = [
            {"mgt_ip": device_ip, "lag_name": self.portchnl_1},
            {"mgt_ip": device_ip, "lag_name": self.portchnl_2},
        ]
        self.perform_del_port_chnl(request_body_port_chnl)
        self.perform_add_port_chnl(request_body_port_chnl)

        response = self.put_req(
            "vlan_config",
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(response.json()["name"], self.vlan_name)
        self.assertEqual(response.json()["vlanid"], self.vlan_id)
        self.assertTrue(
            all(
                True if m in response.json()["mem_ifs"] else False
                for m in response.json()["mem_ifs"]
            )
        )
        self.assertEqual(
            response.json()["mem_ifs"][ether_1],
            str(IFMode.get_enum_from_str(request_body["mem_ifs"][self.ether_names[0]])),
        )
        self.assertEqual(
            response.json()["mem_ifs"][ether_2],
            str(IFMode.get_enum_from_str(request_body["mem_ifs"][self.ether_names[1]])),
        )
        self.assertEqual(
            response.json()["mem_ifs"][self.portchnl_1],
            str(IFMode.get_enum_from_str(request_body["mem_ifs"][self.portchnl_1])),
        )
        self.assertEqual(
            response.json()["mem_ifs"][self.portchnl_2],
            str(IFMode.get_enum_from_str(request_body["mem_ifs"][self.portchnl_2])),
        )

    def get_req_body(self):
        return {
            "mgt_ip": self.device_ips[0],
            "name": self.vlan_name,
            "vlanid": self.vlan_id,
            "mem_ifs": {
                self.ether_names[0]: "TRUNK",
                self.ether_names[1]: "ACCESS",
                self.portchnl_1: "TRUNK",
                self.portchnl_2: "ACCESS",
            },
        }

    def test_vlan_member_if_mode_update(self):
        device_ip = self.device_ips[0]
        request_body = self.get_req_body()
        self.create_sample_vlan_and_member_config(request_body)

        # Testing Valn member if mode update

        request_body["mem_ifs"][self.ether_names[0]] = "ACCESS"
        request_body["mem_ifs"][self.ether_names[1]] = "TRUNK"
        request_body["mem_ifs"][self.portchnl_1] = "ACCESS"
        request_body["mem_ifs"][self.portchnl_2] = "TRUNK"

        response = self.put_req(
            "vlan_config",
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(
            response.json()["mem_ifs"][self.ether_names[0]],
            str(IFMode.get_enum_from_str(request_body["mem_ifs"][self.ether_names[0]])),
        )
        self.assertEqual(
            response.json()["mem_ifs"][self.ether_names[1]],
            str(IFMode.get_enum_from_str(request_body["mem_ifs"][self.ether_names[1]])),
        )
        self.assertEqual(
            response.json()["mem_ifs"][self.portchnl_1],
            str(IFMode.get_enum_from_str(request_body["mem_ifs"][self.portchnl_1])),
        )
        self.assertEqual(
            response.json()["mem_ifs"][self.portchnl_2],
            str(IFMode.get_enum_from_str(request_body["mem_ifs"][self.portchnl_2])),
        )

        # Testing update again

        request_body["mem_ifs"][self.ether_names[0]] = "TRUNK"
        request_body["mem_ifs"][self.ether_names[1]] = "ACCESS"
        request_body["mem_ifs"][self.portchnl_1] = "TRUNK"
        request_body["mem_ifs"][self.portchnl_2] = "ACCESS"

        response = self.put_req(
            "vlan_config",
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_req(
            "vlan_config", {"mgt_ip": device_ip, "name": self.vlan_name}
        )
        self.assertEqual(
            response.json()["mem_ifs"][self.ether_names[0]],
            str(IFMode.get_enum_from_str(request_body["mem_ifs"][self.ether_names[0]])),
        )
        self.assertEqual(
            response.json()["mem_ifs"][self.ether_names[1]],
            str(IFMode.get_enum_from_str(request_body["mem_ifs"][self.ether_names[1]])),
        )
        self.assertEqual(
            response.json()["mem_ifs"][self.portchnl_1],
            str(IFMode.get_enum_from_str(request_body["mem_ifs"][self.portchnl_1])),
        )
        self.assertEqual(
            response.json()["mem_ifs"][self.portchnl_2],
            str(IFMode.get_enum_from_str(request_body["mem_ifs"][self.portchnl_2])),
        )

        # Cleanup
        self.cleanup_vlan_mem_and_config(request_body)
