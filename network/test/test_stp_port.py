import time

from rest_framework import status

from network.test.test_common import TestORCA


class TestSTPPort(TestORCA):
    """
    This module contains tests for the STP API.
    """

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

    def perform_add_stp_port(self, request_body):

        response = self.put_req("stp_port", request_body)
        self.assertTrue(response.status_code == status.HTTP_200_OK)
        for i in request_body if isinstance(request_body, list) else [request_body]:
            # Call with timeout because subscription response isn't recevied in time.
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "stp_port",
                i,
                status=status.HTTP_200_OK,
                if_name=i["if_name"],
                stp_enabled=i["stp_enabled"],
                bpdu_guard=i["bpdu_guard"],
                uplink_fast=i["uplink_fast"],
            )

    def perform_delete_stp_port(self, request_body):
        while True:
            del_response = self.del_req("stp_port", request_body)
            if any(
                "device is not ready to receive gnmi updates" in res.get("message", "").lower()
                for res in del_response.json()["result"]
                if res != "\n"
            ):
                time.sleep(5)
            else:
                break

        self.assertTrue(
            del_response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower()
                for res in del_response.json()["result"]
                if res != "\n"
            )
        )

        self.assert_with_timeout_retry(
            lambda path, payload: self.get_req(path, payload),
            "stp_port",
            request_body,
            status=status.HTTP_204_NO_CONTENT,
        )

    def test_stp_port_config(self):
        device_ip = self.device_ips[0]

        # adding interface member
        ether_1 = self.ether_names[0]
        itf_request_body = [
            {
                "mgt_ip": device_ip,
                "name": ether_1,
                "mtu": 9100,
            },
        ]
        self.assert_with_timeout_retry(
            lambda path, payload: self.put_req(path, payload),
            "device_interface_list",
            itf_request_body,
            status=status.HTTP_200_OK,
        )

        # adding port channel
        port_channel_1 = "PortChannel104"
        port_channel_request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel_1,
            "mtu": 9100,
            "admin_status": "up"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel_1})

        # adding port channel
        self.perform_add_port_chnl([port_channel_request_body])

        # adding stp config
        device_ip = self.device_ips[0]
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

        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
            },
            {
                "mgt_ip": device_ip,
                "if_name": ether_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
            },
        ]

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)

        # testing adding stp port config
        self.perform_add_stp_port(request_body=request_body)

        # clean up
        response = self.del_req("device_interface_list", itf_request_body)
        self.assertTrue(
            response.status_code == status.HTTP_200_OK
            or any(
                "resource not found" in res.get("message", "").lower() for res in response.json()["result"]
                if res != "\n"
            )
        )

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)
        self.perform_del_port_chnl(request_body=port_channel_request_body)
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_port_bpdu_guard(self):
        device_ip = self.device_ips[0]

        # adding port channel
        port_channel_1 = "PortChannel104"
        port_channel_request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel_1,
            "mtu": 9100,
            "admin_status": "up"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel_1})

        # adding port channel
        self.perform_add_port_chnl([port_channel_request_body])

        # adding stp config
        device_ip = self.device_ips[0]
        stp_global_request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["MSTP"],
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

        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
            }
        ]

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)

        # testing adding stp port config
        self.perform_add_stp_port(request_body=request_body)

        # update bpdu guard to false
        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": False,
                "uplink_fast": True,
                "stp_enabled": True,
            }
        ]
        response = self.put_req("stp_port", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "stp_port",
                i,
                status=status.HTTP_200_OK,
                bpdu_guard=i["bpdu_guard"],
                if_name=i["if_name"],
            )

        # clean up
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)
        self.perform_del_port_chnl(request_body=port_channel_request_body)
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_port_bpdu_filter(self):
        device_ip = self.device_ips[0]

        # adding port channel
        port_channel_1 = "PortChannel104"
        port_channel_request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel_1,
            "mtu": 9100,
            "admin_status": "up"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel_1})

        # adding port channel
        self.perform_add_port_chnl([port_channel_request_body])

        # adding stp config
        device_ip = self.device_ips[0]
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

        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
            }
        ]

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)

        # testing adding stp port config
        self.perform_add_stp_port(request_body=request_body)

        # update bpdu filter to false
        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_filter": False,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
            }
        ]
        response = self.put_req("stp_port", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "stp_port",
                i,
                status=status.HTTP_200_OK,
                bpdu_filter=i["bpdu_filter"],
                if_name=i["if_name"],
            )

        # clean up
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)
        self.perform_del_port_chnl(request_body=port_channel_request_body)
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_port_portfast(self):
        device_ip = self.device_ips[0]

        # adding port channel
        port_channel_1 = "PortChannel104"
        port_channel_request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel_1,
            "mtu": 9100,
            "admin_status": "up"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel_1})

        # adding port channel
        self.perform_add_port_chnl([port_channel_request_body])

        # adding stp config
        device_ip = self.device_ips[0]
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

        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
                "portfast": True
            }
        ]

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)

        # testing adding stp port config
        self.perform_add_stp_port(request_body=request_body)

        # update portfast to false
        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "portfast": False,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
            }
        ]
        response = self.put_req("stp_port", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "stp_port",
                i,
                status=status.HTTP_200_OK,
                portfast=i["portfast"],
                if_name=i["if_name"],
            )

        # clean up
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)
        self.perform_del_port_chnl(request_body=port_channel_request_body)
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_port_uplink_fast(self):
        device_ip = self.device_ips[0]

        # adding port channel
        port_channel_1 = "PortChannel104"
        port_channel_request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel_1,
            "mtu": 9100,
            "admin_status": "up"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel_1})

        # adding port channel
        self.perform_add_port_chnl([port_channel_request_body])

        # adding stp config
        device_ip = self.device_ips[0]
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

        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
            }
        ]

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)

        # testing adding stp port config
        self.perform_add_stp_port(request_body=request_body)

        # update uplink_fast to false
        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "uplink_fast": False,
                "bpdu_guard": True,
                "stp_enabled": True,
            }
        ]
        response = self.put_req("stp_port", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "stp_port",
                i,
                status=status.HTTP_200_OK,
                uplink_fast=i["uplink_fast"],
                if_name=i["if_name"],)

        # clean up
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)
        self.perform_del_port_chnl(request_body=port_channel_request_body)
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_port_stp_enabled(self):
        device_ip = self.device_ips[0]

        # adding port channel
        port_channel_1 = "PortChannel104"
        port_channel_request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel_1,
            "mtu": 9100,
            "admin_status": "up"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel_1})

        # adding port channel
        self.perform_add_port_chnl([port_channel_request_body])

        # adding stp config
        device_ip = self.device_ips[0]
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

        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
            }
        ]

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)

        # testing adding stp port config
        self.perform_add_stp_port(request_body=request_body)

        # update stp_enabled to false
        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "stp_enabled": False,
                "bpdu_guard": True,
                "uplink_fast": True,
            }
        ]
        response = self.put_req("stp_port", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "stp_port",
                i,
                status=status.HTTP_200_OK,
                stp_enabled=i["stp_enabled"],
                if_name=i["if_name"],
            )

        # clean up
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)
        self.perform_del_port_chnl(request_body=port_channel_request_body)
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_port_edge_port(self):
        device_ip = self.device_ips[0]

        # adding port channel
        port_channel_1 = "PortChannel104"
        port_channel_request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel_1,
            "mtu": 9100,
            "admin_status": "up"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel_1})

        # adding port channel
        self.perform_add_port_chnl([port_channel_request_body])

        # adding stp config
        device_ip = self.device_ips[0]
        stp_global_request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["MSTP"],
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

        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
                "edge_port": "EDGE_AUTO"
            }
        ]

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)

        # testing adding stp port config
        self.perform_add_stp_port(request_body=request_body)

        # update edge_port to EDGE_DISABLE
        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "edge_port": "EDGE_DISABLE",
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
            }
        ]
        response = self.put_req("stp_port", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "stp_port",
                i,
                status=status.HTTP_200_OK,
                if_name=i["if_name"],
                edge_port=i["edge_port"],
            )

        # clean up
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)
        self.perform_del_port_chnl(request_body=port_channel_request_body)
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_port_link_type(self):
        device_ip = self.device_ips[0]

        # adding port channel
        port_channel_1 = "PortChannel104"
        port_channel_request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel_1,
            "mtu": 9100,
            "admin_status": "up"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel_1})

        # adding port channel
        self.perform_add_port_chnl([port_channel_request_body])

        # adding stp config
        device_ip = self.device_ips[0]
        stp_global_request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["MSTP"],
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

        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
                "link_type": "P2P"
            }
        ]

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)

        # testing adding stp port config
        self.perform_add_stp_port(request_body=request_body)

        # update link_type to SHARED
        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
                "link_type": "SHARED"
            }
        ]
        response = self.put_req("stp_port", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "stp_port",
                i,
                status=status.HTTP_200_OK,
                if_name=i["if_name"],
                link_type=i["link_type"],
            )

        # clean up
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)
        self.perform_del_port_chnl(request_body=port_channel_request_body)
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_port_guard(self):
        device_ip = self.device_ips[0]

        # adding port channel
        port_channel_1 = "PortChannel104"
        port_channel_request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel_1,
            "mtu": 9100,
            "admin_status": "up"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel_1})

        # adding port channel
        self.perform_add_port_chnl([port_channel_request_body])

        # adding stp config
        device_ip = self.device_ips[0]
        stp_global_request_body = {
            "mgt_ip": device_ip,
            "enabled_protocol": ["MSTP"],
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

        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
                "guard": "ROOT"
            }
        ]

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)

        # testing adding stp port config
        self.perform_add_stp_port(request_body=request_body)

        # update guard to LOOP
        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "guard": "LOOP",
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,

            }
        ]
        response = self.put_req("stp_port", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "stp_port",
                i,
                status=status.HTTP_200_OK,
                if_name=i["if_name"],
                guard=i["guard"],
            )

        # clean up
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)
        self.perform_del_port_chnl(request_body=port_channel_request_body)
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_port_bpdu_guard_port_shutdown(self):
        device_ip = self.device_ips[0]

        # adding port channel
        port_channel_1 = "PortChannel104"
        port_channel_request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel_1,
            "mtu": 9100,
            "admin_status": "up"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel_1})

        # adding port channel
        self.perform_add_port_chnl([port_channel_request_body])

        # adding stp config
        device_ip = self.device_ips[0]
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

        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
                "bpdu_guard_port_shutdown": True
            }
        ]

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)

        # testing adding stp port config
        self.perform_add_stp_port(request_body=request_body)

        # update bpdu_guard_port_shutdown to False
        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard_port_shutdown": False,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
            }
        ]
        response = self.put_req("stp_port", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "stp_port",
                i,
                status=status.HTTP_200_OK,
                if_name=i["if_name"],
                bpdu_guard_port_shutdown=i["bpdu_guard_port_shutdown"],
            )

        # clean up
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)
        self.perform_del_port_chnl(request_body=port_channel_request_body)
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_port_cost(self):
        device_ip = self.device_ips[0]

        # adding port channel
        port_channel_1 = "PortChannel104"
        port_channel_request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel_1,
            "mtu": 9100,
            "admin_status": "up"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel_1})

        # adding port channel
        self.perform_add_port_chnl([port_channel_request_body])

        # adding stp config
        device_ip = self.device_ips[0]
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

        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
                "cost": 200
            }
        ]

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)

        # testing adding stp port config
        self.perform_add_stp_port(request_body=request_body)

        # update cost to 500
        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "cost": 500,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
            }
        ]
        response = self.put_req("stp_port", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "stp_port",
                i,
                status=status.HTTP_200_OK,
                if_name=i["if_name"],
                cost=i["cost"],
            )

        # clean up
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)
        self.perform_del_port_chnl(request_body=port_channel_request_body)
        self.perform_delete_stp_global(request_body=stp_global_request_body)

    def test_stp_port_port_priority(self):
        device_ip = self.device_ips[0]

        # adding port channel
        port_channel_1 = "PortChannel104"
        port_channel_request_body = {
            "mgt_ip": device_ip,
            "lag_name": port_channel_1,
            "mtu": 9100,
            "admin_status": "up"
        }
        self.perform_del_port_chnl({"mgt_ip": device_ip, "lag_name": port_channel_1})

        # adding port channel
        self.perform_add_port_chnl([port_channel_request_body])

        # adding stp config
        device_ip = self.device_ips[0]
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

        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
                "port_priority": 20
            }
        ]

        # deleting stp port config
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)

        # testing adding stp port config
        self.perform_add_stp_port(request_body=request_body)

        # update port priority to 50
        request_body = [
            {
                "mgt_ip": device_ip,
                "if_name": port_channel_1,
                "port_priority": 50,
                "bpdu_guard": True,
                "uplink_fast": True,
                "stp_enabled": True,
            }
        ]
        response = self.put_req("stp_port", request_body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in request_body:
            self.assert_with_timeout_retry(
                lambda path, payload: self.get_req(path, payload),
                "stp_port",
                i,
                status=status.HTTP_200_OK,
                if_name=i["if_name"],
                port_priority=i["port_priority"],
            )

        # clean up
        for i in request_body:
            self.perform_delete_stp_port(request_body=i)
        self.perform_del_port_chnl(request_body=port_channel_request_body)
        self.perform_delete_stp_global(request_body=stp_global_request_body)
