# pylint: disable=logging-format-interpolation
'''Module provides utility functions for AWS Metadata Collection'''

import sys
import logging  # pylint: disable=import-error
import requests  # pylint: disable=import-error


METADATA_URL = "169.254.169.254"
TIMEOUT = 2
HEADER_TOKEN_TTL = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
logger = logging.getLogger(__name__)


def determine():
    '''Function to Try Call AWS Metadata URL and get token'''
    logger.info("Run Determine if AWS Cloud")
    try:
        result = requests.put(
            "http://{0}/latest/api/token".format(METADATA_URL), headers=HEADER_TOKEN_TTL, timeout=TIMEOUT)
    except Exception as error:  # pylint: disable=broad-except
        logger.exception("Error in determine fundtion for {0} module, see exception stack\n:{1}"
                         .format(__name__, error))
        return False
    logger.info("End Determine if AWS Cloud")
    return result.status_code == 200
    # return True


def collectmetadata(query=None):
    '''Function to collect metadata.
       Present Version tries to collect data described, future will collect all
    '''
    logger.info("Run CollectMetadata for AWS Cloud")
    try:
        result = requests.put("http://{0}/latest/api/token".format(
            METADATA_URL), headers=HEADER_TOKEN_TTL, timeout=TIMEOUT)
    except Exception as error:  # pylint: disable=broad-except
        logger.exception("Error in determine function for {0} module, see exception stack\n:{1}"
                         .format(__name__, error))
        return {}
    aws_token = result.text
    header_token = {"X-aws-ec2-metadata-token": aws_token}

    if query is None:
        # Get Metadata json Document
        try:
            result = requests.get("http://{0}/latest/dynamic/instance-identity/document".format(
                METADATA_URL), headers=header_token, timeout=TIMEOUT)
        except Exception as error:  # pylint: disable=broad-except
            logger.exception("Error in determine function for {0} module, see exception stack\n:{1}"
                             .format(__name__, error))
        json_doc = result.json()

        # Get Metadata Hostname
        try:
            result = requests.get("http://{0}//latest/meta-data/hostname".format(
                METADATA_URL), headers=header_token, timeout=TIMEOUT)
        except Exception as error:  # pylint: disable=broad-except
            logger.exception("Error in determine function for {0} module, see exception stack\n:{1}"
                             .format(__name__, error))
        hostname = result.text
        metadata = {"hostname": hostname, "region": json_doc["region"],
                    "instanceType": json_doc["instanceType"], "availability_zone":  json_doc["availabilityZone"]}
        return metadata
    # TO-DO Write logic for passing query to metadata # pylint: disable=fixme
    return {}


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info("Running as executable")
    if determine():
        logger.info("We are running on AWS")
        collectmetadata()
    else:
        logger.info("Not AWS")
