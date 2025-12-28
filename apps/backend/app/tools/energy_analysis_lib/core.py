import json
import os
import uuid
from io import StringIO
from typing import Optional

import tools.energy_analysis_lib.energy as energy
import tools.energy_analysis_lib.solar as solar
import tools.pvgis_api_wrapper as api
from tools.energy_analysis_lib.energy import (
    parse_consumption_file,
    parse_consumption_file_with_generation,
)
from tools.utils import logger

from .constants import PATHS


def _save_metadata(analysisId: str, metadata: dict) -> None:
    """
    Save metadata for an analysis.
    """
    if not os.path.exists(PATHS["metadata"]):
        os.makedirs(PATHS["metadata"])

    metadata_path = os.path.join(PATHS["metadata"], f"{analysisId}.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)


def _get_metadata(analysisId: str) -> dict:
    """
    Get metadata for an analysis.
    """
    metadata_path = os.path.join(PATHS["metadata"], f"{analysisId}.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            return json.load(f)
    return {}


async def solar_calculation(
    consumption_file: Optional[StringIO],
    location: str,
    roofs: list[dict],
    name: Optional[str] = None,
) -> str:
    """
    Generate all the data necessary for the solar analysis.

    :param consumption_file: The consumption file (optional)
    :param location: The location of the solar panels
    :param roofs: List of roof configurations (peakpower, mountingplace, loss, angle, aspect)

    :return: The id of the analysis
    """

    # Create a unique id for the analysis repeatable by the parameters
    # Sort roofs to ensure ID consistency
    sorted_roofs = sorted(roofs, key=lambda x: str(x))
    analysisId = str(
        uuid.uuid3(
            uuid.NAMESPACE_DNS,
            location + json.dumps(sorted_roofs)
        )
    )

    # Save metadata
    if name:
        _save_metadata(analysisId, {"name": name})

    # Parse the consumption file if provided
    if consumption_file:
        energy.parse_consumption_file(consumption_file, analysisId)

    # Process each roof and aggregate production
    all_hourly_productions = []
    all_monthly_productions = []

    for i, roof in enumerate(roofs):
        # Create a temporary ID for this roof's raw data
        roof_id = f"{analysisId}_roof_{i}"
        
        # Get the production data from api for this roof
        await api.get_monthly_production(
            location, 
            roof["peakpower"], 
            roof["mountingplace"], 
            roof["loss"], 
            roof["angle"], 
            roof["aspect"], 
            roof_id
        )
        await api.get_hourly_production(
            location, 
            roof["peakpower"], 
            roof["mountingplace"], 
            roof["loss"], 
            roof["angle"], 
            roof["aspect"], 
            roof_id
        )

        # Parse and load production data for this roof
        hourly_df = solar.load_and_parse_hourly(roof_id)
        monthly_df = solar.load_and_parse_monthly(roof_id)
        
        all_hourly_productions.append(hourly_df)
        all_monthly_productions.append(monthly_df)

    # Aggregate productions
    aggregated_hourly = solar.aggregate_hourly(all_hourly_productions, analysisId)
    aggregated_monthly = solar.aggregate_monthly(all_monthly_productions, analysisId)

    # Generate graphs and calculations
    # Generate consumption vs production plot (handles missing consumption)
    solar.consumption_production_chart(analysisId)

    # Calculate the self consumption and plot monthly (handles missing consumption)
    solar.plot_self_consumption_monthly(analysisId)

    # Get the time slot consumption (handles missing consumption)
    solar.process_results_time_slot_solar(analysisId)

    return analysisId


def get_monthly_production(analysisId: str) -> bytes:
    """
    Return the monthly production data to the api.

    :param analysisId: The id of the analysis
    """
    try:
        production_file = open(
            os.path.join(PATHS["production_parsed_monthly"], f"{analysisId}.csv"), "rb"
        )
    except FileNotFoundError:
        logger.error("The production file does not exist")
        raise FileNotFoundError("The production file does not exist")

    return production_file.read()


def get_monthly_consumption(analysisId: str) -> bytes:
    """
    Return the monthly consumption data to the api.

    :param analysisId: The id of the analysis
    """
    try:
        consumption_file = open(
            os.path.join(PATHS["consumption_parsed_monthly"], f"{analysisId}.csv"), "rb"
        )
    except FileNotFoundError:
        logger.error("The consumption file does not exist")
        raise FileNotFoundError("The consumption file does not exist")

    return consumption_file.read()


def get_monthly_consumption_production_plot(analysisId: str) -> bytes:
    """
    Return the monthly consumption vs production plot to the api.

    :param analysisId: The id of the analysis
    """
    try:
        consumption_production_plot = open(
            os.path.join(
                PATHS["plots_consumption_production_chart"], f"{analysisId}.png"
            ),
            "rb",
        )

    except FileNotFoundError:
        logger.error("The consumption vs production plot file does not exist")
        raise FileNotFoundError(
            "The consumption vs production plot file does not exist"
        )

    return consumption_production_plot.read()


def get_results_monthly_plots(analysisId: str) -> [bytes]:
    """
    Return the monthly results plots to the api.

    :param analysisId: The id of the analysis
    """
    results_monthly = []
    try:
        for month in range(1, 13):
            results_monthly.append(
                open(
                    os.path.join(PATHS["plots_monthly"], f"{analysisId}_{month}.png"),
                    "rb",
                )
            )
    except FileNotFoundError:
        logger.error("The monthly results plots do not exist")
        raise FileNotFoundError("The monthly results plots do not exist")
    return results_monthly


def get_self_percent_ratios(analysisId: str) -> dict:
    """
    Return the self consumption percentages and the averageto the api.

    :param analysisId: The id of the analysis
    """

    monthly_ratios, average = solar.get_self_consumption_ratio(analysisId)

    return {"monthly_ratios": monthly_ratios, "average": average}


def get_results_time_slot_solar(analysisId: str) -> bytes:
    """
    Return the time slot solar results to the api.

    :param analysisId: The id of the analysis
    """
    try:
        results_time_slot_solar = open(
            os.path.join(PATHS["time_slots"], f"{analysisId}.csv"), "rb"
        )
    except FileNotFoundError:
        logger.error("The time slot results after solar do not exist")
        raise FileNotFoundError("The time slot results after solar do not exist")

    return results_time_slot_solar.read()


"""
/api/energy methods
"""


def process_consumption_file(consumption_file: bytes, name: Optional[str] = None) -> str:
    """
    Process the consumption file. If some exception is raised,

    :param consumption_file: consumption file
    :return: None
    """
    logger.info("Processing consumption file")

    analysisId = str(uuid.uuid4())

    # Save metadata
    if name:
        _save_metadata(analysisId, {"name": name})

    try:
        # Read StringIO object into a string
        consumption_file_str = consumption_file.getvalue()

        # Split string into rows
        rows = consumption_file_str.split("\n")

        # If first row contains a "GENERACION Wh" string, then it is a solar file
        if "GENERACION Wh" in rows[0]:
            parse_consumption_file_with_generation(consumption_file, analysisId)
        else:
            parse_consumption_file(consumption_file, analysisId)

        return analysisId
    except Exception as e:
        logger.error(e)
        raise e


def get_results_time_slot_energy_by_id(analysisId: str) -> bytes:
    """
    Return the time slot energy results to the api.

    :param analysisId: The id of the analysis
    """
    # Check if the results exist in output folder
    time_slot_energy_results = None
    try:
        time_slot_energy_results = open(
            os.path.join(PATHS["time_slots"], f"{analysisId}.csv"), "rb"
        ).read()
    except FileNotFoundError:
        logger.info("The time slot energy results do not exist, calculating")

        hourly = None
        # Check if the hourly consumption file exists
        hourly = open(
            os.path.join(PATHS["consumption_parsed_hourly"], f"{analysisId}.csv"), "rb"
        )
        # If first row contains a "Generation" column, then it is a solar file
        if "Generation" in hourly.readline().decode("utf-8"):
            time_slot_energy_results = (
                energy.process_results_time_slot_energy_with_generation(analysisId)
            )
        else:
            time_slot_energy_results = energy.process_results_time_slot_energy(
                analysisId
            )
    return time_slot_energy_results


def get_results_time_slot_energy() -> list:
    """
    Return all the analysisId
    """
    # Create the path if it does not exist
    if not os.path.exists(PATHS["consumption_parsed_hourly"]):
        os.makedirs(PATHS["consumption_parsed_hourly"])
    # Check csv files in "parsed_hourly" folder
    files = os.listdir(os.path.join(PATHS["consumption_parsed_hourly"]))
    results = []
    for file in files:
        # Check if the file is a csv file
        if file.endswith(".csv"):
            # Remove the extension
            analysisId = file[:-4]
            # Get date from the file
            time = os.path.getctime(
                os.path.join(PATHS["consumption_parsed_hourly"], file)
            )
            metadata = _get_metadata(analysisId)
            results.append({
                "analysisId": analysisId, 
                "created_at": time,
                "name": metadata.get("name")
            })

    return results


def delete_results_time_slot_energy_by_id(analysisId: str):
    """
    Delete the time slots analysis.

    :param analysisId: The id of the analysis
    """
    # Delet if exists in folders 'parsed_hourly', 'parsed_monthly' and 'time_slots'
    if os.path.exists(
        os.path.join(PATHS["consumption_parsed_hourly"], f"{analysisId}.csv")
    ):
        os.remove(os.path.join(PATHS["consumption_parsed_hourly"], f"{analysisId}.csv"))

    if os.path.exists(
        os.path.join(PATHS["consumption_parsed_monthly"], f"{analysisId}.csv")
    ):
        os.remove(
            os.path.join(PATHS["consumption_parsed_monthly"], f"{analysisId}.csv")
        )

    if os.path.exists(os.path.join(PATHS["time_slots"], f"{analysisId}.csv")):
        os.remove(os.path.join(PATHS["time_slots"], f"{analysisId}.csv"))

    if os.path.exists(os.path.join(PATHS["metadata"], f"{analysisId}.json")):
        os.remove(os.path.join(PATHS["metadata"], f"{analysisId}.json"))

    message = "The analysis was deleted"

    return message


def get_solar_analysis() -> list:
    """
    Return all the analysisId
    """
    # Create the path if it does not exist
    if not os.path.exists(PATHS["results"]):
        os.makedirs(PATHS["results"])
    # Check csv files in "parsed_hourly" folder
    files = os.listdir(os.path.join(PATHS["results"]))
    results = []
    for file in files:
        # Check if the file is a csv file
        if file.endswith(".csv"):
            # Remove the extension
            analysisId = file[:-4]
            # Get date from the file
            time = os.path.getctime(os.path.join(PATHS["results"], file))
            metadata = _get_metadata(analysisId)
            results.append({
                "analysisId": analysisId, 
                "created_at": time,
                "name": metadata.get("name")
            })

    return results
