#!/usr/bin/env python3
"""
Unit tests for the client module.
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests the GithubOrgClient class.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """
        Tests that GithubOrgClient.org returns the correct value
        and that get_json is called once with the expected argument.
        """
        # Define the expected payload for the mocked get_json call
        expected_payload = {"login": org_name, "id": 123}
        mock_get_json.return_value = expected_payload

        # Create an instance of GithubOrgClient
        client = GithubOrgClient(org_name)

        # Access the org property (corrected from method call)
        result = client.org

        # Assert that get_json was called exactly once with the expected URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

        # Assert that the result is equal to the expected payload
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self):
        """
        Tests that _public_repos_url returns the expected URL
        based on a mocked org payload.
        """
        # Define the payload that GithubOrgClient.org should return
        expected_org_payload = {"repos_url": "https://api.github.com/orgs/test_org/repos"}

        # Use patch as a context manager to mock GithubOrgClient.org
        with patch('client.GithubOrgClient.org', new_callable=Mock) as mock_org:
            mock_org.return_value = expected_org_payload

            # Create an instance of GithubOrgClient
            client = GithubOrgClient("test_org")

            # Access the _public_repos_url property
            result = client._public_repos_url

            # Assert that GithubOrgClient.org was called
            mock_org.assert_called_once()

            # Assert that the result is the expected repos_url
            self.assertEqual(result, expected_org_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """
        Tests that GithubOrgClient.public_repos returns the expected
        list of repositories and that the underlying mocked calls are
        made correctly.
        """
        # Define the payload that get_json should return for repos_payload
        mock_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = mock_repos_payload

        # Define the URL that _public_repos_url should return
        expected_public_repos_url = "https://api.github.com/orgs/test_org/repos"

        # Use patch as a context manager to mock GithubOrgClient._public_repos_url property
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = expected_public_repos_url

            # Create an instance of GithubOrgClient
            client = GithubOrgClient("test_org")

            # Call the public_repos method
            result = client.public_repos()

            # Assert that _public_repos_url property was accessed
            mock_public_repos_url.assert_called_once()

            # Assert that get_json was called once with the expected URL
            mock_get_json.assert_called_once_with(
                expected_public_repos_url
            )

            # Assert that the list of repos is as expected
            self.assertEqual(result, ["repo1", "repo2", "repo3"])

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected_result):
        """
        Tests that GithubOrgClient.has_license returns the correct boolean
        value based on the provided repository and license key.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected_result)


# Prepare the parameters for parameterized_class from TEST_PAYLOAD
# TEST_PAYLOAD is a list of tuples: (org_info_part, repos_data)
# We need to transform it into a list of dictionaries with keys:
# "org_payload", "repos_payload", "expected_repos", "apache2_repos"
integration_test_fixtures = []
for org_info_part, repos_data in TEST_PAYLOAD:
    # Extract org_name from the repos_url in org_info_part
    # This assumes the org_info_part always has a 'repos_url'
    org_name = org_info_part["repos_url"].split('/')[-2]
    # Create a full org_payload for the test, including 'login'
    full_org_payload = {"login": org_name, **org_info_part}

    expected_repos_list = [repo["name"] for repo in repos_data]
    apache2_repos_list = [
        repo["name"] for repo in repos_data
        if repo.get("license", {}).get("key") == "apache-2.0"
    ]

    integration_test_fixtures.append({
        "org_payload": full_org_payload,
        "repos_payload": repos_data,
        "expected_repos": expected_repos_list,
        "apache2_repos": apache2_repos_list
    })


@parameterized_class(integration_test_fixtures)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for the GithubOrgClient.public_repos method.
    This class uses parameterized_class to run tests with different fixtures.
    """
    @classmethod
    def setUpClass(cls):
        """
        Sets up the class-level fixtures for integration tests.
        Mocks requests.get to return predefined payloads.
        """
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        # Configure side_effect for mock_get
        # The first call to requests.get will be for the org URL
        # The second call will be for the repos URL
        mock_org_response = Mock()
        mock_org_response.json.return_value = cls.org_payload

        mock_repos_response = Mock()
        mock_repos_response.json.return_value = cls.repos_payload

        cls.mock_get.side_effect = [mock_org_response, mock_repos_response]

    @classmethod
    def tearDownClass(cls):
        """
        Tears down the class-level fixtures after integration tests.
        Stops the requests.get patcher.
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Tests the public_repos method in an integration context without a license filter.
        Verifies that the list of public repositories matches the expected data.
        Also asserts that requests.get was called the correct number of times.
        """
        # The org_name is derived from the org_payload in setUpClass
        org_name = self.org_payload.get("login")

        client = GithubOrgClient(org_name)
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)
        # Assert that requests.get was called twice (once for org, once for repos)
        self.assertEqual(self.mock_get.call_count, 2)

    def test_public_repos_with_license(self):
        """
        Tests the public_repos method in an integration context
        Verifies that the list of public repositories with the specified
        matches the expected data.
        """
        # The org_name is derived from the org_payload in setUpClass
        org_name = self.org_payload.get("login")

        client = GithubOrgClient(org_name)
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)
# OK ( 3 chars long)
# has @parameterized_class decorator

#  - [Got]
# FAIL

# (5 chars long)

# [Expected]
# OK

# (3 chars long)
