import uuid
import os
import re
import tools.pvgis_api_wrapper as api
from tools.utils import logger
from tools.energy_analysis_lib.energy import parse_consumption_file
import tools.energy_analysis_lib.solar as solar
import tools.energy_analysis_lib.energy as energy
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
            PATHS["production"] + "parsed_monthly_" + analysisId + ".csv", "rb"
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
            PATHS["consumption"] + "parsed_monthly_" + analysisId + ".csv", "rb"
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
        consumption_production_plot = open(PATHS["plots"] + analysisId + ".png", "rb")
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
                    PATHS["plots"]
                    + "results_monthly_"
                    + analysisId
                    + "_"
                    + str(month)
                    + ".png",
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
            PATHS["outputs"] + "results_time_slot_" + analysisId + ".csv", "rb"
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
        parse_consumption_file(consumption_file, analysisId)
    except Exception as e:
        logger.error(e)
        raise e
    logger.info("Consumption file processed")
    return analysisId


def get_results_time_slot_energy_by_id(analysisId: str) -> bytes:
    """
    Return the time slot energy results to the api.

    :param analysisId: The id of the analysis
    """
    # Calculate
    energy.process_results_time_slot_energy(analysisId)

    try:
        results_time_slot_energy = open(
            PATHS["output"] + "results_time_slot_consumption_" + analysisId + ".csv",
            "rb",
        )
    except Exception as e:
        logger.error(e)
        logger.error("The time slot energy results do not exist")
        raise FileNotFoundError("The time slot energy results do not exist")

    return results_time_slot_energy.read()


def get_results_time_slot_energy() -> list:
    """
    Return all the analysisId
    """
    # In the output folder read all the files and extract the analysisId
    try:
        files = os.listdir(PATHS["output"])
        uuids = []

        for file in files:
            if file.startswith("results_time_slot_consumption_"):
                # Extract the UUID from the file name using a regular expression
                uuid = re.search(
                    r"(?<=results_time_slot_consumption_)[\w-]+", file
                ).group(0)
                uuids.append(uuid)

        return uuids
    except Exception as e:
        logger.error(e)
        logger.error("Error getting the time slot energy results")
        raise e
