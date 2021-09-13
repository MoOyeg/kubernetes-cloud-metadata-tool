# pylint: disable=logging-format-interpolation
'''Module provides utility functions for GCP Metadata Collection'''

import sys
import logging  # pylint: disable=import-error
import requests  # pylint: disable=import-error


METADATA_URL = "metadata.google.internal"
TIMEOUT = 2
HEADER_METADATA = {"Metadata-Flavor": "Google"}
logger = logging.getLogger(__name__)


def determine():
    '''Function to Try Call GCP Metadata URL'''
    logger.info("Run Determine if GCP Cloud")
    try:
        result = requests.get(
            "http://{0}/computeMetadata/v1/instance".
            format(METADATA_URL), headers=HEADER_METADATA, timeout=TIMEOUT)
    except Exception as error:  # pylint: disable=broad-except
        logger.exception("Error in determine foundtion for {0} module, see exception stack\n:{1}"
                         .format(__name__, error))
        return False
    logger.info("End Determine if GCP Cloud")
    return result.status_code == 200


def collectmetadata(query=None):
    '''Function to collect metadata.
       Present Version tries to collect data described, future will collect all
    '''
    logger.info("Run CollectMetadata for GCP Cloud")

    if query is None:
        # Get Region from metadata
        try:
            result = requests.get(
                "http://{0}/computeMetadata/v1/instance/zone".
                format(METADATA_URL), headers=HEADER_METADATA, timeout=TIMEOUT)
        except Exception as error:  # pylint: disable=broad-except
            logger.exception("Error in Collect Metadata function for {0} module, see exception stack\n:{1}"
                             .format(__name__, error))
        zone = result.text.split("/")[-1]
        region = zone[0:-2]

        # Get Hostname from metadata
        try:
            result = requests.get(
                "http://{0}/computeMetadata/v1/instance/hostname".
                format(METADATA_URL), headers=HEADER_METADATA, timeout=TIMEOUT)
        except Exception as error:  # pylint: disable=broad-except
            logger.exception("Error in Collect Metadata function for {0} module, see exception stack\n:{1}"
                             .format(__name__, error))
        hostname = result.text

        # Get InstanceType from metadata
        try:
            result = requests.get(
                "http://{0}/computeMetadata/v1/instance/machine-type".
                format(METADATA_URL), headers=HEADER_METADATA, timeout=TIMEOUT)
        except Exception as error:  # pylint: disable=broad-except
            logger.exception("Error in Collect Metadata function for {0} module, see exception stack\n:{1}"
                             .format(__name__, error))
        instancetype = result.text.split("/")[-1]
        metadata = {"hostname": hostname, "region": region,
                    "availability_zone": zone, "instanceType": instancetype}
        return metadata
    # TO-DO Write logic for passing query to metadata # pylint: disable=fixme
    return {}


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info("Running as executable")
    if determine():
        logger.info("We are running on GCP")
        print(collectmetadata())
    else:
        logger.info("Not GCP")
