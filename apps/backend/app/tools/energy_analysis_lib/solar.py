import datetime
import logging

import numpy as np
import pandas as pd
import tools.pvgis_api_wrapper as api
from matplotlib import pyplot as plt
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
        PATHS["production"] + "monthly_" + analysisId + ".csv",
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
    df.to_csv(
        PATHS["production"] + "parsed_monthly_" + analysisId + ".csv",
        index=False,
        sep=";",
        decimal=",",
        encoding="UTF-8",
    )
    logger.info("File saved")


def parse_hourly_production_file(analysisId: str) -> None:
    """
    Converts a csv file with hourly production data to a csv file with 3 columns:
    'Month', 'Day', 'Hour', 'Energy'

    :param analysisId: id of the user
    :return: None
    """

    # Count file lines
    with open(PATHS["production"] + "hourly_" + analysisId + ".csv", "r") as f:
        n_lines = sum(1 for line in f)

    # Import the csv file as a pandas dataframe
    df = pd.read_csv(
        PATHS["production"] + "hourly_" + analysisId + ".csv",
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
    df.to_csv(
        PATHS["production"] + "parsed_hourly_" + analysisId + ".csv",
        index=False,
        sep=";",
        decimal=",",
        encoding="UTF-8",
    )
    logger.info("File saved")


def consumption_production_chart(
    location: str,
    peakpower: float,
    mountingplace: str,
    loss: float,
    angle: float,
    aspect: float,
    analysisId: str,
) -> None:
    """
    Generates a chart with the consumption and production data for a location

    :param location: location to get the data
    :param peakpower: peak power of the installation
    :param mountingplace: mounting place of the installation
    :param loss: loss of the installation
    :param angle: angle of the installation
    :param aspect: aspect of the installation
    :param analysisId: id of the user
    :return: None
    """

    # Load the consumption data
    try:
        df_consumption = pd.read_csv(
            PATHS["consumption"] + "parsed_monthly_" + analysisId + ".csv",
            sep=";",
            decimal=",",
            thousands=".",
            encoding="UTF-8",
        )
    except FileNotFoundError:
        raise FileNotFoundError("Consumption file not found")
    logger.info("Consumption data loaded")

    # Load the production data
    try:
        df_production = pd.read_csv(
            PATHS["production"] + "parsed_monthly_" + analysisId + ".csv",
            sep=";",
            decimal=",",
            thousands=".",
            encoding="UTF-8",
        )
    except FileNotFoundError:
        api.get_monthly_production(
            location=location,
            peakpower=peakpower,
            mountingplace=mountingplace,
            loss=loss,
            angle=angle,
            aspect=aspect,
            analysisId=analysisId,
        )
        parse_monthly_production_file(analysisId)
        df_production = pd.read_csv(
            PATHS["production"] + "parsed_monthly_" + analysisId + ".csv",
            sep=";",
            decimal=",",
            thousands=".",
            encoding="UTF-8",
        )
    logger.info("Production data loaded")

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
    plt.xlabel("Month")
    plt.ylabel("Energy (kWh)")
    plt.title("Consumption and production")
    plt.legend(["Consumption", "Production"])
    plt.gcf().set_size_inches(10, 5)
    plt.savefig(PATHS["plots"] + analysisId + ".png", dpi=100)

    # Clear the plot
    plt.clf()

    logger.info("Chart saved")


def get_self_consumption_ratio(analysisId: str) -> (list[float], float):
    """
    Calculates the self consumption ratio of a location

    :param analysisId: id of the user
    :return: list of self consumption ratios, average self consumption ratio
    """

    # Load the consumption data
    try:
        df_consumption = pd.read_csv(
            PATHS["consumption"] + "parsed_hourly_" + analysisId + ".csv",
            sep=";",
            decimal=",",
            thousands=".",
            encoding="UTF-8",
        )
    except FileNotFoundError:
        raise FileNotFoundError("Consumption file not found")
    logger.info("Consumption data loaded")

    # Load the production data
    try:
        df_production = pd.read_csv(
            PATHS["production"] + "parsed_hourly_" + analysisId + ".csv",
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
    df["Self_consumption_ratio"] = (
        1 - (df["Substraction"] / df["Energy_production"])
    ).round(2)

    # Save the dataframe as a csv file
    df.to_csv(
        PATHS["output"] + "self_consumption_ratio_" + analysisId + ".csv",
        index=False,
        sep=";",
        decimal=",",
        encoding="UTF-8",
    )
    logger.info("File saved")

    self_consumption_avg = df["Self_consumption_ratio"].mean()

    # Return the self consumption ratio and the average
    return df["Self_consumption_ratio"].tolist(), self_consumption_avg


def process_results_time_slot_solar(analysisId: str) -> None:
    """
    Calculates the results of the time slot analysis

    :param analysisId: id of the user
    :return: None
    """

    # Load the consumption data
    try:
        df_consumption = pd.read_csv(
            PATHS["consumption"] + "parsed_hourly_" + analysisId + ".csv",
            sep=";",
            decimal=",",
            thousands=".",
            encoding="UTF-8",
        )
    except FileNotFoundError:
        raise FileNotFoundError("Consumption file not found")
    logger.info("Consumption data loaded")

    # Load the production data
    try:
        df_production = pd.read_csv(
            PATHS["production"] + "parsed_hourly_" + analysisId + ".csv",
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

    # Create datetime column
    # TODO: Datetime 2022???
    df["Datetime"] = df.apply(
        lambda x: datetime.datetime(
            2022, int(x["Month"]), int(x["Day"]), int(x["Hour"])
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
    df = (
        df.groupby(["Month"])
        .agg(
            {
                "Surpluses": "sum",
                "Consumption_after_self_consumption": "sum",
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
            "Surpluses",
            "14h_Promocionadas",
            "14h_No promocionadas",
            "6h_Promocionadas",
            "6h_No promocionadas",
            "16h_Promocionadas",
            "16h_No promocionadas",
        ]
    )

    # Save the results
    df.to_csv(
        PATHS["output"] + "results_time_slot_" + analysisId + ".csv",
        sep=";",
        decimal=".",
        encoding="UTF-8",
    )

    logger.info("Self consumption results saved")

    process_results_time_slot_energy(analysisId)

    logger.info("Consumption results saved")


def plot_self_consumption_monthly(analysisId: str) -> None:
    """
    Calculate the self consumption for each month and generate the charts for each
    month.

    Return the total self consumption

    :param analysisId: The id of the analysis
    """

    # Load the consumption data
    try:
        df_consumption = pd.read_csv(
            PATHS["consumption"] + "parsed_hourly_" + analysisId + ".csv",
            sep=";",
            decimal=",",
            encoding="UTF-8",
        )
    except FileNotFoundError:
        logger.error("The consumption file does not exist")
        raise FileNotFoundError("The consumption file does not exist")

    # Load the production data
    try:
        df_production = pd.read_csv(
            PATHS["production"] + "parsed_hourly_" + analysisId + ".csv",
            sep=";",
            decimal=",",
            encoding="UTF-8",
        )
    except FileNotFoundError:
        logger.error("The production file does not exist")
        raise FileNotFoundError("The production file does not exist")

    # Merge the dataframes
    df = pd.merge(
        df_consumption,
        df_production,
        on=["Month", "Day", "Hour"],
        how="left",
        suffixes=("_consumption", "_production"),
    )

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
    df.to_csv(
        PATHS["output"] + "results_monthly_" + analysisId + ".csv",
        sep=";",
        decimal=".",
        encoding="UTF-8",
    )
    logger.info("Monthly results saved")

    # Plot the results for each month
    for month in range(1, 13):
        df_month = df[df["Month"] == month]
        df_month.plot(
            x="Hour",
            y=["Energy_consumption", "Energy_production"],
            kind="line",
            title="Month " + str(month),
            ylabel="Energy (kWh)",
            xlabel="Hour",
        )
        # Wider plot
        plt.gcf().set_size_inches(15, 8)
        plt.savefig(
            PATHS["plots"] + "results_monthly_" + analysisId + "_" + str(month) + ".png"
        )
        plt.close()

    logger.info("Monthly plots saved")
