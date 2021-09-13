# pylint: disable=logging-format-interpolation
'''Module provides utility functions for Azure Metadata Collection'''

import sys
import logging  # pylint: disable=import-error
import requests  # pylint: disable=import-error


METADATA_URL = "169.254.169.254"
TIMEOUT = 2
HEADER_METADATA = {"Metadata": "true"}
AZURE_API_VERSION = "2021-02-01"
logger = logging.getLogger(__name__)


def determine():
    '''Function to Try Call Azure Metadata URL'''
    logger.info("Run Determine if Azure Cloud")
    try:
        result = requests.get(
            "http://{0}/metadata/instance/compute/azEnvironment?api-version={1}&format=text".
            format(METADATA_URL, AZURE_API_VERSION), headers=HEADER_METADATA, timeout=TIMEOUT)
    except Exception as error:  # pylint: disable=broad-except
        logger.exception("Error in determine foundtion for {0} module, see exception stack\n:{1}"
                         .format(__name__, error))
        return False
    logger.info("End Determine if Azure Cloud")
    if result.status_code == 200:
        return "azure" in result.text.lower()
    return False


def collectmetadata(query=None):
    '''Function to collect metadata.
       Present Version tries to collect data described, future will collect all
    '''
    logger.info("Run CollectMetadata for Azure Cloud")

    if query is None:
        # Get Region from metadata
        try:
            result = requests.get(
                "http://{0}/metadata/instance/compute/location?api-version={1}&format=text".
                format(METADATA_URL, AZURE_API_VERSION), headers=HEADER_METADATA, timeout=TIMEOUT)
        except Exception as error:  # pylint: disable=broad-except
            logger.exception("Error in Collect Metadata function for {0} module, see exception stack\n:{1}"
                             .format(__name__, error))
        region = result.text

        # Get Hostname from metadata
        try:
            result = requests.get(
                "http://{0}/metadata/instance/compute/name?api-version={1}&format=text".
                format(METADATA_URL, AZURE_API_VERSION), headers=HEADER_METADATA, timeout=TIMEOUT)
        except Exception as error:  # pylint: disable=broad-except
            logger.exception("Error in Collect Metadata function for {0} module, see exception stack\n:{1}"
                             .format(__name__, error))
        hostname = result.text

        # Get InstanceType from metadata
        try:
            result = requests.get(
                "http://{0}/metadata/instance/compute/vmSize?api-version={1}&format=text".
                format(METADATA_URL, AZURE_API_VERSION), headers=HEADER_METADATA, timeout=TIMEOUT)
        except Exception as error:  # pylint: disable=broad-except
            logger.exception("Error in Collect Metadata function for {0} module, see exception stack\n:{1}"
                             .format(__name__, error))
        instancetype = result.text

        # Get Zone from metadata
        try:
            result = requests.get(
                "http://{0}/metadata/instance/compute/zone?api-version={1}&format=text".
                format(METADATA_URL, AZURE_API_VERSION), headers=HEADER_METADATA, timeout=TIMEOUT)
        except Exception as error:  # pylint: disable=broad-except
            logger.exception("Error in Collect Metadata function for {0} module, see exception stack\n:{1}"
                             .format(__name__, error))
        zone = result.text
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
        logger.info("We are running on Azure")
        collectmetadata()
    else:
        logger.info("Not Azure")
