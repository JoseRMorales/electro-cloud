import zipfile
from io import BytesIO, StringIO
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from tools.energy_analysis_lib import core
from tools.utils import logger

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Hello Solar"}


@router.post("/process-file")
async def process(
    consumption_file: Annotated[UploadFile, File()],
    location: Annotated[str, Form()],
    peakpower: Annotated[float, Form()],
    mountingplace: Annotated[str, Form()],
    loss: Annotated[float, Form()],
    angle: Annotated[float, Form()],
    aspect: Annotated[float, Form()],
):
    """
    Process the consumption file and the form data. If some exception is raised,
    return the error message

    :param consumption_file: consumption file
    :param location: location of the installation
    :param peakpower: peak power of the installation
    :param mountingplace: mounting place of the installation
    :param loss: loss of the installation
    :param angle: angle of the installation
    :param aspect: azimuth of the installation
    :return: None
    """
    logger.info("Processing request")

    consumption_file = await consumption_file.read()
    consumption_file = StringIO(consumption_file.decode("utf-8"))

    try:
        analysisId = core.solar_calculation(
            consumption_file, location, peakpower, mountingplace, loss, angle, aspect
        )
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    logger.info("Request processed")
    return {"analysisId": analysisId}


@router.get("/api/monthly_production/{analysisId}")
def monthly_production(analysisId: str):
    """
    Get the monthly production of the analysisId

    :param analysisId: id of the analysis
    :return: monthly production in csv format
    """
    logger.info("Processing request")

    try:
        production = core.get_monthly_production(analysisId)
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    headers = {"Content-Disposition": 'attachment; filename="monthly_production.csv"'}

    logger.info("Request processed")
    return Response(content=production, media_type="text/csv", headers=headers)


@router.get("/api/monthly_consumption/{analysisId}")
def monthly_consumption(analysisId: str):
    """
    Get the monthly consumption of the analysisId

    :param analysisId: id of the analysis
    :return: monthly consumption in csv format
    """
    logger.info("Processing request")

    try:
        consumption = core.get_monthly_consumption(analysisId)
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    headers = {"Content-Disposition": 'attachment; filename="monthly_consumption.csv"'}

    logger.info("Request processed")
    return Response(content=consumption, media_type="text/csv", headers=headers)


@router.get("/api/monthly_consumption_production_plot/{analysisId}")
def monthly_consumption_production_plot(analysisId: str):
    """
    Get the monthly consumption and production plot of the analysisId

    :param analysisId: id of the analysis
    :return: monthly consumption and production plot in png format
    """
    logger.info("Processing request")

    try:
        plot = core.get_monthly_consumption_production_plot(analysisId)
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    headers = {
        "Content-Disposition": 'attachment; \
        filename="monthly_consumption_production_plot.png"'
    }

    logger.info("Request processed")
    return Response(content=plot, media_type="image/png", headers=headers)


@router.get("/api/results_monthly_plots/{analysisId}")
def results_monthly_plots(analysisId: str):
    """
    Get the monthly plots of the analysisId

    :param analysisId: id of the analysis
    :return: monthly plots in zip format
    """

    try:
        plots = core.get_results_monthly_plots(analysisId)
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    # Create a zip file in memory
    zip_bytes = BytesIO()
    with zipfile.ZipFile(zip_bytes, mode="w") as zip_file:
        # Add each image to the zip file
        for i, plot in enumerate(plots):
            zip_file.writestr(f"image{i}.png", plot.read())

    zip_bytes.seek(0)

    headers = {
        "Content-Disposition": 'attachment; filename="results_monthly_plots.zip"'
    }

    logger.info("Request processed")
    return Response(
        content=zip_bytes.getvalue(), media_type="application/zip", headers=headers
    )


@router.get("/api/self_percent_ratios/{analysisId}")
def self_percent_ratios(analysisId: str):
    """
    Get the self percent ratios of the analysisId

    :param analysisId: id of the analysis
    :return: self percent ratios in json format
    """
    logger.info("Processing request")

    try:
        ratios = core.get_self_percent_ratios(analysisId)
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    logger.info("Request processed")
    return ratios


@router.get("/api/results_time_slot_solar/{analysisId}")
def results_time_slot_solar(analysisId: str):
    """
    Get the time slot solar of the analysisId

    :param analysisId: id of the analysis
    :return: time slot solar in csv format
    """
    logger.info("Processing request")

    try:
        solar = core.get_results_time_slot_solar(analysisId)
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    headers = {
        "Content-Disposition": 'attachment; filename="results_time_slot_solar.csv"'
    }

    logger.info("Request processed")
    return Response(content=solar, media_type="text/csv", headers=headers)


@router.get("/energy-time-slot/{analysisId}")
def get_results_time_slot_energy(analysisId: str) -> bytes:
    """
    Return the time slot energy results to the api.

    :param analysisId: The id of the analysis
    """
    logger.info("GET /api/energy/consumption-time-slot")
    try:
        time_slot_energy_results = core.get_results_time_slot_energy(analysisId)
    # TODO: Better exception handling
    except Exception as e:
        logger.error(e)
        logger.error("The time slot energy results do not exist")
        raise FileNotFoundError("The time slot energy results do not exist")

    headers = {
        "Content-Disposition": 'attachment; filename="results_time_slot_energy.csv"'
    }

    logger.info("Request processed")
    return Response(
        content=time_slot_energy_results, headers=headers, media_type="text/csv"
    )
