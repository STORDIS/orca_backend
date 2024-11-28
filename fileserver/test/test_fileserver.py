import os
from fileserver.test.test_common import TestCommon


class TestFileServer(TestCommon):

    test_file_name = "test.txt"
    test_file_content = "Hello World"

    def test_file_download(self):
        response = self.get_req("download_file", args=[self.test_file_name])
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.test_file_content, b"".join(response.streaming_content).decode("utf-8"))

    @classmethod
    def setUpClass(cls):
        app_directory = os.path.dirname(os.path.abspath(__file__))  # Get the path of the current app
        path = os.path.join(app_directory, '../media/download', cls.test_file_name)
        with open(path, "w") as f:
            f.write(cls.test_file_content)

    @classmethod
    def tearDownClass(cls):
        app_directory = os.path.dirname(os.path.abspath(__file__))  # Get the path of the current app
        path = os.path.join(app_directory, '../media/download', cls.test_file_name)
        os.remove(path)
