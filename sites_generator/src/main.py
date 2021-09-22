""" Sites generator """
import json
import os
from typing import Any, Dict, List

import boto3
import html5lib
import yaml
from geojson_pydantic.geometries import Polygon
from geojson_pydantic.types import BBox, Position
from pydantic import BaseModel, ValidationError, constr


BASE_PATH = os.path.abspath('.')
config = yaml.load(open(f"{BASE_PATH}/config.yml", "r"), Loader=yaml.FullLoader)

SITES_INPUT_FILEPATH = os.path.join(BASE_PATH, "sites")

SITES_OUTPUT_FILENAME = f"{os.environ.get('STAGE', 'local')}-site-metadata.json"


class Site(BaseModel):

    id: constr(min_length=3)
    label: constr(min_length=3)
    center: Position
    polygon: Polygon
    bounding_box: BBox
    indicators: List[str]

    def to_dict(self, **kwargs):
        return self.dict(by_alias=True, exclude_unset=True, **kwargs)

    def to_json(self, **kwargs):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)


def create_sites_json():
    """
    Returns:
    -------
    (string): JSON object containing a list of all sites. This is the output of the 
        `/sites` endpoint.
    """

    sites = _gather_data(dirpath=SITES_INPUT_FILEPATH, visible_sites=config['SITES'])

    s3 = boto3.resource("s3")
    bucket = s3.create_bucket(Bucket=os.environ.get("DATA_BUCKET_NAME", config.get('BUCKET')))
    bucket.put_object(
        Body=json.dumps(sites), Key=SITES_OUTPUT_FILENAME, ContentType="application/json",
    )

    return sites


def _gather_data(dirpath: str, visible_sites: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Gathers site info and creates a JSON structure from it"""
    parser = html5lib.HTMLParser(strict=True)

    results = []
    for path in os.walk(dirpath):
        site = path[0].rsplit("/", 1)[1]
        if visible_sites and site not in visible_sites and site != "global":
            continue
        with open(os.path.join(dirpath, site, "site.json"), "r") as f:
            entity = json.loads(f.read())
            if site != "global":
                try:
                    Site(**entity)
                except ValidationError as e:
                    print(f"Error processing site.json for {site}: {e.json()}")
                    raise e
        with open(os.path.join(dirpath, site, "summary.html"), "r") as f:
            summary = f.read()
            parser.parseFragment(summary)
            entity["summary"] = summary
        results.append(entity)    
    return {"sites" : results }

if __name__ == "__main__":
    print(json.dumps(create_sites_json()))
