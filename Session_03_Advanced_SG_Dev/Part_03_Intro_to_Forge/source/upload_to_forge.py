
import base64
import json
import os
import requests
import time

import sgtk

logger = sgtk.platform.get_logger(__name__)

HookBaseClass = sgtk.get_hook_baseclass()

# ---- FORGE URLs

################################################################################
# demo-specific values

# must be of the form  [-_.a-z0-9]{3,128}
FORGE_BUCKET_NAME = "sg_dev_day_demo_bucket"

################################################################################
# Forge endpoints

# base url
FORGE_DEV_SITE = "https://developer.api.autodesk.com"

# functional endpoints
FORGE_AUTHENTICATION = FORGE_DEV_SITE + "/authentication/v1/authenticate"

FORGE_BUCKETS = FORGE_DEV_SITE + "/oss/v2/buckets"
FORGE_DEMO_BUCKET = FORGE_BUCKETS + "/{bucket}".format(bucket=FORGE_BUCKET_NAME)
FORGE_BUCKET_DETAILS = FORGE_DEMO_BUCKET + "/details"

FORGE_OBJECT_UPLOAD = FORGE_DEMO_BUCKET + "/objects/{object_name}"

FORGE_DESIGNDATA = FORGE_DEV_SITE + "/modelderivative/v2/designdata"
FORGE_DESIGNDATA_JOB = FORGE_DESIGNDATA + "/job"
FORGE_DESIGNDATA_MANIFEST = FORGE_DESIGNDATA + "/{base64_urn}/manifest"

################################################################################


class UploadToForgePlugin(HookBaseClass):

    @property
    def icon(self):
        return ""

    @property
    def description(self):
        return """
        <p>
        This plugin submits a published model to forge and updates
        information in SG to allow it to be reviewed.
        </p>
        """

    @property
    def settings(self):
        return {}

    @property
    def item_filters(self):
        # this means the accept() method will run for all items to check for
        # the path and if it is an 'obj' file.
        return ["*"]

    def accept(self, settings, item):

        is_accepted = False

        # NOTE: this works in conjunction with the default collector for
        # standalone publishes. When a file is dragged and dropped or browsed
        # to in the UI, a 'path' property is set with the full path to the file.
        path = item.get_property("path")
        if path and path.endswith(".obj"):
            is_accepted = True

        return {
            "accepted": is_accepted,
            "checked": True
        }

    def validate(self, settings, item):

        # Ensure the publish is to an Asset context
        if not item.context.entity or not item.context.entity.get("type") == "Asset":
            self.logger.error("Requires publishing to an asset context.")
            return False

        return True

    def publish(self, settings, item):

        # NOTE: While this example is for the standalone publisher, you could
        # implement this within a DCC and do the export of the geometry here
        # before uploading.

        # submit the item's path to the forge broker
        model_path = item.properties.get("path")

        if not os.path.exists(model_path):
            self.logger.warning(
                "Path was found on the item, but does not exists on disk."
            )

        # validation ensured this was an asset context
        asset_id = item.context.entity.get("id")

        # ---- upload to forge

        self.logger.info("Uploading model to forge...")
        forge_urn = submit_to_forge(
            model_path,
            item.properties["sg_publish_data"]["name"],
        )
        self.logger.info("Upload complete.")

        # ---- update the asset in SG

        self.logger.info("Updating SG with forge URN")
        self.sgtk.shotgun.update(
            "Asset",
            asset_id,
            {
                # TODO: this requires a "forge_urn" custom field on Asset entities
                "sg_forge_urn": forge_urn
            }
        )
        self.logger.info("Shotgun has been updated.")

    def finalize(self, settings, item):
        pass

def submit_to_forge(model_path, object_name):

    # TODO: this is executing in the main thread. A better solution would
    # be to run this upload as a separate process that updates SG once the
    # upload/conversion is complete (time depends on file size, forge server
    # load, etc.). This code should be used for reference only.

    forge_token = get_forge_access_token()
    if not ensure_forge_bucket_exists(forge_token):
        raise sgtk.TankError("Failed to create Forge bucket.")

    # upload the model
    with open(model_path, 'rb') as f:
        result = requests.put(
            FORGE_OBJECT_UPLOAD.format(object_name=object_name),
            headers={
                "Authorization": "Bearer {access_token}".format(
                    access_token=forge_token
                ),
                "Content-Type": "application/octet-stream",
            },
            data=f
        )
        result.raise_for_status()

    # if we're here, upload was successful. get the URN for the model
    result_data = result.json()
    model_urn = result_data["objectId"]

    logger.debug("Model uploaded: %s" % (model_urn,))

    model_urn_base64 = base64.b64encode(model_urn).decode('utf-8').rstrip("=")
    logger.debug("Model URN (base 64): %s" % (model_urn_base64,))

    logger.debug("Starting conversion to SVF...")

    # convert to SVF format on the server. this is required for viewing the
    # model using the forge viewer API
    result = requests.post(
        FORGE_DESIGNDATA_JOB,
        headers={
            "Authorization": "Bearer {access_token}".format(
                access_token=forge_token
            ),
        },
        json={
            "input": {
                "urn": model_urn_base64
            },
            "output": {
                "formats": [
                    {
                        "type": "svf",
                        "views": ["2d", "3d"]
                    }
                ]
            }
        }
    )
    result.raise_for_status()

    # TODO: You could wait for the proper status before updating SG. Again,
    # this is not ideal for the main publish thread. You might consider a
    # separate service to handle checking for upload status and updating SG.
    # Leaving this here for reference.

    """
    # poll for completion...
    logger.debug("Conversion submitted. Polling for completion...")

    status = None
    while status not in ["success", "failed", "timeout"]:
        result = requests.get(
            FORGE_DESIGNDATA_MANIFEST.format(base64_urn=model_urn_base64),
            headers={
                "Authorization": "Bearer {access_token}".format(
                    access_token=forge_token
                )
            }
        )
        result.raise_for_status()
        result_data = result.json()
        status = result_data["status"]
        logger.debug("Conversion status: %s" % (status,))

        time.sleep(2)

    # the last result is the one with all the info
    logger.debug(json.dumps(result.json(), indent=4, sort_keys=True))
    """

    return model_urn_base64


def ensure_forge_bucket_exists(access_token):

    # see if the bucket already exists...
    result = requests.get(
        FORGE_BUCKET_DETAILS.format(bucket_name=FORGE_BUCKET_NAME),
        headers={
            "Authorization": "Bearer {access_token}".format(
                access_token=access_token
            )
        }
    )
    if result.status_code == requests.codes.ok:
        return True

    # bucket doesn't exists. create it
    result = requests.post(
        FORGE_BUCKETS,
        json={
            "bucketKey": FORGE_BUCKET_NAME,
            "policyKey": "persistent"
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {access_token}".format(
                access_token=access_token
            )
        }
    )

    if result.status_code != requests.codes.ok:
        logger.error("Failed to create forge bucket: %s" % (FORGE_BUCKET_NAME,))
        logger.error("ERROR: " + result.text)
        return False

    return True


def get_forge_access_token():

    # TODO: You will first need to register your app with Forge. Once you've
    # done that, you can test your code by including the id/secret here. For
    # production though, you'll want to externalize these values and access them
    # here.
    client_id = 1234      # TODO
    client_secret = 1234  # TODO

    result = requests.post(
        FORGE_AUTHENTICATION,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": "data:read data:write bucket:create bucket:read"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    result.raise_for_status()

    return result.json()["access_token"]
