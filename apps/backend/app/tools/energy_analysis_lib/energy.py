import pandas as pd
import datetime
from .constants import TIME_SLOTS, SUPABASE_STORAGE, SUPABASE_TABLES
from .utils import is_within_time_slot, save_csv_to_variable, get_supabase_client
from tools.utils import logger
from supabase import StorageException
import io


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
    df = df.rename(columns={"Consumo": "Energy"})
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
    print(df.head())
    # Create a dataframe with monthly data
    df_monthly = df.drop(columns=["Datetime"]).groupby(["Month"]).sum()
    df_monthly = df_monthly.reset_index()

    # Only keep Month and Energy columns
    df_monthly = df_monthly.iloc[:, [0, 1]]

    # Remove hour 25 corresponding to the change to winter time
    df = df[df["Hour"] != 25]

    supabase = get_supabase_client()

    # Check if buckets exist
    try:
        supabase.storage.get_bucket(
            SUPABASE_STORAGE["buckets"]["energy_analysis"]["name"]
        )
    except StorageException:
        # Create bucket
        supabase.storage.create_bucket(
            SUPABASE_STORAGE["buckets"]["energy_analysis"]["name"]
        )

    # Save the dataframe as a csv file
    monthly_csv = save_csv_to_variable(df_monthly)
    logger.info(f"Written file parsed_monthly_{analysisId}.csv")

    # Upload the file to supabase
    path = (
        SUPABASE_STORAGE["buckets"]["energy_analysis"]["consumption"]["monthly_path"]
        + f"{analysisId}.csv"
    )
    supabase.storage.from_(
        SUPABASE_STORAGE["buckets"]["energy_analysis"]["name"]
    ).upload(
        file=monthly_csv,
        path=path,
        file_options={"contentType": "text/csv"},
    )
    logger.info("File uploaded")

    # Save the dataframe as a csv file
    hourly_csv = save_csv_to_variable(df)
    logger.info(f"Written file parsed_hourly_{analysisId}.csv")

    # Upload the file to supabase
    path = (
        SUPABASE_STORAGE["buckets"]["energy_analysis"]["consumption"]["hourly_path"]
        + f"{analysisId}.csv"
    )
    supabase.storage.from_(
        SUPABASE_STORAGE["buckets"]["energy_analysis"]["name"]
    ).upload(
        file=hourly_csv,
        path=path,
        file_options={"contentType": "text/csv"},
    )
    logger.info("File uploaded")

    # Upsert table
    supabase.table(SUPABASE_TABLES["energy_analysis"]).upsert(
        {"analysisId": analysisId, "analysis_time_slots": True}
    ).execute()
    logger.info("Table upserted")


def process_results_time_slot_energy(analysisId: str) -> bytes:
    """
    Calculates the results of the time slot analysis

    :param analysisId: id of the user
    :return: CSV file with the results
    """
    logger.info("Calculating time slot energy results")

    supabase = get_supabase_client()
    # Load the consumption data
    try:
        # Get file from supabase
        res = supabase.storage.from_(
            SUPABASE_STORAGE["buckets"]["energy_analysis"]["name"]
        ).download(
            SUPABASE_STORAGE["buckets"]["energy_analysis"]["consumption"]["hourly_path"]
            + f"{analysisId}.csv"
        )
        res = io.BytesIO(res)
        df = pd.read_csv(
            res,
            sep=";",
            decimal=",",
            thousands=".",
            encoding="UTF-8",
        )
    except StorageException:
        raise FileNotFoundError("Consumption file not found")
    logger.info("Consumption data loaded")
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
                if is_within_time_slot(
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
    results_csv = save_csv_to_variable(df)

    # Upload the file to supabase
    path = (
        SUPABASE_STORAGE["buckets"]["energy_analysis"]["output"]["time_slots"]
        + f"{analysisId}.csv"
    )
    supabase.storage.from_(
        SUPABASE_STORAGE["buckets"]["energy_analysis"]["name"]
    ).upload(
        file=results_csv,
        path=path,
        file_options={"contentType": "text/csv"},
    )

    return results_csv
