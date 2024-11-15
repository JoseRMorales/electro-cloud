import datetime
import os

import pandas as pd
from tools.energy_analysis_lib import utils as lib_utils
from tools.utils import logger

from .constants import TIME_SLOTS


def parse_consumption_file(csv_file: bytes, analysisId: str) -> None:
    """
    Converts a csv file with consumption data to a csv file with 3 columns:
    'Month','Day', 'Hour', 'Energy'

    :param csv_file: csv file with consumption data
    :param analysisId: id of the user
    :return: None
    """
    logger.info("Importing file")
    # Import the csv file as a pandas dataframe
    df = pd.read_csv(
        csv_file,
        sep=";",
        decimal=",",
        thousands=".",
        encoding="UTF-8",
        parse_dates=[1],
        dayfirst=True,
    )
    logger.info("File imported")

    # Remove first and last columns
    df = df.iloc[:, 1:-1]
    # Convert date column with name 'Fecha' to 3 columns 'Month', 'Day', 'Hour'
    df["Month"] = df["Fecha"].dt.month
    df["Day"] = df["Fecha"].dt.day
    df["Hour"] = df["Hora"]

    df = df.drop(columns=["Hora"])
    df = df.rename(columns={"Fecha": "Datetime"})
    # One column can be named "Consumo" or "Consumo_kWh" depending on the file. Rename
    # it to "Energy"
    df = df.rename(columns={"Consumo": "Energy", "Consumo_kWh": "Energy"})

    # At the moment only same year data is supported
    # Throw error if there are multiple rows with same month, day and hour
    # TODO: Support for 12 months of different years and better error handling in case
    # of infringement of this rule
    if df.duplicated(subset=["Month", "Day", "Hour"]).any():
        raise ValueError(
            "There are multiple rows with same month, \
            day and hour"
        )
    else:
        logger.info("No duplicated rows")
    # Create a dataframe with monthly data
    df_monthly = df.drop(columns=["Datetime"]).groupby(["Month"]).sum()
    df_monthly = df_monthly.reset_index()

    # Only keep Month and Energy columns
    df_monthly = df_monthly.iloc[:, [0, 1]]

    # Remove hour 25 corresponding to the change to winter time
    df = df[df["Hour"] != 25]

    # Save the dataframe as a csv file
    hourly_csv = lib_utils.save_csv_file("parsed_hourly", analysisId, df)
    logger.info(f"Written file {hourly_csv}")

    # Save the monthly dataframe as a csv file
    monthly_csv = lib_utils.save_csv_file("parsed_monthly", analysisId, df_monthly)
    logger.info(f"Written file {monthly_csv}")


def parse_consumption_file_with_generation(csv_file: bytes, analysisId: str) -> None:
    """
    Converts a csv file with consumption data to a csv file with 5 columns:
    'Month','Day', 'Hour', 'Consumption', 'Generation'

    :param csv_file: csv file with consumption data
    :param analysisId: id of the user
    :return: None
    """
    logger.info("Importing file with generation")
    # Import the csv file as a pandas dataframe
    df = pd.read_csv(
        csv_file,
        sep=";",
        decimal=",",
        thousands=".",
        encoding="UTF-8",
        parse_dates=[1],
        dayfirst=True,
    )
    logger.info("File imported")

    # Remove first, third, fourth and last columns
    df = df.iloc[:, [1, 4, 5]]

    # Convert date column with format 'yyyy/mm/dd hh:mm' to 3 columns
    # 'Month', 'Day', 'Hour'
    df["Datetime"] = pd.to_datetime(df["FECHA-HORA"], format="%Y/%m/%d %H:%M")
    # TODO: Workaround because of how the other file date is given
    df["Month"] = df["Datetime"].dt.month
    df["Day"] = df["Datetime"].dt.day
    df["Hour"] = df["Datetime"].dt.hour

    # Remove hour from datetime column
    df["Datetime"] = df["Datetime"].dt.date
    # Add 1 hour to the hour column
    df["Hour"] = df["Hour"] + 1
    df.drop(columns=["FECHA-HORA"], inplace=True)
    df = df.rename(columns={"CONSUMO Wh": "Consumption", "GENERACION Wh": "Generation"})
    # One column can be named "Consumo" or "Consumo_kWh" depending on the file. Rename
    # it to "Energy"
    df = df.rename(columns={"Consumo": "Energy", "Consumo_kWh": "Energy"})
    # At the moment only same year data is supported
    # Throw error if there are multiple rows with same month, day and hour
    # TODO: Support for 12 months of different years and better error handling in case
    # of infringement of this rule
    df = df[~df.duplicated(subset=["Month", "Day", "Hour"], keep="first")]
    df["Generation"] = df["Generation"] / 1000
    df["Consumption"] = df["Consumption"] / 1000

    # Create a dataframe with monthly data
    df_monthly = df.drop(columns=["Datetime"]).groupby(["Month"]).sum()
    df_monthly = df_monthly.reset_index()

    # Only keep Month and Energy columns
    df_monthly = df_monthly.iloc[:, [0, 1]]

    # Remove hour 25 corresponding to the change to winter time
    df = df[df["Hour"] != 25]

    # Save the dataframe as a csv file
    saved_path = lib_utils.save_csv_file("parsed_hourly", analysisId, df)
    logger.info(f"Written file {saved_path}")

    # Save the monthly dataframe as a csv file
    saved_path = lib_utils.save_csv_file("parsed_monthly", analysisId, df_monthly)
    logger.info(f"Written file {saved_path}")


def process_results_time_slot_energy(analysisId: str) -> bytes:
    """
    Calculates the results of the time slot analysis

    :param analysisId: id of the user
    :return: CSV file with the results
    """
    logger.info("Calculating time slot energy results")
    output_path = lib_utils.output_path
    hourly_file = None
    try:
        hourly_file = open(
            os.path.join(output_path, "parsed_hourly", f"{analysisId}.csv"), "rb"
        )

    except FileNotFoundError:
        raise FileNotFoundError("Parsed hourly file not found")

    df = pd.read_csv(
        hourly_file,
        sep=";",
        decimal=",",
        thousands=".",
        encoding="UTF-8",
    )

    # Create datetime column
    # TODO: Datetime 2022???
    df["Datetime"] = df.apply(
        lambda x: datetime.datetime(
            2022, int(x["Month"]), int(x["Day"]), int(x["Hour"] - 1)
        ),
        axis=1,
    )

    # Create a new column with each time slot
    for time_slot_name, time_slot in TIME_SLOTS.items():
        for time_slot_type, time_slot_hours in time_slot.items():
            df[time_slot_name + "_" + time_slot_type] = df.apply(
                lambda x: x["Energy"]
                if lib_utils.is_within_time_slot(
                    x["Hour"],
                    time_slot_hours,
                    x["Datetime"],
                    time_slot_name,
                    time_slot_type,
                )
                else 0,
                axis=1,
            )

    # Create a new dataframe with the sum by month
    df = (
        df.groupby(["Month"])
        .agg(
            {
                "nocturna_Valle": "sum",
                "nocturna_Llana": "sum",
                "nocturna_Punta": "sum",
                "14h_Promocionadas": "sum",
                "14h_No promocionadas": "sum",
                "6h_Promocionadas": "sum",
                "6h_No promocionadas": "sum",
                "16h_Promocionadas": "sum",
                "16h_No promocionadas": "sum",
            }
        )
        .reset_index()
    )

    # Transpose the dataframe
    df = df.transpose()

    # Order rows. In this order nocturna_punta, nocturna_llana, nocturna_valle,
    # surpluses, 14h_promocionadas, 14h_no_promocionadas, 6h_promocionadas,
    # 6h_no_promocionadas, 16h_promocionadas, 16h_no_promocionadas
    df = df.reindex(
        [
            "nocturna_Punta",
            "nocturna_Llana",
            "nocturna_Valle",
            "14h_Promocionadas",
            "14h_No promocionadas",
            "6h_Promocionadas",
            "6h_No promocionadas",
            "16h_Promocionadas",
            "16h_No promocionadas",
        ]
    )

    # Save the results
    results_path = lib_utils.save_csv_file("time_slots", analysisId, df)
    logger.info(f"Written file {results_path}")

    results_csv = lib_utils.save_csv_to_variable(df)

    return results_csv


def process_results_time_slot_energy_with_generation(analysisId: str) -> bytes:
    """
    Calculates the results of the time slot analysis

    :param analysisId: id of the user
    :return: CSV file with the results
    """
    logger.info("Calculating time slot energy results")
    output_path = lib_utils.output_path
    hourly_file = None
    try:
        hourly_file = open(
            os.path.join(output_path, "parsed_hourly", f"{analysisId}.csv"), "rb"
        )

    except FileNotFoundError:
        raise FileNotFoundError("Parsed hourly file not found")

    df = pd.read_csv(
        hourly_file,
        sep=";",
        decimal=",",
        thousands=".",
        encoding="UTF-8",
    )

    # Create datetime column
    # TODO: Datetime 2022???
    df["Datetime"] = df.apply(
        lambda x: datetime.datetime(
            2022, int(x["Month"]), int(x["Day"]), int(x["Hour"] - 1)
        ),
        axis=1,
    )

    # Create a new column with each time slot
    for time_slot_name, time_slot in TIME_SLOTS.items():
        for time_slot_type, time_slot_hours in time_slot.items():
            df[time_slot_name + "_" + time_slot_type] = df.apply(
                lambda x: x["Consumption"]
                if lib_utils.is_within_time_slot(
                    x["Hour"],
                    time_slot_hours,
                    x["Datetime"],
                    time_slot_name,
                    time_slot_type,
                )
                else 0,
                axis=1,
            )

    # Create a new dataframe with the sum by month
    df = (
        df.groupby(["Month"])
        .agg(
            {
                "nocturna_Valle": "sum",
                "nocturna_Llana": "sum",
                "nocturna_Punta": "sum",
                "14h_Promocionadas": "sum",
                "14h_No promocionadas": "sum",
                "6h_Promocionadas": "sum",
                "6h_No promocionadas": "sum",
                "16h_Promocionadas": "sum",
                "16h_No promocionadas": "sum",
                "Generation": "sum",
            }
        )
        .reset_index()
    )

    # Transpose the dataframe
    df = df.transpose()

    df = df.reindex(
        [
            "nocturna_Punta",
            "nocturna_Llana",
            "nocturna_Valle",
            "14h_Promocionadas",
            "14h_No promocionadas",
            "6h_Promocionadas",
            "6h_No promocionadas",
            "16h_Promocionadas",
            "16h_No promocionadas",
            "Generation",
        ]
    )

    # Save the results
    results_path = lib_utils.save_csv_file("time_slots", analysisId, df)
    logger.info(f"Written file {results_path}")

    results_csv = lib_utils.save_csv_to_variable(df)

    return results_csv
