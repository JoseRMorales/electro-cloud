from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Response

# from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import Tools.SolarAnalysisLib as sa
from typing import Annotated
import logging
from io import StringIO, BytesIO
import zipfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/api/")
def api():
    return {"message": "Hello Api!"}


@app.post("/api/process")
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
    logger = logging.getLogger(__name__)
    logger.info("Processing request")

    consumption_file = await consumption_file.read()
    consumption_file = StringIO(consumption_file.decode("utf-8"))

    try:
        analysisId = sa.solar_calculation(
            consumption_file, location, peakpower, mountingplace, loss, angle, aspect
        )
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    logger.info("Request processed")
    return {"analysisId": analysisId}


@app.get("/api/monthly_production/{analysisId}")
def monthly_production(analysisId: str):
    """
    Get the monthly production of the analysisId

    :param analysisId: id of the analysis
    :return: monthly production in csv format
    """
    logger = logging.getLogger(__name__)
    logger.info("Processing request")

    try:
        production = sa.get_monthly_production(analysisId)
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    headers = {"Content-Disposition": 'attachment; filename="monthly_production.csv"'}

    logger.info("Request processed")
    return Response(content=production, media_type="text/csv", headers=headers)


@app.get("/api/monthly_consumption/{analysisId}")
def monthly_consumption(analysisId: str):
    """
    Get the monthly consumption of the analysisId

    :param analysisId: id of the analysis
    :return: monthly consumption in csv format
    """
    logger = logging.getLogger(__name__)
    logger.info("Processing request")

    try:
        consumption = sa.get_monthly_consumption(analysisId)
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    headers = {"Content-Disposition": 'attachment; filename="monthly_consumption.csv"'}

    logger.info("Request processed")
    return Response(content=consumption, media_type="text/csv", headers=headers)


@app.get("/api/monthly_consumption_production_plot/{analysisId}")
def monthly_consumption_production_plot(analysisId: str):
    """
    Get the monthly consumption and production plot of the analysisId

    :param analysisId: id of the analysis
    :return: monthly consumption and production plot in png format
    """
    logger = logging.getLogger(__name__)
    logger.info("Processing request")

    try:
        plot = sa.get_monthly_consumption_production_plot(analysisId)
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


@app.get("/api/results_monthly_plots/{analysisId}")
def results_monthly_plots(analysisId: str):
    """
    Get the monthly plots of the analysisId

    :param analysisId: id of the analysis
    :return: monthly plots in zip format
    """
    logger = logging.getLogger(__name__)

    try:
        plots = sa.get_results_monthly_plots(analysisId)
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


@app.get("/api/self_percent_ratios/{analysisId}")
def self_percent_ratios(analysisId: str):
    """
    Get the self percent ratios of the analysisId

    :param analysisId: id of the analysis
    :return: self percent ratios in json format
    """
    logger = logging.getLogger(__name__)
    logger.info("Processing request")

    try:
        ratios = sa.get_self_percent_ratios(analysisId)
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    logger.info("Request processed")
    return ratios


@app.get("/api/results_time_slot_consumption/{analysisId}")
def results_time_slot_consumption(analysisId: str):
    """
    Get the time slot consumption of the analysisId

    :param analysisId: id of the analysis
    :return: time slot consumption in csv format
    """
    logger = logging.getLogger(__name__)
    logger.info("Processing request")

    try:
        consumption = sa.get_results_time_slot_consumption(analysisId)
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    headers = {
        "Content-Disposition": 'attachment; \
        filename="results_time_slot_consumption.csv"'
    }

    logger.info("Request processed")
    return Response(content=consumption, media_type="text/csv", headers=headers)


@app.get("/api/results_time_slot_solar/{analysisId}")
def results_time_slot_solar(analysisId: str):
    """
    Get the time slot solar of the analysisId

    :param analysisId: id of the analysis
    :return: time slot solar in csv format
    """
    logger = logging.getLogger(__name__)
    logger.info("Processing request")

    try:
        solar = sa.get_results_time_slot_solar(analysisId)
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    headers = {
        "Content-Disposition": 'attachment; filename="results_time_slot_solar.csv"'
    }

    logger.info("Request processed")
    return Response(content=solar, media_type="text/csv", headers=headers)
