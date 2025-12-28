import json
import zipfile
from io import BytesIO, StringIO
from typing import Annotated, Optional

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from tools.energy_analysis_lib import core
from tools.utils import logger

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Hello Solar"}


@router.post("/process-file")
async def process(
    location: Annotated[str, Form()],
    roofs: Annotated[str, Form()],
    consumption_file: Annotated[Optional[UploadFile], File()] = None,
):
    """
    Process the consumption file and the form data. If some exception is raised,
    return the error message

    :param location: location of the installation
    :param roofs: JSON string containing list of roof configurations
    :param consumption_file: optional consumption file
    :return: analysisId
    """
    logger.info("Processing request")

    consumption_io = None
    if consumption_file:
        consumption_content = await consumption_file.read()
        if consumption_content:
            consumption_io = StringIO(consumption_content.decode("utf-8"))

    try:
        roofs_list = json.loads(roofs)
        analysisId = await core.solar_calculation(
            consumption_io, location, roofs_list
        )
    except Exception as e:
        logger.exception(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    logger.info("Request processed")
    return {"analysisId": analysisId}


@router.get("/monthly_production/{analysisId}")
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


@router.get("/monthly_consumption/{analysisId}")
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


@router.get("/monthly_consumption_production_plot/{analysisId}")
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


@router.get("/results_monthly_plots/{analysisId}")
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
            plot.close()

    zip_bytes.seek(0)

    headers = {
        "Content-Disposition": 'attachment; filename="results_monthly_plots.zip"'
    }

    logger.info("Request processed")
    return Response(
        content=zip_bytes.getvalue(), media_type="application/zip", headers=headers
    )


@router.get("/self_percent_ratios/{analysisId}")
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


@router.get("/results_time_slot_solar/{analysisId}")
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


@router.get("/analysis")
def get_analysis():
    """
    Get all the analysis

    :return: list of analysis
    """
    logger.info("Processing request")

    try:
        analysis = core.get_solar_analysis()
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    logger.info("Request processed")
    response = {"results": analysis}
    return response
