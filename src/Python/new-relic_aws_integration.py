#!/usr/bin/env python3

"""
Example usage:

    gql_client = NewRelicGQL("NR Account ID Here", "API Key Here")
    gql_client.link_account("AWS IAM Role Here", "name")
    gql_client.enable_integration(12345, "aws", "ec2", "eu-west-1")
    gql_client.unlink_account("Linked Account ID Here")

"""
import sys, json, requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class NewRelicGQL(object):
    def __init__(self, account_id, api_key, region="us"):
        try:
            self.account_id = int(account_id)
        except ValueError:
            raise ValueError("Account ID must be an integer")

        self.api_key = api_key

        if region == "us":
            self.url = "https://api.newrelic.com/graphql"
        elif region == "eu":
            self.url = "https://api.eu.newrelic.com/graphql"
        else:
            raise ValueError("Region must be one of 'us' or 'eu'")

        transport = RequestsHTTPTransport(url=self.url, use_json=True)
        transport.headers = {"api-key": self.api_key}

        try:
            self.client = Client(transport=transport, fetch_schema_from_transport=True)
        except Exception:
            self.client = Client(transport=transport, fetch_schema_from_transport=False)

    def query(self, query, timeout=None, **variable_values):
        return self.client.execute(
            gql(query), timeout=timeout, variable_values=variable_values or None
        )

    def get_license_key(self):
        """
        Fetch the license key for the NR Account
        """
        res = self.query(
            """
            query ($accountId: Int!) {
              requestContext {
                apiKey
              }
              actor {
                account(id: $accountId) {
                  licenseKey
                  id
                  name
                }
              }
            }
            """,
            accountId=self.account_id,
        )
        try:
            return res["actor"]["account"]["licenseKey"]
        except KeyError:
            return None

    def get_linked_accounts(self):
        """
        Return a list of linked accounts for the New Relic account
        """
        res = self.query(
            """
            query ($accountId: Int!) {
              actor {
                account(id: $accountId) {
                  cloud {
                    linkedAccounts {
                      id
                      externalId
                      name
                      authLabel
                    }
                  }
                }
              }
            }
            """,
            accountId=self.account_id,
        )
        try:
            return res["actor"]["account"]["cloud"]["linkedAccounts"]
        except KeyError:
            return []

    def link_account(self, role_arn, account_name):
        """
        Create a linked account (cloud integrations account)
        in the New Relic account
        """
        res = self.query(
            """
            mutation ($accountId: Int!, $accounts: CloudLinkCloudAccountsInput!){
              cloudLinkAccount (accountId: $accountId, accounts: $accounts) {
                linkedAccounts {
                  id
                  name
                }
                errors {
                    message
                }
              }
            }
            """,
            accountId=self.account_id,
            accounts={"aws": {"arn": role_arn, "name": account_name}},
        )
        try:
            return res["cloudLinkAccount"]["linkedAccounts"][0]["id"]
        except (IndexError, KeyError):
            if "errors" in res:
                print("Error while linking account with New Relic: {0}".format(res["errors"]))

            return None

    def unlink_account(self, linked_account_id):
        """
        Unlink a New Relic Cloud integrations account
        """
        res = self.query(
            """
            mutation ($accountId: Int!, $accounts: [CloudUnlinkAccountsInput!]!) {
              cloudUnlinkAccount(accountId: $accountId, accounts: $accounts) {
                errors {
                  message
                  type
                }
                unlinkedAccounts {
                  id
                  name
                }
              }
            }
            """,
            accountId=self.account_id,
            accounts={"linkedAccountId": linked_account_id},
        )

        if "errors" in res:
            print("Error while unlinking account with New Relic: {0}".format(res["errors"]))

        return res

    def enable_integration(self, linked_account_id, provider_slug, service_slug, aws_region):
        """
        Enable monitoring of a Cloud provider's service (integration)
        """
        integrations = {
            provider_slug: {
                service_slug: [{"linkedAccountId": linked_account_id, "awsRegions": aws_region}]
            }
        }
        if service_slug in ["iam", "s3", "route53", "billing"]:
            del integrations[provider_slug][service_slug][0]["awsRegions"]
            if service_slug == "iam":
                integrations[provider_slug][service_slug][0]["tagKey"] = "Region"
                integrations[provider_slug][service_slug][0]["tagValue"] = aws_region

        res = self.query(
            """
            mutation ($accountId: Int!, $integrations: CloudIntegrationsInput!) {
              cloudConfigureIntegration (
                accountId: $accountId,
                integrations: $integrations
              ) {
                integrations {
                  id
                  name
                  service {
                    id
                    name
                  }
                }
                errors {
                  linkedAccountId
                  message
                }
              }
            }
            """,
            accountId=self.account_id,
            integrations=integrations,
        )
        try:
            return res["cloudConfigureIntegration"]["integrations"][0]
        except (IndexError, KeyError):
            if "errors" in res:
                print("Error while enabling integration with New Relic:\n{0}".format(res["errors"]))

            return None


def main():
    arguments = sys.argv[1].split()

    aws_iam_role = arguments[0]
    name = arguments[1]
    aws_region = arguments[2]
    new_relic_acc_id = arguments[3]
    new_relic_api_key = arguments[4]
    services = arguments[5].split(",")

    cloud_provider = "aws"

    gql_client = NewRelicGQL(new_relic_acc_id, new_relic_api_key)
    linked_accounts = gql_client.get_linked_accounts()

    if aws_iam_role != "unlink":
        linked_acc_id = gql_client.link_account(aws_iam_role, name)
        id = linked_accounts[0]["id"] if linked_accounts else linked_acc_id
        for s in services:
            print(gql_client.enable_integration(id, cloud_provider, s, aws_region))

    # Unlink the integration on terraform-destroy
    if linked_accounts and aws_iam_role == "unlink":
        print(gql_client.unlink_account(linked_accounts[0]["id"]))


if __name__ == "__main__":
    main()