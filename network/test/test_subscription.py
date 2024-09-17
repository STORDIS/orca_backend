from orca_nw_lib.device_gnmi import get_device_state_url
from orca_nw_lib.portgroup_gnmi import _get_port_groups_base_path

from orca_nw_lib.interface_gnmi import get_interface_base_path, get_intfc_config_path

from network.test.test_common import TestORCA
from orca_nw_lib.gnmi_sub import gnmi_subscribe, get_subscription_path_for_config_change, sync_response_received, \
    get_running_thread_names, get_subscription_thread_name
from orca_nw_lib.stp_port_gnmi import get_stp_port_path


class TestSubscription(TestORCA):

    def test_subscription(self):
        device_ip = list(self.device_ips.keys())[0]

        # Check if subscription is successful
        self.assertTrue(gnmi_subscribe(device_ip))

        # checking if all paths are subscribed
        subscription_paths = get_subscription_path_for_config_change(device_ip)
        expected_subscription_paths = [
            get_interface_base_path().elem[0].name,
            _get_port_groups_base_path().elem[0].name,
            get_stp_port_path().elem[0].name,
            get_device_state_url().elem[0].name
        ]
        for path in subscription_paths:
            self.assertTrue(path.path.elem[0].name in expected_subscription_paths)

        # Check if subscription is successful
        running_threads = get_running_thread_names()
        self.assertIn(get_subscription_thread_name(device_ip), running_threads)

        # Check if sync response is received
        self.assert_until_condition_met(
            sync_response_received,
            True,
            device_ip
        )
