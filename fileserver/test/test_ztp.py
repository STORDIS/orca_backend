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

    def test_ztp_rename(self):
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

        # rename ztp file
        response = self.put_req(
            "rename_ztp_file", {"old_filename": "ztp_test.json", "new_filename": "ztp_test_renamed.json"}
        )
        print(response.json())
        self.assertEqual(response.status_code, 200)

        # validate ztp file
        response = self.get_req("host_ztp_files", {"filename": "ztp_test_renamed.json"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], data["content"])
        self.assertEqual(response.json()["filename"], "ztp_test_renamed.json")

        # delete ztp file
        response = self.del_req("host_ztp_files", {"filename": "ztp_test2.json"})
        self.assertEqual(response.status_code, 200)
