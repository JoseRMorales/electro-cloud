import datetime
import logging
import os

import numpy as np
import pandas as pd
import tools.pvgis_api_wrapper as api
from matplotlib import pyplot as plt
from tools.energy_analysis_lib import utils as lib_utils
from tools.utils import logger

from .constants import PATHS, TIME_SLOTS
from .energy import process_results_time_slot_energy
from .utils import is_within_time_slot

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def parse_monthly_production_file(analysisId: str) -> None:
    """
    Converts a csv file with monthly production data to a csv file with 2 columns:
    'Month', 'Energy'

    :param analysisId: id of the user
    :return: None
    """

    # Import the csv file as a pandas dataframe
    df = pd.read_csv(
        os.path.join(PATHS["production_monthly"], f"{analysisId}.csv"),
        sep="\t",
        decimal=".",
        thousands=",",
        encoding="UTF-8",
        skiprows=9,
        nrows=12,
    )
    logger.info("File imported")

    # Only keep first and third column
    df = df.iloc[:, [0, 4]]

    # Rename 'E_m' to 'Energy'
    df = df.rename(columns={"E_m": "Energy"})

    # Save the dataframe as a csv file
    saved_path = lib_utils.save_csv_file(
        PATHS["production_parsed_monthly"], analysisId, df
    )
    logger.info(f"Written file {saved_path}")


def parse_hourly_production_file(analysisId: str) -> None:
    """
    Converts a csv file with hourly production data to a csv file with 3 columns:
    'Month', 'Day', 'Hour', 'Energy'

    :param analysisId: id of the user
    :return: None
    """

    # Count file lines
    with open(os.path.join(PATHS["production_hourly"], f"{analysisId}.csv"), "r") as f:
        n_lines = sum(1 for line in f)

    # Import the csv file as a pandas dataframe
    df = pd.read_csv(
        os.path.join(PATHS["production_hourly"], f"{analysisId}.csv"),
        sep=",",
        decimal=".",
        thousands=",",
        encoding="UTF-8",
        skiprows=10,
        nrows=n_lines - 22,
    )
    logger.info("File imported")

    # Convert first column to datetime
    df["time"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M")
    # Only keep frst 2 columns
    df = df.iloc[:, [0, 1]]

    # Convert date column with name 'time' to 3 columns 'Month', 'Day', 'Hour'
    df["Month"] = df["time"].dt.month
    df["Day"] = df["time"].dt.day
    df["Hour"] = df["time"].dt.hour

    df = df.drop(columns=["time"])

    # Divide by 1000 to convert from Wh to kWh, round to 2 decimals
    df["P"] = df["P"].div(1000).round(3)

    # Rename 'P' to 'Energy'
    df = df.rename(columns={"P": "Energy"})

    # Rename 'E_m' to 'Energy'
    df = df.rename(columns={"E_m": "Energy"})

    # Delete 29th of February
    df = df[~((df["Month"] == 2) & (df["Day"] == 29))]

    # Save the dataframe as a csv file
    saved_path = lib_utils.save_csv_file(
        PATHS["production_parsed_hourly"], analysisId, df
    )
    logger.info(f"Written file {saved_path}")



def load_and_parse_hourly(analysisId: str) -> pd.DataFrame:
    """
    Loads and parses the hourly production file for a given analysisId
    """
    parse_hourly_production_file(analysisId)
    df = pd.read_csv(
        os.path.join(PATHS["production_parsed_hourly"], f"{analysisId}.csv"),
        sep=";",
        decimal=",",
        thousands=".",
        encoding="UTF-8",
    )
    return df


def load_and_parse_monthly(analysisId: str) -> pd.DataFrame:
    """
    Loads and parses the monthly production file for a given analysisId
    """
    parse_monthly_production_file(analysisId)
    df = pd.read_csv(
        os.path.join(PATHS["production_parsed_monthly"], f"{analysisId}.csv"),
        sep=";",
        decimal=",",
        thousands=".",
        encoding="UTF-8",
    )
    return df


def aggregate_hourly(dfs: list[pd.DataFrame], targetId: str) -> pd.DataFrame:
    """
    Aggregates multiple hourly production DataFrames by summing their Energy
    """
    if not dfs:
        return None

    df_agg = dfs[0].copy()
    for df in dfs[1:]:
        df_agg["Energy"] += df["Energy"]

    # Round to 3 decimals after aggregation
    df_agg["Energy"] = df_agg["Energy"].round(3)

    lib_utils.save_csv_file(PATHS["production_parsed_hourly"], targetId, df_agg)
    return df_agg


def aggregate_monthly(dfs: list[pd.DataFrame], targetId: str) -> pd.DataFrame:
    """
    Aggregates multiple monthly production DataFrames by summing their Energy
    """
    if not dfs:
        return None

    df_agg = dfs[0].copy()
    for df in dfs[1:]:
        df_agg["Energy"] += df["Energy"]

    # Round to 2 decimals
    df_agg["Energy"] = df_agg["Energy"].round(2)

    lib_utils.save_csv_file(PATHS["production_parsed_monthly"], targetId, df_agg)
    return df_agg


def consumption_production_chart(analysisId: str) -> None:
    """
    Generates a chart with the consumption and production data for a location
    If consumption is not found, only production is plotted.

    :param analysisId: id of the user
    :return: None
    """

    # Load the consumption data
    df_consumption = None
    try:
        df_consumption = pd.read_csv(
            os.path.join(PATHS["consumption_parsed_monthly"], f"{analysisId}.csv"),
            sep=";",
            decimal=",",
            thousands=".",
            encoding="UTF-8",
        )
        logger.info("Consumption data loaded")
    except FileNotFoundError:
        logger.info("Consumption file not found, skipping consumption plot")

    # Load the production data
    try:
        df_production = pd.read_csv(
            os.path.join(PATHS["production_parsed_monthly"], f"{analysisId}.csv"),
            sep=";",
            decimal=",",
            thousands=".",
            encoding="UTF-8",
        )
    except FileNotFoundError:
        logger.error("Production file not found")
        raise FileNotFoundError("Production file not found")

    logger.info("Production data loaded")

    if df_consumption is not None:
        # Merge the consumption and production data
        df = pd.merge(
            df_consumption,
            df_production,
            on=["Month"],
            how="outer",
            suffixes=("_consumption", "_production"),
        )
        df = df.reset_index(drop=True)
        logger.info("Data merged")

        # Generate the bar chart
        df.plot.bar(x="Month", y=["Energy_consumption", "Energy_production"], rot=0)
        plt.legend(["Consumption", "Production"])
    else:
        # Only production
        df_production.plot.bar(x="Month", y="Energy", rot=0)
        plt.legend(["Production"])

    plt.xlabel("Month")
    plt.ylabel("Energy (kWh)")
    plt.title("Consumption and production")
    plt.gcf().set_size_inches(10, 5)

    # Create the path if it does not exist
    if not os.path.exists(PATHS["plots_consumption_production_chart"]):
        os.makedirs(PATHS["plots_consumption_production_chart"])
    plt.savefig(
        os.path.join(PATHS["plots_consumption_production_chart"], f"{analysisId}.png"),
        dpi=100,
    )

    # Clear the plot
    plt.clf()

    logger.info("Chart saved")


def get_self_consumption_ratio(analysisId: str) -> (list[float], float):
    """
    Calculates the self consumption ratio of a location
    If consumption is missing, returns zeros.

    :param analysisId: id of the user
    :return: list of self consumption ratios, average self consumption ratio
    """

    # Load the consumption data
    df_consumption = None
    try:
        df_consumption = pd.read_csv(
            os.path.join(PATHS["consumption_parsed_hourly"], f"{analysisId}.csv"),
            sep=";",
            decimal=",",
            thousands=".",
            encoding="UTF-8",
        )
        logger.info("Consumption data loaded")
    except FileNotFoundError:
        logger.info("Consumption file not found, returning zero ratios")
        return [0.0] * 12, 0.0

    # Load the production data
    try:
        df_production = pd.read_csv(
            os.path.join(PATHS["production_parsed_hourly"], f"{analysisId}.csv"),
            sep=";",
            decimal=",",
            thousands=".",
            encoding="UTF-8",
        )
    except FileNotFoundError:
        raise FileNotFoundError("Production file not found")
    logger.info("Production data loaded")

    # Merge the consumption and production data
    df = pd.merge(
        df_consumption,
        df_production,
        on=["Month", "Day", "Hour"],
        how="outer",
        suffixes=("_consumption", "_production"),
    )
    df = df.reset_index(drop=True)
    logger.info("Data merged")

    # Calculate the self consumption ratio.
    # For every hour subtract production from consumption but only if production is
    # greater than consumption else it is 0
    df["Substraction"] = np.where(
        df["Energy_production"] > df["Energy_consumption"],
        df["Energy_production"] - df["Energy_consumption"],
        0,
    )

    # Create a new dataframe with the sum of the substraction for each month, the total
    # production and the total consumption for each month
    df = (
        df.groupby(["Month"])
        .agg(
            {
                "Substraction": "sum",
                "Energy_production": "sum",
                "Energy_consumption": "sum",
            }
        )
        .reset_index()
    )

    # Calculate the self consumption ratio rounding to 2 decimals
    # Avoid division by zero
    df["Self_consumption_ratio"] = np.where(
        df["Energy_production"] > 0,
        (1 - (df["Substraction"] / df["Energy_production"])).round(2),
        0.0
    )

    # Save the dataframe as a csv file
    saved_path = lib_utils.save_csv_file(
        PATHS["results_self_consumption"], analysisId, df
    )
    logger.info(f"Written file {saved_path}")

    self_consumption_avg = df["Self_consumption_ratio"].mean()
    # Return the self consumption ratio and the average
    return df["Self_consumption_ratio"].tolist(), self_consumption_avg


def process_results_time_slot_solar(analysisId: str) -> None:
    """
    Calculates the results of the time slot analysis
    If consumption is missing, only surpluses are calculated.

    :param analysisId: id of the user
    :return: None
    """

    # Load the consumption data
    df_consumption = None
    try:
        df_consumption = pd.read_csv(
            os.path.join(PATHS["consumption_parsed_hourly"], f"{analysisId}.csv"),
            sep=";",
            decimal=",",
            thousands=".",
            encoding="UTF-8",
        )
        logger.info("Consumption data loaded")
    except FileNotFoundError:
        logger.info("Consumption file not found, only calculating surpluses")

    # Load the production data
    try:
        df_production = pd.read_csv(
            os.path.join(PATHS["production_parsed_hourly"], f"{analysisId}.csv"),
            sep=";",
            decimal=",",
            thousands=".",
            encoding="UTF-8",
        )
    except FileNotFoundError:
        raise FileNotFoundError("Production file not found")
    logger.info("Production data loaded")

    if df_consumption is not None:
        # Merge the consumption and production data
        df = pd.merge(
            df_consumption,
            df_production,
            on=["Month", "Day", "Hour"],
            how="outer",
            suffixes=("_consumption", "_production"),
        )
    else:
        df = df_production.copy()
        df = df.rename(columns={"Energy": "Energy_production"})
        df["Energy_consumption"] = 0.0

    df = df.reset_index(drop=True)
    logger.info("Data merged")

    # For every hour subtract production from consumption but only if production is
    # greater than consumption else it is 0
    df["Surpluses"] = np.where(
        df["Energy_production"] > df["Energy_consumption"],
        df["Energy_production"] - df["Energy_consumption"],
        0,
    )

    # Consumption after self consumption. Substract the production from the consumption.
    # If the production is greater than the consumption, the consumption is 0
    df["Consumption_after_self_consumption"] = np.where(
        df["Energy_production"] > df["Energy_consumption"],
        0,
        df["Energy_consumption"] - df["Energy_production"],
    )

    # Remove row with hour 24 (because of daylight saving time)
    df = df[df["Hour"] != 24]

    # Create datetime column
    df["Datetime"] = df.apply(
        lambda x: datetime.datetime(
            2024, int(x["Month"]), int(x["Day"]), int(x["Hour"])
        ),
        axis=1,
    )

    # Create a new column with each time slot
    for time_slot_name, time_slot in TIME_SLOTS.items():
        for time_slot_type, time_slot_hours in time_slot.items():
            df[time_slot_name + "_" + time_slot_type] = df.apply(
                lambda x: x["Consumption_after_self_consumption"]
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
    agg_dict = {
        "Surpluses": "sum",
        "Consumption_after_self_consumption": "sum",
    }
    for time_slot_name, time_slot in TIME_SLOTS.items():
        for time_slot_type in time_slot.keys():
            agg_dict[time_slot_name + "_" + time_slot_type] = "sum"

    df = df.groupby(["Month"]).agg(agg_dict).reset_index()

    # Transpose the dataframe
    df = df.transpose()

    # Order rows.
    order = [
        "nocturna_Punta",
        "nocturna_Llana",
        "nocturna_Valle",
        "Surpluses",
        "14h_Promocionadas",
        "14h_No promocionadas",
        "6h_Promocionadas",
        "6h_No promocionadas",
        "16h_Promocionadas",
        "16h_No promocionadas",
    ]
    # Filter order to only include existing columns in df
    order = [o for o in order if o in df.index]
    df = df.reindex(order)

    # Save the results
    saved_path = lib_utils.save_csv_file(PATHS["time_slots"], analysisId, df)
    logger.info(f"Written file {saved_path}")

    # Only call process_results_time_slot_energy if consumption was provided
    if df_consumption is not None:
        process_results_time_slot_energy(analysisId)
        logger.info("Consumption results saved")


def plot_self_consumption_monthly(analysisId: str) -> None:
    """
    Calculate the self consumption for each month and generate the charts for each
    month.
    If consumption is missing, only production is plotted.

    :param analysisId: The id of the analysis
    """

    # Load the consumption data
    df_consumption = None
    try:
        df_consumption = pd.read_csv(
            os.path.join(PATHS["consumption_parsed_hourly"], f"{analysisId}.csv"),
            sep=";",
            decimal=",",
            encoding="UTF-8",
        )
    except FileNotFoundError:
        logger.info("The consumption file does not exist, plotting only production")

    # Load the production data
    try:
        df_production = pd.read_csv(
            os.path.join(PATHS["production_parsed_hourly"], f"{analysisId}.csv"),
            sep=";",
            decimal=",",
            encoding="UTF-8",
        )
    except FileNotFoundError:
        logger.error("The production file does not exist")
        raise FileNotFoundError("The production file does not exist")

    if df_consumption is not None:
        # Merge the dataframes
        df = pd.merge(
            df_consumption,
            df_production,
            on=["Month", "Day", "Hour"],
            how="left",
            suffixes=("_consumption", "_production"),
        )
    else:
        df = df_production.copy()
        df = df.rename(columns={"Energy": "Energy_production"})
        df["Energy_consumption"] = 0.0

    # Get days of each month
    days_of_month = df.groupby(["Month"]).agg({"Day": "max"}).reset_index()

    # Sum all same hours from each month. That is the sum of every hour 1, 2, 3, etc.
    df = (
        df.groupby(["Month", "Hour"])
        .agg({"Energy_consumption": "sum", "Energy_production": "sum"})
        .reset_index()
    )

    # Get the average for each hour. That is dividing the sum of each hour by the
    # number of days of the month
    df = pd.merge(df, days_of_month, on=["Month"], how="left")
    df["Energy_consumption"] = df.apply(
        lambda x: x["Energy_consumption"] / x["Day"], axis=1
    )
    df["Energy_production"] = df.apply(
        lambda x: x["Energy_production"] / x["Day"], axis=1
    )

    # Keep only the columns we need
    df = df[["Month", "Hour", "Energy_consumption", "Energy_production"]]

    # Export the data
    saved_path = lib_utils.save_csv_file(PATHS["results"], analysisId, df)
    logger.info(f"Written file {saved_path}")

    # Plot the results for each month
    for month in range(1, 13):
        df_month = df[df["Month"] == month]
        
        if df_consumption is not None:
            df_month.plot(
                x="Hour",
                y=["Energy_consumption", "Energy_production"],
                kind="line",
                title="Month " + str(month),
                ylabel="Energy (kWh)",
                xlabel="Hour",
            )
            plt.legend(["Consumption", "Production"])
        else:
            df_month.plot(
                x="Hour",
                y="Energy_production",
                kind="line",
                title="Month " + str(month),
                ylabel="Energy (kWh)",
                xlabel="Hour",
            )
            plt.legend(["Production"])

        # Wider plot
        plt.gcf().set_size_inches(15, 8)
        # Create the path if it does not exist
        if not os.path.exists(PATHS["plots_monthly"]):
            os.makedirs(PATHS["plots_monthly"])
        plt.savefig(os.path.join(PATHS["plots_monthly"], f"{analysisId}_{month}.png"))
        plt.close()

    logger.info("Monthly plots saved")
