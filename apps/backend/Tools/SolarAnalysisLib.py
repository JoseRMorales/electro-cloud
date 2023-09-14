import pandas as pd
import logging
import Tools.APIwrapper as api
from matplotlib import pyplot as plt
import numpy as np
import datetime
import uuid

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


consumption_path = "Tools/consumption/"
production_path = "Tools/production/"
plots_path = "Tools/plots/"
output_path = "Tools/output/"


def parse_consumption_file(csv_file: bytes, analysisId: str) -> None:
    """
    Converts a csv file with consumption data to a csv file with 3 columns: 'Month',
    'Day', 'Hour', 'Energy'

    :param csv_file: csv file with consumption data
    :param analysisId: id of the user
    :return: None
    """
    logger = logging.getLogger(__name__)

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

    df = df.drop(columns=["Fecha", "Hora"])
    df = df.rename(columns={"Consumo_kWh": "Energy"})

    # At the moment only same year data is supported
    # Throw error if there are multiple rows with same month, day and hour
    if df.duplicated(subset=["Month", "Day", "Hour"]).any():
        raise ValueError("There are multiple rows with same month, day and hour")
    else:
        logger.info("No duplicated rows")

    # Create a dataframe with monthly data
    df_monthly = df.groupby(["Month"]).sum()
    df_monthly = df_monthly.reset_index()

    # Only keep Month and Energy columns
    df_monthly = df_monthly.iloc[:, [0, 1]]

    # Convert the hour 24 to 0
    df["Hour"] = df["Hour"].replace(24, 0)

    # Remove hour 25 corresponding to the change to winter time
    df = df[df["Hour"] != 25]

    # Save the dataframe as a csv file
    df_monthly.to_csv(
        consumption_path + "parsed_monthly_" + analysisId + ".csv",
        index=False,
        sep=";",
        decimal=",",
        encoding="UTF-8",
    )

    # Save the dataframe as a csv file
    df.to_csv(
        consumption_path + "parsed_hourly_" + analysisId + ".csv",
        index=False,
        sep=";",
        decimal=",",
        encoding="UTF-8",
    )
    logger.info("File saved")


def parse_monthly_production_file(analysisId: str) -> None:
    """
    Converts a csv file with monthly production data to a csv file with 2 columns:
    'Month', 'Energy'

    :param analysisId: id of the user
    :return: None
    """
    logger = logging.getLogger(__name__)

    # Import the csv file as a pandas dataframe
    df = pd.read_csv(
        production_path + "monthly_" + analysisId + ".csv",
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
        production_path + "parsed_monthly_" + analysisId + ".csv",
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
    logger = logging.getLogger(__name__)

    # Count file lines
    with open(production_path + "hourly_" + analysisId + ".csv", "r") as f:
        n_lines = sum(1 for line in f)

    # Import the csv file as a pandas dataframe
    df = pd.read_csv(
        production_path + "hourly_" + analysisId + ".csv",
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
        production_path + "parsed_hourly_" + analysisId + ".csv",
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
    logger = logging.getLogger(__name__)

    # Load the consumption data
    try:
        df_consumption = pd.read_csv(
            consumption_path + "parsed_monthly_" + analysisId + ".csv",
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
            production_path + "parsed_monthly_" + analysisId + ".csv",
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
            production_path + "parsed_monthly_" + analysisId + ".csv",
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
    plt.savefig(plots_path + analysisId + ".png", dpi=100)

    # Clear the plot
    plt.clf()

    logger.info("Chart saved")


def get_self_consumption_ratio(analysisId: str) -> (list[float], float):
    """
    Calculates the self consumption ratio of a location

    :param analysisId: id of the user
    :return: list of self consumption ratios, average self consumption ratio
    """
    logger = logging.getLogger(__name__)

    # Load the consumption data
    try:
        df_consumption = pd.read_csv(
            consumption_path + "parsed_hourly_" + analysisId + ".csv",
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
            production_path + "parsed_hourly_" + analysisId + ".csv",
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
        output_path + "self_consumption_ratio_" + analysisId + ".csv",
        index=False,
        sep=";",
        decimal=",",
        encoding="UTF-8",
    )
    logger.info("File saved")

    self_consumption_avg = df["Self_consumption_ratio"].mean()

    # Return the self consumption ratio and the average
    return df["Self_consumption_ratio"].tolist(), self_consumption_avg


time_slots = {
    "nocturna": {
        "Valle": [(0, 7)],  # 00:00 - 07:59
        "Llana": [
            (8, 9),
            (14, 17),
            (22, 23),
        ],  # 08:00 - 09:59, 14:00 - 17:59, 22:00 - 23:59
        "Punta": [(10, 13), (18, 21)],  # 10:00 - 13:59, 18:00 - 21:59
    },
    "14h": {
        "Promocionadas": [(22, 11)],  # 22:00 - 11:59
        "No promocionadas": [(12, 21)],  # 12:00 - 21:59
    },
    "6h": {
        "Promocionadas": [(1, 6)],  # 01:00 - 06:59
        "No promocionadas": [(7, 0)],  # 07:00 - 00:59
    },
    "16h": {
        "Promocionadas": [(17, 8)],  # 17:00 - 08:59
        "No promocionadas": [(9, 16)],  # 09:00 - 16:59
    },
}


def is_within_time_slot(
    hour: int,
    time_slot: list[(int, int)],
    date: datetime,
    time_slot_name: str,
    time_slot_type: str,
) -> bool:
    """
    Checks if the hour is within the time slot

    :param hour: hour to check
    :param time_slot: time slot to check
    :return: True if the hour is within the time slot, False otherwise
    """
    # If the time slot is nocturna, the time_slot_type is 'Valle' and is weekend,
    # return True
    # Workaround to avoid repetitions in weekend
    if time_slot_name == "nocturna" and date.weekday() >= 5:
        if time_slot_type == "Valle":
            return True
        else:
            return False

    for start, end in time_slot:
        if start > end:
            if hour >= start or hour <= end:
                return True
        else:
            if start <= hour <= end:
                return True

    return False


def get_results_time_slot(analysisId: str) -> None:
    """
    Calculates the results of the time slot analysis

    :param analysisId: id of the user
    :return: None
    """
    logger = logging.getLogger(__name__)

    # Load the consumption data
    try:
        df_consumption = pd.read_csv(
            consumption_path + "parsed_hourly_" + analysisId + ".csv",
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
            production_path + "parsed_hourly_" + analysisId + ".csv",
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
    df["Datetime"] = df.apply(
        lambda x: datetime.datetime(
            2022, int(x["Month"]), int(x["Day"]), int(x["Hour"])
        ),
        axis=1,
    )

    # Create a new column with each time slot
    for time_slot_name, time_slot in time_slots.items():
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
        output_path + "results_time_slot_" + analysisId + ".csv",
        sep=";",
        decimal=".",
        encoding="UTF-8",
    )

    logger.info("Self consumption results saved")

    # Create datetime column
    df_consumption["Datetime"] = df_consumption.apply(
        lambda x: datetime.datetime(
            2022, int(x["Month"]), int(x["Day"]), int(x["Hour"])
        ),
        axis=1,
    )

    # Create a new column with each time slot
    for time_slot_name, time_slot in time_slots.items():
        for time_slot_type, time_slot_hours in time_slot.items():
            df_consumption[
                time_slot_name + "_" + time_slot_type
            ] = df_consumption.apply(
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
    df_consumption = (
        df_consumption.groupby(["Month"])
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
    df_consumption = df_consumption.transpose()

    # Order rows. In this order nocturna_punta, nocturna_llana, nocturna_valle,
    # surpluses, 14h_promocionadas, 14h_no_promocionadas, 6h_promocionadas, 6h_no_promocionadas, 16h_promocionadas, 16h_no_promocionadas
    df_consumption = df_consumption.reindex(
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
    df_consumption.to_csv(
        output_path + "results_time_slot_consumption_" + analysisId + ".csv",
        sep=";",
        decimal=".",
        encoding="UTF-8",
    )

    logger.info("Consumption results saved")


def self_consumption_monthly(analysisId: str):
    """
    Calculate the self consumption for each month and generate the charts for each
    month.

    Return the total self consumption

    :param analysisId: The id of the analysis
    """
    logger = logging.getLogger(__name__)

    # Load the consumption data
    try:
        df_consumption = pd.read_csv(
            consumption_path + "parsed_hourly_" + analysisId + ".csv",
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
            production_path + "parsed_hourly_" + analysisId + ".csv",
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
        output_path + "results_monthly_" + analysisId + ".csv",
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
            plots_path + "results_monthly_" + analysisId + "_" + str(month) + ".png"
        )
        plt.close()

    logger.info("Monthly plots saved")


# API methods


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
    logger = logging.getLogger(__name__)

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
    parse_hourly_production_file(analysisId)
    parse_monthly_production_file(analysisId)

    # Generate consumption vs production plot
    consumption_production_chart(
        location, peakpower, mountingplace, loss, angle, aspect, analysisId
    )

    # Calculate the self consumption
    self_consumption_monthly(analysisId)

    # Get the time slot consumption
    get_results_time_slot(analysisId)

    return analysisId


def get_monthly_production(analysisId: str) -> bytes:
    """
    Return the monthly production data to the api.

    :param analysisId: The id of the analysis
    """
    logger = logging.getLogger(__name__)
    try:
        production_file = open(
            production_path + "parsed_monthly_" + analysisId + ".csv", "rb"
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
    logger = logging.getLogger(__name__)
    try:
        consumption_file = open(
            consumption_path + "parsed_monthly_" + analysisId + ".csv", "rb"
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
    logger = logging.getLogger(__name__)
    try:
        consumption_production_plot = open(plots_path + analysisId + ".png", "rb")
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
    logger = logging.getLogger(__name__)
    results_monthly = []
    try:
        for month in range(1, 13):
            results_monthly.append(
                open(
                    plots_path
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
    logger = logging.getLogger(__name__)

    monthly_ratios, average = get_self_consumption_ratio(analysisId)

    return {"monthly_ratios": monthly_ratios, "average": average}


def get_results_time_slot_consumption(analysisId: str) -> bytes:
    """
    Return the time slot consumption results to the api.

    :param analysisId: The id of the analysis
    """
    logger = logging.getLogger(__name__)
    try:
        results_time_slot = open(
            output_path + "results_time_slot_consumption_" + analysisId + ".csv", "rb"
        )
    except FileNotFoundError:
        logger.error("The time slot results do not exist")
        raise FileNotFoundError("The time slot results do not exist")

    return results_time_slot.read()


def get_results_time_slot_solar(analysisId: str) -> bytes:
    """
    Return the time slot solar results to the api.

    :param analysisId: The id of the analysis
    """
    logger = logging.getLogger(__name__)
    try:
        results_time_slot_solar = open(
            output_path + "results_time_slot_" + analysisId + ".csv", "rb"
        )
    except FileNotFoundError:
        logger.error("The time slot results after solar do not exist")
        raise FileNotFoundError("The time slot results after solar do not exist")

    return results_time_slot_solar.read()
