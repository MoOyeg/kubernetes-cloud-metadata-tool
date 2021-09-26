# pylint: disable=invalid-name
'''
Version 1: Prototype
Module runs in a kubernetes based environment and trys determine cloud metadata information for Applications.
Module does this by accessing cloud metadata urls for access.
Module is meant to be run as a deamonset on every node in the cluster.
Since each instance of the module is accessing only data for it's own node we depend on topologykeys to make sure 
a pod accesses the instance of the service running on it's own node.
'''

from asyncio import get_event_loop
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger, config
from os import getenv
from typing import Optional  # pylint: disable=import-error
from pydantic import BaseModel  # pylint: disable=import-error
from fastapi import FastAPI  # pylint: disable=import-error
from fastapi.responses import JSONResponse


class CloudMetadata(BaseModel):  # pylint: disable=too-few-public-methods
    '''Class For CloudMetadata'''
    cloudname: str = "unknown"
    hostname: str = "unknown"
    region: str = "unknown"
    availability_zone: str = "unknown"
    instance_type: str = "unknown"
    dist: str = "unknown"
    dist_version: str = "unknown"

    def todict(self):
        '''Return Class Representation as Dict'''
        return {"CLOUD_PROVIDER": self.cloudname, "CLOUD_REGION": self.region, "CLOUD_AVAILIBILITY_ZONE": self.availability_zone, "CLOUD_INSTANCE_TYPE": self.instance_type, "HOSTNAME": self.hostname
                }


# setup loggers
config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = getLogger("logger_root")

# Declare App as a FastApi Object
app = FastAPI()

# Declate metadata as the Cloudmetadata Application we will return
metadata = CloudMetadata()

# Instance Hostname is global
instance_hostname = ""

# TO-DO Streamline determine functions into 1(Probably a custom decorator)


async def determine_azure():
    '''entry to determine metadata'''
    logger.info("Starting determine_azure() Function")
    from utility_azure import determine, collectmetadata  # pylint: disable=import-outside-toplevel
    executor = ThreadPoolExecutor(max_workers=1)
    loop = get_event_loop()
    result = await loop.run_in_executor(executor, determine)
    logger.info("Ending determine_azure() Function")
    return [result, collectmetadata, "azure"]


async def determine_aws():
    '''entry to determine metadata'''
    logger.info("Starting determine_aws() Function")
    from utility_aws import determine, collectmetadata  # pylint: disable=import-outside-toplevel
    executor = ThreadPoolExecutor(max_workers=1)
    loop = get_event_loop()
    result = await loop.run_in_executor(executor, determine)
    logger.info("Ending determine_aws() Function")
    return [result, collectmetadata, "aws"]


async def determine_gcp():
    '''entry to determine metadata'''
    logger.info("Starting determine_gcp() Function")
    from utility_gcp import determine, collectmetadata  # pylint: disable=import-outside-toplevel
    executor = ThreadPoolExecutor(max_workers=1)
    loop = get_event_loop()
    result = await loop.run_in_executor(executor, determine)
    logger.info("Ending determine_gcp() Function")
    return [result, collectmetadata, "gcp"]

# Clouds that have metadata scripts available
determine_cloud_functions_list = [
    determine_aws, determine_azure, determine_gcp]

# Get Startup Information


@app.on_event("startup")
async def startup_event():
    '''Startup Function'''
    logger.info("Starting up Metadata Service")
    global instance_hostname  # pylint: disable=global-statement
    # Get environment variables
    # TO-DO Integrate redis
    #redis_url = getenv('REDIS_URL')
    instance_hostname = getenv('HOSTNAME')
    # PASSWORD = os.environ.get('API_PASSWORD')
    # app.state.redis = await init_redis_pool()


@app.get("/")
async def read_root():
    '''Application'''
    logger.info("Root Url '/' was Called")
    return {"Application": "Cloud Metadata Application,Open /docs for API information"}


@app.get("/metadata/")
async def determine_metadata(q: Optional[str] = None):
    '''determine cloud'''
    logger.info("/metadata path was called")
    if metadata.cloudname == "unknown":
        result = False
        if q is None:
            for determine_function in determine_cloud_functions_list:
                result = await determine_function()
                if result[0] is True:
                    response_data = result[1]()
                    metadata.cloudname = result[2]
                    metadata.hostname = response_data["hostname"]
                    metadata.region = response_data["region"]
                    metadata.instance_type = response_data["instanceType"]
                    metadata.availability_zone = response_data["availability_zone"]
                    break
            return JSONResponse(metadata.todict())
    else:
        return JSONResponse(metadata.todict())
