#!/usr/bin/env python

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials


# when triggered as cloud function, disregard topic data..
def main(_event, _context):
    gcp_service_account_key_cleaner()


def gcp_service_account_key_cleaner():
    try:
        service_account = GCPServiceAccount(
            email=os.environ["SERVICE_ACCOUNT_EMAIL"], ttl=os.environ["TIME_TO_LIVE"],
        )
    except KeyError as error:
        raise KeyError(f"environment variable not set: {error}")

    service_account.delete_old_keys()


@dataclass
class GCPServiceAccount:
    email: str
    ttl: str
    service: None = field(init=False)

    def __post_init__(self):
        credentials = GoogleCredentials.get_application_default()
        self.service = discovery.build(
            "iam", "v1", credentials=credentials, cache_discovery=False
        )

    def delete_key(self, key_name):
        request = self.service.projects().serviceAccounts().keys().delete(name=key_name)
        request.execute()

    def keys(self):
        key = f"projects/-/serviceAccounts/{self.email}"
        request = self.service.projects().serviceAccounts().keys().list(name=key)
        response = request.execute()
        return response

    def delete_old_keys(self):
        for key in self.keys()["keys"]:
            key_id = key["name"].split("/")[-1]

            if key["keyType"] == "SYSTEM_MANAGED":
                print(f"[keep]   id: {key_id} (system managed)")
                continue

            key_creation_time = datetime.strptime(
                key["validAfterTime"], "%Y-%m-%dT%H:%M:%SZ"
            )
            key_age = datetime.now() - key_creation_time

            if key_age > timedelta(minutes=int(self.ttl)):
                print(
                    f"[delete] id: {key_id}, age: {key_age} [time to live: {self.ttl}m]"
                )
                self.delete_key(key["name"])
            else:
                print(
                    f"[keep]   id: {key_id}, age: {key_age} [time to live: {self.ttl}m]"
                )


if __name__ == "__main__":
    gcp_service_account_key_cleaner()
