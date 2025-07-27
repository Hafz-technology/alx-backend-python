#!/usr/bin/env python3
"""
Unit and integration tests for GithubOrgClient.
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests for the GithubOrgClient class.
    """
    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(self,
                 org_name: str,
                 expected_payload: dict,
                 mock_get_json: patch) -> None:
        """
        Test that GithubOrgClient.org returns the correct value.
        Uses @patch as a decorator to mock get_json.
        """
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(
            GithubOrgClient.ORG_URL.format(org=org_name)
        )

    def test_public_repos_url(self) -> None:
        """
        Test that _public_repos_url returns the expected URL
        based on a mocked org payload.
        """
        expected_repos_url = "https://api.github.com/orgs/testorg/repos"
        # Patch GithubOrgClient.org as a property
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            # Set the return value of the mocked org property
            mock_org.return_value = {"repos_url": expected_repos_url}

            # Create an instance of GithubOrgClient
            client = GithubOrgClient("testorg")

            # Assert that _public_repos_url returns the expected value
            self.assertEqual(client._public_repos_url, expected_repos_url)

            # Assert that the org property was called exactly once
            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: patch) -> None:
        """
        Test GithubOrgClient.public_repos method.
        Mocks get_json and _public_repos_url.
        """
        # Define the payload that mock_get_json will return
        mock_repos_payload = [
            {"name": "alx-backend", "license": {"key": "mit"}},
            {"name": "holberton-web", "license": {"key": "apache-2.0"}},
            {"name": "my-app", "license": None},  # No license
            {"name": "old-project", "license": {"key": "gpl-3.0"}},
        ]
        mock_get_json.return_value = mock_repos_payload

        # Define the expected list of repo names
        expected_repo_names = ["alx-backend", "holberton-web",
                               "my-app", "old-project"]

        # Define the URL that mock_public_repos_url will return
        mock_repos_url = "https://api.github.com/users/google/repos"

        # Patch GithubOrgClient._public_repos_url as a property
        # using a context manager
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock,
                   return_value=mock_repos_url) as mock_public_repos_url:

            client = GithubOrgClient("google")

            # Call the public_repos method
            result_repos = client.public_repos()

            # Assert that the list of repos matches the expected names
            self.assertEqual(result_repos, expected_repo_names)

            # Assert that _public_repos_url property was accessed once
            mock_public_repos_url.assert_called_once()

            # Assert that get_json was called once with the mocked URL
            mock_get_json.assert_called_once_with(mock_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"name": "no_license_repo"}, "my_license", False),
        ({"license": {}}, "my_license", False), # license key exists but is empty dict
        ({}, "my_license", False) # empty repo dict
    ])
    def test_has_license(self,
                         repo: dict,
                         license_key: str,
                         expected_result: bool) -> None:
        """
        Test the GithubOrgClient.has_license static method.
        """
        self.assertEqual(GithubOrgClient.has_license(repo, license_key),
                         expected_result)


if __name__ == '__main__':
    unittest.main()







#!/usr/bin/env python3
"""
Unit and integration tests for GithubOrgClient.
"""
import unittest
from unittest.mock import patch, PropertyMock, MagicMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests for the GithubOrgClient class.
    """
    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(self,
                 org_name: str,
                 expected_payload: dict,
                 mock_get_json: patch) -> None:
        """
        Test that GithubOrgClient.org returns the correct value.
        Uses @patch as a decorator to mock get_json.
        """
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(
            GithubOrgClient.ORG_URL.format(org=org_name)
        )

    def test_public_repos_url(self) -> None:
        """
        Test that _public_repos_url returns the expected URL
        based on a mocked org payload.
        """
        expected_repos_url = "https://api.github.com/orgs/testorg/repos"
        # Patch GithubOrgClient.org as a property
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            # Set the return value of the mocked org property
            mock_org.return_value = {"repos_url": expected_repos_url}

            # Create an instance of GithubOrgClient
            client = GithubOrgClient("testorg")

            # Assert that _public_repos_url returns the expected value
            self.assertEqual(client._public_repos_url, expected_repos_url)

            # Assert that the org property was called exactly once
            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: patch) -> None:
        """
        Test GithubOrgClient.public_repos method.
        Mocks get_json and _public_repos_url.
        """
        # Define the payload that mock_get_json will return
        mock_repos_payload = [
            {"name": "alx-backend", "license": {"key": "mit"}},
            {"name": "holberton-web", "license": {"key": "apache-2.0"}},
            {"name": "my-app", "license": None},  # No license
            {"name": "old-project", "license": {"key": "gpl-3.0"}},
        ]
        mock_get_json.return_value = mock_repos_payload

        # Define the expected list of repo names
        expected_repo_names = ["alx-backend", "holberton-web",
                               "my-app", "old-project"]

        # Define the URL that mock_public_repos_url will return
        mock_repos_url = "https://api.github.com/users/google/repos"

        # Patch GithubOrgClient._public_repos_url as a property
        # using a context manager
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock,
                   return_value=mock_repos_url) as mock_public_repos_url:

            client = GithubOrgClient("google")

            # Call the public_repos method
            result_repos = client.public_repos()

            # Assert that the list of repos matches the expected names
            self.assertEqual(result_repos, expected_repo_names)

            # Assert that _public_repos_url property was accessed once
            mock_public_repos_url.assert_called_once()

            # Assert that get_json was called once with the mocked URL
            mock_get_json.assert_called_once_with(mock_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"name": "no_license_repo"}, "my_license", False),
        ({"license": {}}, "my_license", False),
        ({}, "my_license", False)
    ])
    def test_has_license(self,
                         repo: dict,
                         license_key: str,
                         expected_result: bool) -> None:
        """
        Test the GithubOrgClient.has_license static method.
        """
        self.assertEqual(GithubOrgClient.has_license(repo, license_key),
                         expected_result)


@parameterized_class([
    {
        'org_payload': org_payload,
        'repos_payload': repos_payload,
        'expected_repos': expected_repos,
        'apache2_repos': apache2_repos,
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.public_repos.
    This class mocks external HTTP requests using fixtures.
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up class for integration tests.
        Mocks requests.get to return example payloads based on URL.
        """
        def get_payload(url: str) -> MagicMock:
            """
            Returns a MagicMock object with a json method that returns
            the appropriate fixture based on the URL.
            """
            if url == GithubOrgClient.ORG_URL.format(org="google"):
                return MagicMock(json=lambda: cls.org_payload)
            elif url == cls.org_payload["repos_url"]:
                return MagicMock(json=lambda: cls.repos_payload)
            return MagicMock(json=lambda: {}) # Default empty payload

        cls.get_patcher = patch('requests.get', side_effect=get_payload)
        cls.mock_get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Tear down class by stopping the patcher.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Integration test for public_repos with no license filter.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)
        # Verify that requests.get was called for org and repos_url
        calls = self.mock_get.call_args_list
        self.assertEqual(len(calls), 2)
        self.mock_get.assert_any_call(
            GithubOrgClient.ORG_URL.format(org="google")
        )
        self.mock_get.assert_any_call(self.org_payload["repos_url"])

    def test_public_repos_with_license(self) -> None:
        """
        Integration test for public_repos with apache-2.0 license filter.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos("apache-2.0"),
                         self.apache2_repos)
        # Verify that requests.get was called for org and repos_url
        calls = self.mock_get.call_args_list
        self.assertEqual(len(calls), 2)
        self.mock_get.assert_any_call(
            GithubOrgClient.ORG_URL.format(org="google")
        )
        self.mock_get.assert_any_call(self.org_payload["repos_url"])


if __name__ == '__main__':
    unittest.main()
