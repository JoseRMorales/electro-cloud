import os
import uuid

import tools.energy_analysis_lib.energy as energy
import tools.energy_analysis_lib.solar as solar
import tools.pvgis_api_wrapper as api
from tools.energy_analysis_lib.energy import (
    parse_consumption_file,
    parse_consumption_file_with_generation,
)
from tools.utils import logger

from .constants import PATHS


def solar_calculation(
    consumption_file: bytes,
    location: str,
    peakpower: float,
    mountingplace: str,
    loss: float,
    angle: float,
    aspect: float,
) -> str:
    """
    Generate all the data necessary for the solar analysis.

    :param consumption_file: The consumption file
    :param location: The location of the solar panels
    :param peakpower: The peak power of the solar panels
    :param mountingplace: The mounting place of the solar panels
    :param loss: The loss of the solar panels
    :param angle: The angle of the solar panels
    :param aspect: The aspect of the solar panels

    :return: The id of the analysis
    """

    # Create a unique id for the analysis repeatable by the parameters
    analysisId = str(
        uuid.uuid3(
            uuid.NAMESPACE_DNS,
            location
            + str(peakpower)
            + mountingplace
            + str(loss)
            + str(angle)
            + str(aspect),
        )
    )

    # Parse the consumption file
    parse_consumption_file(consumption_file, analysisId)

    # Get the production data from api
    api.get_monthly_production(
        location, peakpower, mountingplace, loss, angle, aspect, analysisId
    )
    api.get_hourly_production(
        location, peakpower, mountingplace, loss, angle, aspect, analysisId
    )

    # Parse the production file
    solar.parse_hourly_production_file(analysisId)
    solar.parse_monthly_production_file(analysisId)

    # Generate consumption vs production plot
    solar.consumption_production_chart(
        location, peakpower, mountingplace, loss, angle, aspect, analysisId
    )

    # Calculate the self consumption
    solar.plot_self_consumption_monthly(analysisId)

    # Get the time slot consumption
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


def process_consumption_file(consumption_file: bytes) -> str:
    """
    Process the consumption file. If some exception is raised,

    :param consumption_file: consumption file
    :return: None
    """
    logger.info("Processing consumption file")

    analysisId = str(uuid.uuid4())

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
            results.append({"analysisId": analysisId, "created_at": time})

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
            results.append({"analysisId": analysisId, "created_at": time})

    return results
