""" Country Pilots generator """
import json
import os
from typing import Any, Dict, List

import boto3
import botocore
import html5lib
import yaml
from geojson_pydantic.geometries import Polygon
from geojson_pydantic.types import BBox, Position
from pydantic import BaseModel, ValidationError, constr


BASE_PATH = os.path.abspath('.')
config = yaml.load(open(f"{BASE_PATH}/config.yml", "r"), Loader=yaml.FullLoader)

INPUT_FILEPATH = os.path.join(BASE_PATH, "country_pilots")

OUTPUT_FILENAME = f"{os.environ.get('STAGE', 'local')}-country-pilots-metadata.json"


class CountryPilot(BaseModel):

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


def create_json():
    """
    Returns:
    -------
    (string): JSON object containing a list of all Country Pilots. This is the output of the 
        `/country_pilots` endpoint.
    """

    country_pilots = _gather_data(
        dirpath=INPUT_FILEPATH, 
        visible_country_pilots=config['COUNTRY_PILOTS']
    )

    bucket_name = os.environ.get("DATA_BUCKET_NAME", config.get('BUCKET'))
    s3 = boto3.resource("s3")
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': os.environ.get('AWS_REGION', 'us-east-1')
            }
        )
    except botocore.exceptions.ClientError:
        # this exception is thrown if the bucket already exists in any region other than us-east-1
        pass

    s3.Bucket(bucket_name).put_object(
        Body=json.dumps(country_pilots), Key=OUTPUT_FILENAME, ContentType="application/json",
    )

    return country_pilots


def _gather_data(dirpath: str, visible_country_pilots: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Gathers site info and creates a JSON structure from it"""
    parser = html5lib.HTMLParser(strict=True)

    results = []
    for path in os.walk(dirpath):
        cp = path[0].rsplit("/", 1)[1]
        if visible_country_pilots and cp not in visible_country_pilots:
            continue
        with open(os.path.join(dirpath, cp, "site.json"), "r") as f:
            entity = json.loads(f.read())
            try:
                CountryPilot(**entity)
            except ValidationError as e:
                print(f"Error processing site.json for {cp}: {e.json()}")
                raise e
        with open(os.path.join(dirpath, cp, "summary.html"), "r") as f:
            summary = f.read()
            parser.parseFragment(summary)
            entity["summary"] = summary
        results.append(entity)    
    return {"country_pilots" : results }

if __name__ == "__main__":
    print(json.dumps(create_json()))
