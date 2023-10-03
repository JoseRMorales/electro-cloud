from fastapi import APIRouter, UploadFile, File, HTTPException, Response

from typing import Annotated
from tools.utils import logger
from tools.energy_analysis_lib import core
from io import StringIO

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Hello Energy"}


@router.get("/time-slots/{analysisId}")
def get_results_time_slot_energy_by_id(analysisId: str) -> bytes:
    """
    Return the time slot energy results to the api.

    :param analysisId: The id of the analysis
    """
    logger.info("GET /api/energy/consumption-time-slot")
    try:
        time_slot_energy_results = core.get_results_time_slot_energy_by_id(analysisId)
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


@router.delete("/time-slots/{analysisId}")
def delete_results_time_slot_energy_by_id(analysisId: str):
    """
    Delete the time slots analysis.

    :param analysisId: The id of the analysis
    """
    logger.info("DELETE /api/energy/time-slots")
    message = core.delete_results_time_slot_energy_by_id(analysisId)
    return {"message": message}


@router.post("/time-slots")
async def process(consumption_file: Annotated[UploadFile, File()]):
    """
    Process the consumption file. If some exception is raised,

    :param consumption_file: consumption file
    :return: None
    """
    logger.info("Processing consumption file")

    consumption_file = await consumption_file.read()
    consumption_file = StringIO(consumption_file.decode("utf-8"))

    try:
        analysisId = core.process_consumption_file(consumption_file)
    except Exception as e:
        logger.error(e)
        # Return 500 error
        raise HTTPException(status_code=500, detail=str(e))

    logger.info("Request processed")
    return {"analysisId": analysisId}


@router.get("/time-slots")
def get_results_time_slots_energy() -> dict:
    """
    Return a list of all the time slot energy results to the api.

    :param analysisId: The id of the analysis
    """
    logger.info("GET /api/energy/time-slots")
    try:
        results_list = core.get_results_time_slot_energy()
    # TODO: Better exception handling
    except Exception as e:
        logger.error(e)
        logger.error("The time slot energy results do not exist")
        return Response(status_code=404)

    print(results_list)
    response = {"results": results_list}
    return response
