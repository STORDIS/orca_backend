import asyncio
import datetime
import time

import pytest
from django.urls import reverse
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from network.scheduler import scheduler
from state_manager.middleware import BlockPutMiddleware
from state_manager.models import State, OrcaState
from state_manager.test.test_common import TestCommon


@api_view(["PUT"])
@permission_classes([permissions.AllowAny])
def discovery_stub(request, client=None):
    response = client.get(reverse("orca_state", kwargs={"device_ip": "127.0.0.1"}), )
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("device_ip") == "127.0.0.1"
    assert response.json().get("state") == str(State.DISCOVERY_IN_PROGRESS)
    return Response({"result": [{"message": "testing", "status": "success"}]}, status=200)


@api_view(["PUT"])
@permission_classes([permissions.AllowAny])
def put_stub(request, client=None):
    response = client.get(reverse("orca_state", kwargs={"device_ip": "127.0.0.1"}), )
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("device_ip") == "127.0.0.1"
    assert response.json().get("state") == str(State.CONFIG_IN_PROGRESS)
    return Response({"result": [{"message": "testing", "status": "success"}]}, status=200)


@api_view(["PUT"])
@permission_classes([permissions.AllowAny])
def feature_discovery_stub(request, client=None):
    response = client.get(reverse("orca_state", kwargs={"device_ip": "127.0.0.1"}), )
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("device_ip") == "127.0.0.1"
    assert response.json().get("state") == str(State.FEATURE_DISCOVERY_IN_PROGRESS)
    return Response({"result": [{"message": "testing", "status": "success"}]}, status=200)


class TestState(TestCommon):

    def tearDown(self):
        OrcaState.objects.all().delete()

    @classmethod
    def tearDownClass(cls):
        if scheduler.running:
            scheduler.shutdown()

    def test_discovery_state(self):
        response = self.client.get(reverse("orca_state", kwargs={"device_ip": "127.0.0.1"}), )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        request = self.factory.put(path=reverse('discover'), data={"address": "127.0.0.1"}, format="json")
        middleware = BlockPutMiddleware(lambda req: discovery_stub(req, self.client))
        response = middleware(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("orca_state", kwargs={"device_ip": "127.0.0.1"}), )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("device_ip"), "127.0.0.1")
        self.assertEqual(response.json().get("state"), str(State.AVAILABLE))

    def test_feature_discovery_state(self):
        response = self.client.get(reverse("orca_state", kwargs={"device_ip": "127.0.0.1"}), )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        request = self.factory.put(path=reverse('discover_by_feature'), data={"mgt_ip": "127.0.0.1"}, format="json")
        middleware = BlockPutMiddleware(lambda req: feature_discovery_stub(req, self.client))
        response = middleware(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("orca_state", kwargs={"device_ip": "127.0.0.1"}), )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("device_ip"), "127.0.0.1")
        self.assertEqual(response.json().get("state"), str(State.AVAILABLE))

    def test_config_state(self):
        response = self.client.get(reverse("orca_state", kwargs={"device_ip": "127.0.0.1"}), )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        request = self.factory.put(path=reverse('device_interface_list'), data={"mgt_ip": "127.0.0.1"}, format="json")
        middleware = BlockPutMiddleware(lambda req: put_stub(req, self.client))

        response = middleware(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("orca_state", kwargs={"device_ip": "127.0.0.1"}), )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("device_ip"), "127.0.0.1")
        self.assertEqual(response.json().get("state"), str(State.AVAILABLE))

    @pytest.mark.django_db
    def test_schedule_discovery_state(self):
        response = self.client.get(reverse("device"))
        if response.data:
            response = self.client.put(
                path=reverse("discover"),
                data={"discover_from_config": True},
                format="json"
            )
            if not response or response.get("result") == "Fail":
                self.fail("Failed to discover devices")
            response = self.client.get(reverse("device"))

        assert response.status_code == status.HTTP_200_OK

        device_ip = response.json()[0].get("mgt_ip")

        response = self.client.get(reverse("orca_state", kwargs={"device_ip": device_ip}), )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.put(
            path=reverse("discover_scheduler"),
            data={
                "mgt_ip": device_ip,
                "interval": 1
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # checking db
        response = self.client.get(reverse("discover_scheduler"), {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("interval"), 1)
        self.assertEqual(response.json().get("device_ip"), device_ip)

        job = scheduler.get_job("job_{}".format(device_ip))
        next_run_time = job.next_run_time
        print("time now: ", str(datetime.datetime.now(datetime.timezone.utc)))
        print("next run time", str(next_run_time))
        while datetime.datetime.now(datetime.timezone.utc) < next_run_time:
            time.sleep(10)
        response = self.client.get(reverse("orca_state", kwargs={"device_ip": device_ip}), )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("state"), str(State.SCHEDULED_DISCOVERY_IN_PROGRESS))

        # validating put request blocking while scheduled discovery is in progress
        request_body = {
            "mgt_ip": device_ip,
            "lag_name": "PortChannel104",
            "mtu": 8000,
            "admin_status": "up",
        },
        response = self.client.put(reverse("device_port_chnl"), data=request_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            "Scheduled discovery in progress".lower(), response.json().get("result").lower()
        )

        response = self.client.get(reverse("orca_state", kwargs={"device_ip": device_ip}), )
        state = response.json().get("state")

        # wait for scheduled discovery to complete
        while state != str(State.AVAILABLE):
            response = self.client.get(reverse("orca_state", kwargs={"device_ip": device_ip}), )
            state = response.json().get("state")
            print("state", state)
            time.sleep(5)

        response = self.client.delete(reverse("discover_scheduler"), {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("discover_scheduler"), {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_schedule_discovery(self):

        response = self.client.get(reverse("device"))
        if response.data:
            response = self.client.put(
                path=reverse("discover"),
                data={"discover_from_config": True},
                format="json"
            )
            if not response or response.get("result") == "Fail":
                self.fail("Failed to discover devices")
            response = self.client.get(reverse("device"))

        assert response.status_code == status.HTTP_200_OK

        device_ip = response.json()[0].get("mgt_ip")

        response = self.client.delete(
            path=reverse("del_db"),
            data={"mgt_ip": device_ip},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("device"), {"mgt_ip": device_ip})
        self.assertTrue(
            response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )

        response = self.client.get(reverse("orca_state", kwargs={"device_ip": device_ip}), )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.put(
            path=reverse("discover_scheduler"),
            data={
                "mgt_ip": device_ip,
                "interval": 1
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # checking db
        response = self.client.get(reverse("discover_scheduler"), {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("interval"), 1)
        self.assertEqual(response.json().get("device_ip"), device_ip)

        time.sleep(80)
        response = self.client.get(reverse("orca_state", kwargs={"device_ip": device_ip}), )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("device_ip"), device_ip)
        self.assertEqual(response.json().get("state"), str(State.SCHEDULED_DISCOVERY_IN_PROGRESS))

        response = self.client.get(reverse("orca_state", kwargs={"device_ip": device_ip}), )
        state = response.json().get("state")
        # wait for scheduled discovery to complete
        while state != str(State.AVAILABLE):
            response = self.client.get(reverse("orca_state", kwargs={"device_ip": device_ip}), )
            state = response.json().get("state")
            time.sleep(5)

        # checking device
        response = self.client.get(reverse("device"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            any([device_ip == device.get("mgt_ip") for device in response.json()])
        )

        response = self.client.delete(reverse("discover_scheduler"), {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("discover_scheduler"), {"mgt_ip": device_ip})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
