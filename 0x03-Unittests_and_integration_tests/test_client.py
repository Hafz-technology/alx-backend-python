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


#!/usr/bin/env python3
"""
Integration tests for the GithubOrgClient.
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized, parameterized_class
import requests



# Extract fixtures from TEST_PAYLOAD
org_payload, repos_payload, expected_repos, apache2_repos = TEST_PAYLOAD[0]

# Define the GithubOrgClient class (minimal implementation for testing purposes)
# In a real project, this would be imported from a separate module.
class GithubOrgClient:
    """
    Client for the GitHub API to interact with organizations.
    """
    def __init__(self, org_name: str):
        self.org_name = org_name

    def org(self) -> dict:
        """
        Returns the organization payload.
        """
        url = f"https://api.github.com/orgs/{self.org_name}"
        return self._public_get(url)

    def repos_url(self) -> str:
        """
        Returns the repos URL from the organization payload.
        """
        return self.org()["repos_url"]

    def public_repos(self, license: str = None) -> list[str]:
        """
        Returns a list of public repository names for the organization,
        optionally filtered by license.
        """
        repos = self._public_get(self.repos_url())
        if license:
            return [
                repo["name"] for repo in repos
                if "license" in repo and repo["license"] and repo["license"]["key"] == license
            ]
        return [repo["name"] for repo in repos]

    @staticmethod
    def _public_get(url: str) -> dict:
        """
        Fetches data from a public URL. This method will be mocked in tests.
        """
        r = requests.get(url)
        return r.json()


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos,
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.public_repos method.
    This class mocks external HTTP requests to simulate API responses.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up class-level mocks for `requests.get`.
        This method is called once for the entire test class.
        It patches `requests.get` to return predefined payloads based on the URL.
        """
        # Define a custom MockResponse class to simulate requests.Response objects
        class MockResponse:
            def __init__(self, json_data, status_code=200):
                self._json_data = json_data
                self.status_code = status_code

            def json(self):
                return self._json_data

        # Define the side_effect function for requests.get
        # This function will be called whenever requests.get is invoked.
        def side_effect(url):
            """
            Custom side effect for requests.get mock.
            Returns a MockResponse object whose .json() method returns the appropriate fixture.
            """
            if url == "https://api.github.com/orgs/google":
                # If the URL is for the organization payload, return org_payload
                return MockResponse(cls.org_payload)
            elif url == cls.org_payload["repos_url"]:
                # If the URL is for the repositories payload, return repos_payload
                return MockResponse(cls.repos_payload)
            else:
                # For any unexpected URL, return an empty mock or raise an error
                # This helps in identifying unexpected network calls.
                return MockResponse({}, 404) # Return a 404 for unexpected URLs

        # Start patching 'requests.get' globally.
        # The patcher is stored in a class variable so it can be stopped later.
        cls.get_patcher = patch('requests.get', side_effect=side_effect)
        # Store the mock object returned by start() for assertions in test methods.
        cls.mock_get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """
        Stop the patcher after all tests in the class have run.
        This method is called once after all tests in the class are completed.
        It ensures that the mock applied in setUpClass is reverted.
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Test that `GithubOrgClient.public_repos` returns the expected list of
        public repository names without any license filtering.
        Verifies that `requests.get` was called with the correct URLs.
        """
        # Instantiate the client with the organization name "google"
        client = GithubOrgClient("google")
        # Call the public_repos method
        repos = client.public_repos()
        # Assert that the returned list of repositories matches the expected_repos fixture
        self.assertEqual(repos, self.expected_repos)

        # Verify that requests.get was called with the correct URLs
        # The calls should be for the organization URL and then the repos URL.
        self.mock_get.assert_any_call("https://api.github.com/orgs/google")
        self.mock_get.assert_any_call("https://api.github.com/orgs/google/repos")

    def test_public_repos_with_license(self):
        """
        Test that `GithubOrgClient.public_repos` returns the expected list of
        public repository names when filtered by a specific license ("apache-2.0").
        Verifies that `requests.get` was called with the correct URLs.
        """
        # Instantiate the client with the organization name "google"
        client = GithubOrgClient("google")
        # Call the public_repos method with the license filter
        repos = client.public_repos("apache-2.0")
        # Assert that the returned list of repositories matches the apache2_repos fixture
        self.assertEqual(repos, self.apache2_repos)

        # Verify that requests.get was called with the correct URLs
        # The calls should be for the organization URL and then the repos URL.
        self.mock_get.assert_any_call("https://api.github.com/orgs/google")
        self.mock_get.assert_any_call("https://api.github.com/orgs/google/repos")
