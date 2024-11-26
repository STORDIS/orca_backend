from fileserver.test.test_common import TestCommon


class TestZTP(TestCommon):

    def test_ztp(self):
        data = {
            "filename": "ztp_test.json",
            "content": "test content"
        }

        # add ztp file
        response = self.put_req("host_ztp_files", data)
        self.assertEqual(response.status_code, 200)

        # validate ztp file
        response = self.get_req("host_ztp_files", {"filename": "ztp_test.json"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], data["content"])
        self.assertEqual(response.json()["filename"], data["filename"])

        # list ztp files
        response = self.get_req("host_ztp_files")
        self.assertEqual(response.status_code, 200)
        self.assertIn(data["filename"], [i["filename"] for i in response.json()])

        # delete ztp file
        response = self.del_req("host_ztp_files", {"filename": "ztp_test.json"})
        self.assertEqual(response.status_code, 200)

        # validate ztp file is deleted
        response = self.get_req("host_ztp_files", {"filename": "ztp_test.json"})
        self.assertEqual(response.status_code, 404)
