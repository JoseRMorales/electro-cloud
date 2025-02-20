import json
import logging
import os

import requests
from dotenv import load_dotenv

from .energy_analysis_lib.constants import PATHS

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

locations_cache = os.path.join(PATHS["locations"], "locations.json")
production_monthly_cache = os.path.join(PATHS["production"], "monthly.json")
production_hourly_cache = os.path.join(PATHS["production"], "hourly.json")


def get_coordinates(location: str) -> (str, str):
    """
    Gets the coordinates of a location using the positionstack API

    :param locations: location to get the coordinates
    :return: latitude and longitude of the location
    """
    # Create the locations folder if it does not exist
    if not os.path.exists(PATHS["locations"]):
        os.makedirs(PATHS["locations"])

    # Load the locations saved or create the file
    try:
        with open(locations_cache, "r") as f:
            locations_dict = json.load(f)
    except FileNotFoundError:
        locations_dict = {}
        with open(locations_cache, "w") as f:
            json.dump(locations_dict, f)

    # Check if the location is already saved
    if location in locations_dict:
        latitude, longitude = locations_dict[location]
        logging.info("Location found in cache")
        return latitude, longitude

    # If the location is not saved, get the coordinates from the API
    url = "http://api.positionstack.com/v1/forward"

    # Get Access Key from .env file
    params = {"access_key": os.getenv("POSITIONSTACK_ACCESS_KEY"), "query": location}

    logging.info("Getting coordinates from API")

    # Get the response from the API
    response = requests.get(url, params=params)
    response_json = response.json()

    # Check if the response is correct
    if response.status_code != 200:
        logging.error("Error getting coordinates from API")
        logging.error(response_json)
        raise ValueError("Error getting coordinates from API")

    # Get the coordinates from the response
    latitude = response_json["data"][0]["latitude"]
    longitude = response_json["data"][0]["longitude"]

    # Save the coordinates in the cache
    locations_dict[location] = (latitude, longitude)
    with open(locations_cache, "w") as f:
        json.dump(locations_dict, f)

    logging.info("Location found in API")
    return latitude, longitude


def get_monthly_production(
    location: str,
    peakpower: float,
    mountingplace: str,
    loss: float,
    angle: float,
    aspect: float,
    analysisId: str,
) -> None:
    """
    Gets the monthly production of a pv system in a location

    :param location: location of the pv system
    :param peakpower: peak power of the pv system
    :param mountingplace: mounting place of the pv system. "free" or "building"
    :param loss: loss of the pv system
    :param angle: angle of the pv system
    :param aspect: azimuth of the pv system
    :param analysisId: id of the system
    :return: None
    """
    # Get the coordinates of the location
    latitude, longitude = get_coordinates(location)

    # Create the production folder if it does not exist
    if not os.path.exists(PATHS["production"]):
        os.makedirs(PATHS["production"])

    # Load the production saved or create the file
    try:
        with open(production_monthly_cache, "r") as f:
            production_dict = json.load(f)
    except FileNotFoundError:
        production_dict = {}
        with open(production_monthly_cache, "w") as f:
            json.dump(production_dict, f)

    # Check if the production is already saved
    if analysisId in production_dict:
        logging.info("Production found in cache")
        return

    # If the production is not saved, get the production from the API
    url = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"

    params = {
        "lat": latitude,
        "lon": longitude,
        "peakpower": peakpower,
        "loss": loss,
        "mountingplace": mountingplace,
        "angle": angle,
        "aspect": aspect,
        "outputformat": "csv",
    }

    logging.info("Getting monthly production from API")

    # Get the response from the API
    response = requests.get(url, params=params)

    # Check if the response is correct
    if response.status_code != 200:
        logging.error("Error getting production from API")
        logging.error(response.text)
        raise ValueError("Error getting production from API")

    # Set true if the production is saved
    production_dict[analysisId] = True
    with open(production_monthly_cache, "w") as f:
        json.dump(production_dict, f)

    # Create directory if it does not exist
    if not os.path.exists(PATHS["production_monthly"]):
        os.makedirs(PATHS["production_monthly"])

    # Save the production in a file
    with open(os.path.join(PATHS["production_monthly"], analysisId + ".csv"), "w") as f:
        f.write(response.text)

    logging.info("Production found in API")
    return


def get_hourly_production(
    location: str,
    peakpower: float,
    mountingplace: str,
    loss: float,
    angle: float,
    aspect: float,
    analysisId: str,
) -> None:
    """
    Gets the hourly production of a pv system in a location

    :param location: location of the pv system
    :param peakpower: peak power of the pv system
    :param mountingplace: mounting place of the pv system. "free" or "building"
    :param loss: loss of the pv system
    :param angle: angle of the pv system
    :param aspect: azimuth of the pv system
    :param analysisId: id of the system
    :return: None
    """
    # Get the coordinates of the location
    latitude, longitude = get_coordinates(location)

    # Create the production folder if it does not exist
    if not os.path.exists(PATHS["production"]):
        os.makedirs(PATHS["production"])

    # Load the production saved or create the file
    try:
        with open(production_hourly_cache, "r") as f:
            production_dict = json.load(f)
    except FileNotFoundError:
        production_dict = {}
        with open(production_hourly_cache, "w") as f:
            json.dump(production_dict, f)

    # Check if the production is already saved
    if analysisId in production_dict:
        logging.info("Production found in cache")
        return

    # If the production is not saved, get the production from the API
    url = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"

    params = {
        "lat": latitude,
        "lon": longitude,
        "peakpower": peakpower,
        "loss": loss,
        "mountingplace": mountingplace,
        "angle": angle,
        "aspect": aspect,
        "startyear": 2020,
        "endyear": 2020,
        "pvcalculation": 1,
        "outputformat": "csv",
    }

    logging.info("Getting hourly production from API")

    # Get the response from the API
    response = requests.get(url, params=params)

    # Check if the response is correct
    if response.status_code != 200:
        logging.error("Error getting production from API")
        logging.error(response.text)
        raise ValueError("Error getting production from API")

    # Set true if the production is saved
    production_dict[analysisId] = True
    with open(production_hourly_cache, "w") as f:
        json.dump(production_dict, f)

    # Create directory if it does not exist
    if not os.path.exists(PATHS["production_hourly"]):
        os.makedirs(PATHS["production_hourly"])

    # Save the production in a file
    with open(os.path.join(PATHS["production_hourly"], analysisId + ".csv"), "w") as f:
        f.write(response.text)
        logging.info("Written hourly production to file")

    logging.info("Production found in API")
    return
