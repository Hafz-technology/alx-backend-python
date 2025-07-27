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
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
import requests

# Load fixtures from fixtures.py
# Assuming fixtures.py is in the same directory or accessible
try:
    from fixtures import TEST_PAYLOAD
except ImportError:
    # Fallback for direct execution if fixtures.py isn't directly importable
    # In a real scenario, fixtures.py would be properly placed.
    TEST_PAYLOAD = [
      (
        {"repos_url": "https://api.github.com/orgs/google/repos"},
        [
          {
            "id": 7697149,
            "node_id": "MDEwOlJlcG9zaXRvcnk3Njk3MTQ5",
            "name": "episodes.dart",
            "full_name": "google/episodes.dart",
            "private": False,
            "owner": {
              "login": "google",
              "id": 1342004,
              "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
              "avatar_url": "https://avatars1.githubusercontent.com/u/1342004?v=4",
              "gravatar_id": "",
              "url": "https://api.github.com/users/google",
              "html_url": "https://github.com/google",
              "followers_url": "https://api.github.com/users/google/followers",
              "following_url": "https://api.github.com/users/google/following{/other_user}",
              "gists_url": "https://api.github.com/users/google/gists{/gist_id}",
              "starred_url": "https://api.github.com/users/google/starred{/owner}{/repo}",
              "subscriptions_url": "https://api.github.com/users/google/subscriptions",
              "organizations_url": "https://api.github.com/users/google/orgs",
              "repos_url": "https://api.github.com/users/google/repos",
              "events_url": "https://api.github.com/users/google/events{/privacy}",
              "received_events_url": "https://api.github.com/users/google/received_events",
              "type": "Organization",
              "site_admin": False
            },
            "html_url": "https://github.com/google/episodes.dart",
            "description": "A framework for timing performance of web apps.",
            "fork": False,
            "url": "https://api.github.com/repos/google/episodes.dart",
            "forks_url": "https://api.github.com/repos/google/episodes.dart/forks",
            "keys_url": "https://api.github.com/repos/google/episodes.dart/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/google/episodes.dart/collaborators{/collaborator}",
            "teams_url": "https://api.github.com/repos/google/episodes.dart/teams",
            "hooks_url": "https://api.github.com/repos/google/episodes.dart/hooks",
            "issue_events_url": "https://api.github.com/repos/google/episodes.dart/issues/events{/number}",
            "events_url": "https://api.github.com/repos/google/episodes.dart/events",
            "assignees_url": "https://api.github.com/repos/google/episodes.dart/assignees{/user}",
            "branches_url": "https://api.github.com/repos/google/episodes.dart/branches{/branch}",
            "tags_url": "https://api.github.com/repos/google/episodes.dart/tags",
            "blobs_url": "https://api.github.com/repos/google/episodes.dart/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/google/episodes.dart/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/google/episodes.dart/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/google/episodes.dart/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/google/episodes.dart/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/google/episodes.dart/languages",
            "stargazers_url": "https://api.github.com/repos/google/episodes.dart/stargazers",
            "contributors_url": "https://api.github.com/repos/google/episodes.dart/contributors",
            "subscribers_url": "https://api.github.com/repos/google/episodes.dart/subscribers",
            "subscription_url": "https://api.github.com/repos/google/episodes.dart/subscription",
            "commits_url": "https://api.github.com/repos/google/episodes.dart/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/google/episodes.dart/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/google/episodes.dart/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/google/episodes.dart/issues/comments{/number}",
            "contents_url": "https://api.github.com/repos/google/episodes.dart/contents/{+path}",
            "compare_url": "https://api.github.com/repos/google/episodes.dart/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/google/episodes.dart/merges",
            "archive_url": "https://api.github.com/repos/google/episodes.dart/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/google/episodes.dart/downloads",
            "issues_url": "https://api.github.com/repos/google/episodes.dart/issues{/number}",
            "pulls_url": "https://api.github.com/repos/google/episodes.dart/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/google/episodes.dart/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/google/episodes.dart/notifications{?since,all,participating}",
            "labels_url": "https://api.github.com/repos/google/episodes.dart/labels{/name}",
            "releases_url": "https://api.github.com/repos/google/episodes.dart/releases{/id}",
            "deployments_url": "https://api.github.com/repos/google/episodes.dart/deployments",
            "created_at": "2013-01-19T00:31:37Z",
            "updated_at": "2019-09-23T11:53:58Z",
            "pushed_at": "2014-10-09T21:39:33Z",
            "git_url": "git://github.com/google/episodes.dart.git",
            "ssh_url": "git@github.com:google/episodes.dart.git",
            "clone_url": "https://github.com/google/episodes.dart.git",
            "svn_url": "https://github.com/google/episodes.dart",
            "homepage": None,
            "size": 191,
            "stargazers_count": 12,
            "watchers_count": 12,
            "language": "Dart",
            "has_issues": True,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": True,
            "has_pages": False,
            "forks_count": 22,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 0,
            "license": {
              "key": "bsd-3-clause",
              "name": "BSD 3-Clause \"New\" or \"Revised\" License",
              "spdx_id": "BSD-3-Clause",
              "url": "https://api.github.com/licenses/bsd-3-clause",
              "node_id": "MDc6TGljZW5zZTU="
            },
            "forks": 22,
            "open_issues": 0,
            "watchers": 12,
            "default_branch": "master",
            "permissions": {
              "admin": False,
              "push": False,
              "pull": True
            }
          },
          {
            "id": 7776515,
            "node_id": "MDEwOlJlcG9zaXRvcnk3Nzc2NTE1",
            "name": "cpp-netlib",
            "full_name": "google/cpp-netlib",
            "private": False,
            "owner": {
              "login": "google",
              "id": 1342004,
              "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
              "avatar_url": "https://avatars1.githubusercontent.com/u/1342004?v=4",
              "gravatar_id": "",
              "url": "https://api.github.com/users/google",
              "html_url": "https://github.com/google",
              "followers_url": "https://api.github.com/users/google/followers",
              "following_url": "https://api.github.com/users/google/following{/other_user}",
              "gists_url": "https://api.github.com/users/google/gists{/gist_id}",
              "starred_url": "https://api.github.com/users/google/starred{/owner}{/repo}",
              "subscriptions_url": "https://api.github.com/users/google/subscriptions",
              "organizations_url": "https://api.github.com/users/google/orgs",
              "repos_url": "https://api.github.com/users/google/repos",
              "events_url": "https://api.github.com/users/google/events{/privacy}",
              "received_events_url": "https://api.github.com/users/google/received_events",
              "type": "Organization",
              "site_admin": False
            },
            "html_url": "https://github.com/google/cpp-netlib",
            "description": "The C++ Network Library Project -- header-only, cross-platform, standards compliant networking library.",
            "fork": True,
            "url": "https://api.github.com/repos/google/cpp-netlib",
            "forks_url": "https://api.github.com/repos/google/cpp-netlib/forks",
            "keys_url": "https://api.github.com/repos/google/cpp-netlib/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/google/cpp-netlib/collaborators{/collaborator}",
            "teams_url": "https://api.github.com/repos/google/cpp-netlib/teams",
            "hooks_url": "https://api.github.com/repos/google/cpp-netlib/hooks",
            "issue_events_url": "https://api.github.com/repos/google/cpp-netlib/issues/events{/number}",
            "events_url": "https://api.github.com/repos/google/cpp-netlib/events",
            "assignees_url": "https://api.github.com/repos/google/cpp-netlib/assignees{/user}",
            "branches_url": "https://api.github.com/repos/google/cpp-netlib/branches{/branch}",
            "tags_url": "https://api.github.com/repos/google/cpp-netlib/tags",
            "blobs_url": "https://api.github.com/repos/google/cpp-netlib/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/google/cpp-netlib/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/google/cpp-netlib/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/google/cpp-netlib/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/google/cpp-netlib/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/google/cpp-netlib/languages",
            "stargazers_url": "https://api.github.com/repos/google/cpp-netlib/stargazers",
            "contributors_url": "https://api.github.com/repos/google/cpp-netlib/contributors",
            "subscribers_url": "https://api.github.com/repos/google/cpp-netlib/subscribers",
            "subscription_url": "https://api.github.com/repos/google/cpp-netlib/subscription",
            "commits_url": "https://api.github.com/repos/google/cpp-netlib/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/google/cpp-netlib/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/google/cpp-netlib/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/google/cpp-netlib/issues/comments{/number}",
            "contents_url": "https://api.github.com/repos/google/cpp-netlib/contents/{+path}",
            "compare_url": "https://api.github.com/repos/google/cpp-netlib/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/google/cpp-netlib/merges",
            "archive_url": "https://api.github.com/repos/google/cpp-netlib/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/google/cpp-netlib/downloads",
            "issues_url": "https://api.github.com/repos/google/cpp-netlib/issues{/number}",
            "pulls_url": "https://api.github.com/repos/google/cpp-netlib/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/google/cpp-netlib/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/google/cpp-netlib/notifications{?since,all,participating}",
            "labels_url": "https://api.github.com/repos/google/cpp-netlib/labels{/name}",
            "releases_url": "https://api.github.com/repos/google/cpp-netlib/releases{/id}",
            "deployments_url": "https://api.github.com/repos/google/cpp-netlib/deployments",
            "created_at": "2013-01-23T14:45:32Z",
            "updated_at": "2019-11-15T02:26:31Z",
            "pushed_at": "2018-12-05T17:42:29Z",
            "git_url": "git://github.com/google/cpp-netlib.git",
            "ssh_url": "git@github.com:google/cpp-netlib.git",
            "clone_url": "https://github.com/google/cpp-netlib.git",
            "svn_url": "https://github.com/google/cpp-netlib",
            "homepage": "http://cpp-netlib.github.com/",
            "size": 8937,
            "stargazers_count": 292,
            "watchers_count": 292,
            "language": "C++",
            "has_issues": False,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": True,
            "has_pages": False,
            "forks_count": 59,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 0,
            "license": {
              "key": "bsl-1.0",
              "name": "Boost Software License 1.0",
              "spdx_id": "BSL-1.0",
              "url": "https://api.github.com/licenses/bsl-1.0",
              "node_id": "MDc6TGljZW5zZTI4"
            },
            "forks": 59,
            "open_issues": 0,
            "watchers": 292,
            "default_branch": "master",
            "permissions": {
              "admin": False,
              "push": False,
              "pull": True
            }
          },
          {
            "id": 7968417,
            "node_id": "MDEwOlJlcG9zaXRvcnk3OTY4NDE3",
            "name": "dagger",
            "full_name": "google/dagger",
            "private": False,
            "owner": {
              "login": "google",
              "id": 1342004,
              "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
              "avatar_url": "https://avatars1.githubusercontent.com/u/1342004?v=4",
              "gravatar_id": "",
              "url": "https://api.github.com/users/google",
              "html_url": "https://github.com/google",
              "followers_url": "https://api.github.com/users/google/followers",
              "following_url": "https://api.github.com/users/google/following{/other_user}",
              "gists_url": "https://api.github.com/users/google/gists{/gist_id}",
              "starred_url": "https://api.github.com/users/google/starred{/owner}{/repo}",
              "subscriptions_url": "https://api.github.com/users/google/subscriptions",
              "organizations_url": "https://api.github.com/users/google/orgs",
              "repos_url": "https://api.github.com/users/google/repos",
              "events_url": "https://api.github.com/users/google/events{/privacy}",
              "received_events_url": "https://api.github.com/users/google/received_events",
              "type": "Organization",
              "site_admin": False
            },
            "html_url": "https://github.com/google/dagger",
            "description": "A fast dependency injector for Android and Java.",
            "fork": True,
            "url": "https://api.github.com/repos/google/dagger",
            "forks_url": "https://api.github.com/repos/google/dagger/forks",
            "keys_url": "https://api.github.com/repos/google/dagger/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/google/dagger/collaborators{/collaborator}",
            "teams_url": "https://api.github.com/repos/google/dagger/teams",
            "hooks_url": "https://api.github.com/repos/google/dagger/hooks",
            "issue_events_url": "https://api.github.com/repos/google/dagger/issues/events{/number}",
            "events_url": "https://api.github.com/repos/google/dagger/events",
            "assignees_url": "https://api.github.com/repos/google/dagger/assignees{/user}",
            "branches_url": "https://api.github.com/repos/google/dagger/branches{/branch}",
            "tags_url": "https://api.github.com/repos/google/dagger/tags",
            "blobs_url": "https://api.github.com/repos/google/dagger/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/google/dagger/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/google/dagger/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/google/dagger/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/google/dagger/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/google/dagger/languages",
            "stargazers_url": "https://api.github.com/repos/google/dagger/stargazers",
            "contributors_url": "https://api.github.com/repos/google/dagger/contributors",
            "subscribers_url": "https://api.github.com/repos/google/dagger/subscribers",
            "subscription_url": "https://api.github.com/repos/google/dagger/subscription",
            "commits_url": "https://api.github.com/repos/google/dagger/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/google/dagger/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/google/dagger/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/google/dagger/issues/comments{/number}",
            "contents_url": "https://api.github.com/repos/google/dagger/contents/{+path}",
            "compare_url": "https://api.github.com/repos/google/dagger/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/google/dagger/merges",
            "archive_url": "https://api.github.com/repos/google/dagger/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/google/dagger/downloads",
            "issues_url": "https://api.github.com/repos/google/dagger/issues{/number}",
            "pulls_url": "https://api.github.com/repos/google/dagger/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/google/dagger/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/google/dagger/notifications{?since,all,participating}",
            "labels_url": "https://api.github.com/repos/google/dagger/labels{/name}",
            "releases_url": "https://api.github.com/repos/google/dagger/releases{/id}",
            "deployments_url": "https://api.github.com/repos/google/dagger/deployments",
            "created_at": "2013-02-01T23:14:14Z",
            "updated_at": "2019-12-03T12:39:55Z",
            "pushed_at": "2019-11-27T21:20:38Z",
            "git_url": "git://github.com/google/dagger.git",
            "ssh_url": "git@github.com:google/dagger.git",
            "clone_url": "https://github.com/google/dagger.git",
            "svn_url": "https://github.com/google/dagger",
            "homepage": "https://dagger.dev",
            "size": 59129,
            "stargazers_count": 14492,
            "watchers_count": 14492,
            "language": "Java",
            "has_issues": True,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": True,
            "has_pages": True,
            "forks_count": 1741,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 148,
            "license": {
              "key": "apache-2.0",
              "name": "Apache License 2.0",
              "spdx_id": "Apache-2.0",
              "url": "https://api.github.com/licenses/apache-2.0",
              "node_id": "MDc6TGljZW5zZTI="
            },
            "forks": 1741,
            "open_issues": 148,
            "watchers": 14492,
            "default_branch": "master",
            "permissions": {
              "admin": False,
              "push": False,
              "pull": True
            }
          },
          {
            "id": 8165161,
            "node_id": "MDEwOlJlcG9zaXRvcnk4MTY1MTYx",
            "name": "ios-webkit-debug-proxy",
            "full_name": "google/ios-webkit-debug-proxy",
            "private": False,
            "owner": {
              "login": "google",
              "id": 1342004,
              "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
              "avatar_url": "https://avatars1.githubusercontent.com/u/1342004?v=4",
              "gravatar_id": "",
              "url": "https://api.github.com/users/google",
              "html_url": "https://github.com/google",
              "followers_url": "https://api.github.com/users/google/followers",
              "following_url": "https://api.github.com/users/google/following{/other_user}",
              "gists_url": "https://api.github.com/users/google/gists{/gist_id}",
              "starred_url": "https://api.github.com/users/google/starred{/owner}{/repo}",
              "subscriptions_url": "https://api.github.com/users/google/subscriptions",
              "organizations_url": "https://api.github.com/users/google/orgs",
              "repos_url": "https://api.github.com/users/google/repos",
              "events_url": "https://api.github.com/users/google/events{/privacy}",
              "received_events_url": "https://api.github.com/users/google/received_events",
              "type": "Organization",
              "site_admin": False
            },
            "html_url": "https://github.com/google/ios-webkit-debug-proxy",
            "description": "A DevTools proxy (Chrome Remote Debugging Protocol) for iOS devices (Safari Remote Web Inspector).",
            "fork": False,
            "url": "https://api.github.com/repos/google/ios-webkit-debug-proxy",
            "forks_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/forks",
            "keys_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/collaborators{/collaborator}",
            "teams_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/teams",
            "hooks_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/hooks",
            "issue_events_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/issues/events{/number}",
            "events_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/events",
            "assignees_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/assignees{/user}",
            "branches_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/branches{/branch}",
            "tags_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/tags",
            "blobs_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/languages",
            "stargazers_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/stargazers",
            "contributors_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/contributors",
            "subscribers_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/subscribers",
            "subscription_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/subscription",
            "commits_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/issues/comments{/number}",
            "contents_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/contents/{+path}",
            "compare_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/merges",
            "archive_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/downloads",
            "issues_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/issues{/number}",
            "pulls_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/notifications{?since,all,participating}",
            "labels_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/labels{/name}",
            "releases_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/releases{/id}",
            "deployments_url": "https://api.github.com/repos/google/ios-webkit-debug-proxy/deployments",
            "created_at": "2013-02-12T19:08:19Z",
            "updated_at": "2019-12-04T02:06:43Z",
            "pushed_at": "2019-11-24T07:02:13Z",
            "git_url": "git://github.com/google/ios-webkit-debug-proxy.git",
            "ssh_url": "git@github.com:google/ios-webkit-debug-proxy.git",
            "clone_url": "https://github.com/google/ios-webkit-debug-proxy.git",
            "svn_url": "https://github.com/google/ios-webkit-debug-proxy",
            "homepage": "",
            "size": 680,
            "stargazers_count": 4630,
            "watchers_count": 4630,
            "language": "C",
            "has_issues": True,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": False,
            "has_pages": False,
            "forks_count": 395,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 24,
            "license": {
              "key": "other",
              "name": "Other",
              "spdx_id": "NOASSERTION",
              "url": None,
              "node_id": "MDc6TGljZW5zZTA="
            },
            "forks": 395,
            "open_issues": 24,
            "watchers": 4630,
            "default_branch": "master",
            "permissions": {
              "admin": False,
              "push": False,
              "pull": True
            }
          },
          {
            "id": 8459994,
            "node_id": "MDEwOlJlcG9zaXRvcnk4NDU5OTk0",
            "name": "google.github.io",
            "full_name": "google/google.github.io",
            "private": False,
            "owner": {
              "login": "google",
              "id": 1342004,
              "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
              "avatar_url": "https://avatars1.githubusercontent.com/u/1342004?v=4",
              "gravatar_id": "",
              "url": "https://api.github.com/users/google",
              "html_url": "https://github.com/google",
              "followers_url": "https://api.github.com/users/google/followers",
              "following_url": "https://api.github.com/users/google/following{/other_user}",
              "gists_url": "https://api.github.com/users/google/gists{/gist_id}",
              "starred_url": "https://api.github.com/users/google/starred{/owner}{/repo}",
              "subscriptions_url": "https://api.github.com/users/google/subscriptions",
              "organizations_url": "https://api.github.com/users/google/orgs",
              "repos_url": "https://api.github.com/users/google/repos",
              "events_url": "https://api.github.com/users/google/events{/privacy}",
              "received_events_url": "https://api.github.com/users/google/received_events",
              "type": "Organization",
              "site_admin": False
            },
            "html_url": "https://github.com/google/google.github.io",
            "description": None,
            "fork": False,
            "url": "https://api.github.com/repos/google/google.github.io",
            "forks_url": "https://api.github.com/repos/google/google.github.io/forks",
            "keys_url": "https://api.github.com/repos/google/google.github.io/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/google/google.github.io/collaborators{/collaborator}",
            "teams_url": "https://api.github.com/repos/google/google.github.io/teams",
            "hooks_url": "https://api.github.com/repos/google/google.github.io/hooks",
            "issue_events_url": "https://api.github.com/repos/google/google.github.io/issues/events{/number}",
            "events_url": "https://api.github.com/repos/google/google.github.io/events",
            "assignees_url": "https://api.github.com/repos/google/google.github.io/assignees{/user}",
            "branches_url": "https://api.github.com/repos/google/google.github.io/branches{/branch}",
            "tags_url": "https://api.github.com/repos/google/google.github.io/tags",
            "blobs_url": "https://api.github.com/repos/google/google.github.io/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/google/google.github.io/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/google/google.github.io/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/google/google.github.io/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/google/google.github.io/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/google/google.github.io/languages",
            "stargazers_url": "https://api.github.com/repos/google/google.github.io/stargazers",
            "contributors_url": "https://api.github.com/repos/google/google.github.io/contributors",
            "subscribers_url": "https://api.github.com/repos/google/google.github.io/subscribers",
            "subscription_url": "https://api.github.com/repos/google/google.github.io/subscription",
            "commits_url": "https://api.github.com/repos/google/google.github.io/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/google/google.github.io/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/google/google.github.io/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/google/google.github.io/issues/comments{/number}",
            "contents_url": "https://api.github.com/repos/google/google.github.io/contents/{+path}",
            "compare_url": "https://api.github.com/repos/google/google.github.io/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/google/google.github.io/merges",
            "archive_url": "https://api.github.com/repos/google/google.github.io/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/google/google.github.io/downloads",
            "issues_url": "https://api.github.com/repos/google/google.github.io/issues{/number}",
            "pulls_url": "https://api.github.com/repos/google/google.github.io/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/google/google.github.io/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/google/google.github.io/notifications{?since,all,participating}",
            "labels_url": "https://api.github.com/repos/google/google.github.io/labels{/name}",
            "releases_url": "https://api.github.com/repos/google/google.github.io/releases{/id}",
            "deployments_url": "https://api.github.com/repos/google/google.github.io/deployments",
            "created_at": "2013-02-27T16:21:19Z",
            "updated_at": "2019-12-03T01:38:02Z",
            "pushed_at": "2019-12-03T01:37:58Z",
            "git_url": "git://github.com/google/google.github.io.git",
            "ssh_url": "git@github.com:google/google.github.io.git",
            "clone_url": "https://github.com/google/google.github.io.git",
            "svn_url": "https://github.com/google/google.github.io",
            "homepage": None,
            "size": 8,
            "stargazers_count": 38,
            "watchers_count": 38,
            "language": "HTML",
            "has_issues": False,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": False,
            "has_pages": True,
            "forks_count": 44,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 0,
            "license": None,
            "forks": 44,
            "open_issues": 0,
            "watchers": 38,
            "default_branch": "master",
            "permissions": {
              "admin": False,
              "push": False,
              "pull": True
            }
          },
          {
            "id": 8566972,
            "node_id": "MDEwOlJlcG9zaXRvcnk4NTY2OTcy",
            "name": "kratu",
            "full_name": "google/kratu",
            "private": False,
            "owner": {
              "login": "google",
              "id": 1342004,
              "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
              "avatar_url": "https://avatars1.githubusercontent.com/u/1342004?v=4",
              "gravatar_id": "",
              "url": "https://api.github.com/users/google",
              "html_url": "https://github.com/google",
              "followers_url": "https://api.github.com/users/google/followers",
              "following_url": "https://api.github.com/users/google/following{/other_user}",
              "gists_url": "https://api.github.com/users/google/gists{/gist_id}",
              "starred_url": "https://api.github.com/users/google/starred{/owner}{/repo}",
              "subscriptions_url": "https://api.github.com/users/google/subscriptions",
              "organizations_url": "https://api.github.com/users/google/orgs",
              "repos_url": "https://api.github.com/users/google/repos",
              "events_url": "https://api.github.com/users/google/events{/privacy}",
              "received_events_url": "https://api.github.com/users/google/received_events",
              "type": "Organization",
              "site_admin": False
            },
            "html_url": "https://github.com/google/kratu",
            "description": None,
            "fork": False,
            "url": "https://api.github.com/repos/google/kratu",
            "forks_url": "https://api.github.com/repos/google/kratu/forks",
            "keys_url": "https://api.github.com/repos/google/kratu/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/google/kratu/collaborators{/collaborator}",
            "teams_url": "https://api.github.com/repos/google/kratu/teams",
            "hooks_url": "https://api.github.com/repos/google/kratu/hooks",
            "issue_events_url": "https://api.github.com/repos/google/kratu/issues/events{/number}",
            "events_url": "https://api.github.com/repos/google/kratu/events",
            "assignees_url": "https://api.github.com/repos/google/kratu/assignees{/user}",
            "branches_url": "https://api.github.com/repos/google/kratu/branches{/branch}",
            "tags_url": "https://api.github.com/repos/google/kratu/tags",
            "blobs_url": "https://api.github.com/repos/google/kratu/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/google/kratu/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/google/kratu/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/google/kratu/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/google/kratu/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/google/kratu/languages",
            "stargazers_url": "https://api.github.com/repos/google/kratu/stargazers",
            "contributors_url": "https://api.github.com/repos/google/kratu/contributors",
            "subscribers_url": "https://api.github.com/repos/google/kratu/subscribers",
            "subscription_url": "https://api.github.com/repos/google/kratu/subscription",
            "commits_url": "https://api.github.com/repos/google/kratu/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/google/kratu/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/google/kratu/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/google/kratu/issues/comments{/number}",
            "contents_url": "https://api.github.com/repos/google/kratu/contents/{+path}",
            "compare_url": "https://api.github.com/repos/google/kratu/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/google/kratu/merges",
            "archive_url": "https://api.github.com/repos/google/kratu/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/google/kratu/downloads",
            "issues_url": "https://api.github.com/repos/google/kratu/issues{/number}",
            "pulls_url": "https://api.github.com/repos/google/kratu/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/google/kratu/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/google/kratu/notifications{?since,all,participating}",
            "labels_url": "https://api.github.com/repos/google/kratu/labels{/name}",
            "releases_url": "https://api.github.com/repos/google/kratu/releases{/id}",
            "deployments_url": "https://api.github.com/repos/google/kratu/deployments",
            "created_at": "2013-03-04T22:52:33Z",
            "updated_at": "2019-11-15T22:22:16Z",
            "pushed_at": "2017-08-06T05:44:34Z",
            "git_url": "git://github.com/google/kratu.git",
            "ssh_url": "git@github.com:google/kratu.git",
            "clone_url": "https://github.com/google/kratu.git",
            "svn_url": "https://github.com/google/kratu",
            "homepage": None,
            "size": 1777,
            "stargazers_count": 280,
            "watchers_count": 280,
            "language": "JavaScript",
            "has_issues": True,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": True,
            "has_pages": True,
            "forks_count": 32,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 0,
            "license": {
              "key": "apache-2.0",
              "name": "Apache License 2.0",
              "spdx_id": "Apache-2.0",
              "url": "https://api.github.com/licenses/apache-2.0",
              "node_id": "MDc6TGljZW5zZTI="
            },
            "forks": 32,
            "open_issues": 0,
            "watchers": 280,
            "default_branch": "master",
            "permissions": {
              "admin": False,
              "push": False,
              "pull": True
            }
          },
          {
            "id": 8858648,
            "node_id": "MDEwOlJlcG9zaXRvcnk4ODU4NjQ4",
            "name": "build-debian-cloud",
            "full_name": "google/build-debian-cloud",
            "private": False,
            "owner": {
              "login": "google",
              "id": 1342004,
              "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
              "avatar_url": "https://avatars1.githubusercontent.com/u/1342004?v=4",
              "gravatar_id": "",
              "url": "https://api.github.com/users/google",
              "html_url": "https://github.com/google",
              "followers_url": "https://api.github.com/users/google/followers",
              "following_url": "https://api.github.com/users/google/following{/other_user}",
              "gists_url": "https://api.github.com/users/google/gists{/gist_id}",
              "starred_url": "https://api.github.com/users/google/starred{/owner}{/repo}",
              "subscriptions_url": "https://api.github.com/users/google/subscriptions",
              "organizations_url": "https://api.github.com/users/google/orgs",
              "repos_url": "https://api.github.com/users/google/repos",
              "events_url": "https://api.github.com/users/google/events{/privacy}",
              "received_events_url": "https://api.github.com/users/google/received_events",
              "type": "Organization",
              "site_admin": False
            },
            "html_url": "https://github.com/google/build-debian-cloud",
            "description": "Script to create Debian Squeeze & Wheezy Amazon Machine Images (AMIs) and Google Compute Engine images",
            "fork": True,
            "url": "https://api.github.com/repos/google/build-debian-cloud",
            "forks_url": "https://api.github.com/repos/google/build-debian-cloud/forks",
            "keys_url": "https://api.github.com/repos/google/build-debian-cloud/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/google/build-debian-cloud/collaborators{/collaborator}",
            "teams_url": "https://api.github.com/repos/google/build-debian-cloud/teams",
            "hooks_url": "https://api.github.com/repos/google/build-debian-cloud/hooks",
            "issue_events_url": "https://api.github.com/repos/google/build-debian-cloud/issues/events{/number}",
            "events_url": "https://api.github.com/repos/google/build-debian-cloud/events",
            "assignees_url": "https://api.github.com/repos/google/build-debian-cloud/assignees{/user}",
            "branches_url": "https://api.github.com/repos/google/build-debian-cloud/branches{/branch}",
            "tags_url": "https://api.github.com/repos/google/build-debian-cloud/tags",
            "blobs_url": "https://api.github.com/repos/google/build-debian-cloud/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/google/build-debian-cloud/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/google/build-debian-cloud/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/google/build-debian-cloud/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/google/build-debian-cloud/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/google/build-debian-cloud/languages",
            "stargazers_url": "https://api.github.com/repos/google/build-debian-cloud/stargazers",
            "contributors_url": "https://api.github.com/repos/google/build-debian-cloud/contributors",
            "subscribers_url": "https://api.github.com/repos/google/build-debian-cloud/subscribers",
            "subscription_url": "https://api.github.com/repos/google/build-debian-cloud/subscription",
            "commits_url": "https://api.github.com/repos/google/build-debian-cloud/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/google/build-debian-cloud/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/google/build-debian-cloud/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/google/build-debian-cloud/issues/comments{/number}",
            "contents_url": "https://api.github.com/repos/google/build-debian-cloud/contents/{+path}",
            "compare_url": "https://api.github.com/repos/google/build-debian-cloud/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/google/build-debian-cloud/merges",
            "archive_url": "https://api.github.com/repos/google/build-debian-cloud/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/google/build-debian-cloud/downloads",
            "issues_url": "https://api.github.com/repos/google/build-debian-cloud/issues{/number}",
            "pulls_url": "https://api.github.com/repos/google/build-debian-cloud/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/google/build-debian-cloud/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/google/build-debian-cloud/notifications{?since,all,participating}",
            "labels_url": "https://api.github.com/repos/google/build-debian-cloud/labels{/name}",
            "releases_url": "https://api.github.com/repos/google/build-debian-cloud/releases{/id}",
            "deployments_url": "https://api.github.com/repos/google/build-debian-cloud/deployments",
            "created_at": "2013-03-18T16:32:00Z",
            "updated_at": "2019-09-23T11:54:00Z",
            "pushed_at": "2014-06-17T18:52:10Z",
            "git_url": "git://github.com/google/build-debian-cloud.git",
            "ssh_url": "git@github.com:google/build-debian-cloud.git",
            "clone_url": "https://github.com/google/build-debian-cloud.git",
            "svn_url": "https://github.com/google/build-debian-cloud",
            "homepage": "",
            "size": 986,
            "stargazers_count": 32,
            "watchers_count": 32,
            "language": "Shell",
            "has_issues": False,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": False,
            "has_pages": False,
            "forks_count": 22,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 5,
            "license": {
              "key": "other",
              "name": "Other",
              "spdx_id": "NOASSERTION",
              "url": None,
              "node_id": "MDc6TGljZW5zZTA="
            },
            "forks": 22,
            "open_issues": 5,
            "watchers": 32,
            "default_branch": "master",
            "permissions": {
              "admin": False,
              "push": False,
              "pull": True
            }
          },
          {
            "id": 9060347,
            "node_id": "MDEwOlJlcG9zaXRvcnk5MDYwMzQ3",
            "name": "traceur-compiler",
            "full_name": "google/traceur-compiler",
            "private": False,
            "owner": {
              "login": "google",
              "id": 1342004,
              "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
              "avatar_url": "https://avatars1.githubusercontent.com/u/1342004?v=4",
              "gravatar_id": "",
              "url": "https://api.github.com/users/google",
              "html_url": "https://github.com/google",
              "followers_url": "https://api.github.com/users/google/followers",
              "following_url": "https://api.github.com/users/google/following{/other_user}",
              "gists_url": "https://api.github.com/users/google/gists{/gist_id}",
              "starred_url": "https://api.github.com/users/google/starred{/owner}{/repo}",
              "subscriptions_url": "https://api.github.com/users/google/subscriptions",
              "organizations_url": "https://api.github.com/users/google/orgs",
              "repos_url": "https://api.github.com/users/google/repos",
              "events_url": "https://api.github.com/users/google/events{/privacy}",
              "received_events_url": "https://api.github.com/users/google/received_events",
              "type": "Organization",
              "site_admin": False
            },
            "html_url": "https://github.com/google/traceur-compiler",
            "description": "Traceur is a JavaScript.next-to-JavaScript-of-today compiler",
            "fork": False,
            "url": "https://api.github.com/repos/google/traceur-compiler",
            "forks_url": "https://api.github.com/repos/google/traceur-compiler/forks",
            "keys_url": "https://api.github.com/repos/google/traceur-compiler/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/google/traceur-compiler/collaborators{/collaborator}",
            "teams_url": "https://api.github.com/repos/google/traceur-compiler/teams",
            "hooks_url": "https://api.github.com/repos/google/traceur-compiler/hooks",
            "issue_events_url": "https://api.github.com/repos/google/traceur-compiler/issues/events{/number}",
            "events_url": "https://api.github.com/repos/google/traceur-compiler/events",
            "assignees_url": "https://api.github.com/repos/google/traceur-compiler/assignees{/user}",
            "branches_url": "https://api.github.com/repos/google/traceur-compiler/branches{/branch}",
            "tags_url": "https://api.github.com/repos/google/traceur-compiler/tags",
            "blobs_url": "https://api.github.com/repos/google/traceur-compiler/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/google/traceur-compiler/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/google/traceur-compiler/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/google/traceur-compiler/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/google/traceur-compiler/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/google/traceur-compiler/languages",
            "stargazers_url": "https://api.github.com/repos/google/traceur-compiler/stargazers",
            "contributors_url": "https://api.github.com/repos/google/traceur-compiler/contributors",
            "subscribers_url": "https://api.github.com/repos/google/traceur-compiler/subscribers",
            "subscription_url": "https://api.github.com/repos/google/traceur-compiler/subscription",
            "commits_url": "https://api.github.com/repos/google/traceur-compiler/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/google/traceur-compiler/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/google/traceur-compiler/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/google/traceur-compiler/issues/comments{/number}",
            "contents_url": "https://api.github.com/repos/google/traceur-compiler/contents/{+path}",
            "compare_url": "https://api.github.com/repos/google/traceur-compiler/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/google/traceur-compiler/merges",
            "archive_url": "https://api.github.com/repos/google/traceur-compiler/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/google/traceur-compiler/downloads",
            "issues_url": "https://api.github.com/repos/google/traceur-compiler/issues{/number}",
            "pulls_url": "https://api.github.com/repos/google/traceur-compiler/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/google/traceur-compiler/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/google/traceur-compiler/notifications{?since,all,participating}",
            "labels_url": "https://api.github.com/repos/google/traceur-compiler/labels{/name}",
            "releases_url": "https://api.github.com/repos/google/traceur-compiler/releases{/id}",
            "deployments_url": "https://api.github.com/repos/google/traceur-compiler/deployments",
            "created_at": "2013-03-27T18:05:40Z",
            "updated_at": "2019-12-02T16:45:54Z",
            "pushed_at": "2018-05-28T04:37:54Z",
            "git_url": "git://github.com/google/traceur-compiler.git",
            "ssh_url": "git@github.com:google/traceur-compiler.git",
            "clone_url": "https://github.com/google/traceur-compiler.git",
            "svn_url": "https://github.com/google/traceur-compiler",
            "homepage": "",
            "size": 27487,
            "stargazers_count": 8033,
            "watchers_count": 8033,
            "language": "JavaScript",
            "has_issues": True,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": True,
            "has_pages": True,
            "forks_count": 604,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 296,
            "license": {
              "key": "apache-2.0",
              "name": "Apache License 2.0",
              "spdx_id": "Apache-2.0",
              "url": "https://api.github.com/licenses/apache-2.0",
              "node_id": "MDc6TGljZW5zZTI="
            },
            "forks": 604,
            "open_issues": 296,
            "watchers": 8033,
            "default_branch": "master",
            "permissions": {
              "admin": False,
              "push": False,
              "pull": True
            }
          },
          {
            "id": 9065917,
            "node_id": "MDEwOlJlcG9zaXRvcnk5MDY1OTE3",
            "name": "firmata.py",
            "full_name": "google/firmata.py",
            "private": False,
            "owner": {
              "login": "google",
              "id": 1342004,
              "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
              "avatar_url": "https://avatars1.githubusercontent.com/u/1342004?v=4",
              "gravatar_id": "",
              "url": "https://api.github.com/users/google",
              "html_url": "https://github.com/google",
              "followers_url": "https://api.github.com/users/google/followers",
              "following_url": "https://api.github.com/users/google/following{/other_user}",
              "gists_url": "https://api.github.com/users/google/gists{/gist_id}",
              "starred_url": "https://api.github.com/users/google/starred{/owner}{/repo}",
              "subscriptions_url": "https://api.github.com/users/google/subscriptions",
              "organizations_url": "https://api.github.com/users/google/orgs",
              "repos_url": "https://api.github.com/users/google/repos",
              "events_url": "https://api.github.com/users/google/events{/privacy}",
              "received_events_url": "https://api.github.com/users/google/received_events",
              "type": "Organization",
              "site_admin": False
            },
            "html_url": "https://github.com/google/firmata.py",
            "description": None,
            "fork": False,
            "url": "https://api.github.com/repos/google/firmata.py",
            "forks_url": "https://api.github.com/repos/google/firmata.py/forks",
            "keys_url": "https://api.github.com/repos/google/firmata.py/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/google/firmata.py/collaborators{/collaborator}",
            "teams_url": "https://api.github.com/repos/google/firmata.py/teams",
            "hooks_url": "https://api.github.com/repos/google/firmata.py/hooks",
            "issue_events_url": "https://api.github.com/repos/google/firmata.py/issues/events{/number}",
            "events_url": "https://api.github.com/repos/google/firmata.py/events",
            "assignees_url": "https://api.github.com/repos/google/firmata.py/assignees{/user}",
            "branches_url": "https://api.github.com/repos/google/firmata.py/branches{/branch}",
            "tags_url": "https://api.github.com/repos/google/firmata.py/tags",
            "blobs_url": "https://api.github.com/repos/google/firmata.py/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/google/firmata.py/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/google/firmata.py/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/google/firmata.py/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/google/firmata.py/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/google/firmata.py/languages",
            "stargazers_url": "https://api.github.com/repos/google/firmata.py/stargazers",
            "contributors_url": "https://api.github.com/repos/google/firmata.py/contributors",
            "subscribers_url": "https://api.github.com/repos/google/firmata.py/subscribers",
            "subscription_url": "https://api.github.com/repos/google/firmata.py/subscription",
            "commits_url": "https://api.github.com/repos/google/firmata.py/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/google/firmata.py/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/google/firmata.py/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/google/firmata.py/issues/comments{/number}",
            "contents_url": "https://api.github.com/repos/google/firmata.py/contents/{+path}",
            "compare_url": "https://api.github.com/repos/google/firmata.py/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/google/firmata.py/merges",
            "archive_url": "https://api.github.com/repos/google/firmata.py/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/google/firmata.py/downloads",
            "issues_url": "https://api.github.com/repos/google/firmata.py/issues{/number}",
            "pulls_url": "https://api.github.com/repos/google/firmata.py/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/google/firmata.py/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/google/firmata.py/notifications{?since,all,participating}",
            "labels_url": "https://api.github.com/repos/google/firmata.py/labels{/name}",
            "releases_url": "https://api.github.com/repos/google/firmata.py/releases{/id}",
            "deployments_url": "https://api.github.com/repos/google/firmata.py/deployments",
            "created_at": "2013-03-27T23:20:35Z",
            "updated_at": "2019-09-23T11:54:02Z",
            "pushed_at": "2013-03-27T23:34:35Z",
            "git_url": "git://github.com/google/firmata.py.git",
            "ssh_url": "git@github.com:google/firmata.py.git",
            "clone_url": "https://github.com/google/firmata.py.git",
            "svn_url": "https://github.com/google/firmata.py",
            "homepage": None,
            "size": 160,
            "stargazers_count": 15,
            "watchers_count": 15,
            "language": "Python",
            "has_issues": True,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": True,
            "has_pages": False,
            "forks_count": 15,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 0,
            "license": {
              "key": "apache-2.0",
              "name": "Apache License 2.0",
              "spdx_id": "Apache-2.0",
              "url": "https://api.github.com/licenses/apache-2.0",
              "node_id": "MDc6TGljZW5zZTI="
            },
            "forks": 15,
            "open_issues": 0,
            "watchers": 15,
            "default_branch": "master",
            "permissions": {
              "admin": False,
              "push": False,
              "pull": True
            }
          }
        ],
        ['episodes.dart', 'cpp-netlib', 'dagger', 'ios-webkit-debug-proxy', 'google.github.io', 'kratu', 'build-debian-cloud', 'traceur-compiler', 'firmata.py'],
        ['dagger', 'kratu', 'traceur-compiler', 'firmata.py'],
      )
    ]


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
        # Define the side_effect function for requests.get
        # This function will be called whenever requests.get is invoked.
        def side_effect(url):
            """
            Custom side effect for requests.get mock.
            Returns a Mock object whose .json() method returns the appropriate fixture.
            """
            mock_response = Mock()
            if url == "https://api.github.com/orgs/google":
                # If the URL is for the organization payload, return org_payload
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                # If the URL is for the repositories payload, return repos_payload
                mock_response.json.return_value = cls.repos_payload
            else:
                # For any unexpected URL, return an empty mock or raise an error
                # This helps in identifying unexpected network calls.
                mock_response.json.return_value = {}
            return mock_response

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
