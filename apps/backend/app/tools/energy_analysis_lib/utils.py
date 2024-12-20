import datetime
import io
import os

import pandas as pd


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
    # TODO: National holidays
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


def save_csv_to_variable(df: pd.DataFrame) -> io.BytesIO:
    """
    Save the CSV data to a variable.

    :param df: The monthly consumption data
    :return: The CSV data as a string
    """
    csv_buffer = io.StringIO()
    df.to_csv(
        csv_buffer,
        index=True,
        sep=";",
        decimal=",",
        encoding="UTF-8",
    )
    csv_buffer.seek(0)

    csv_bytes = csv_buffer.getvalue().encode("utf-8")

    return csv_bytes


def save_csv_file(path: str, analysisId: str, df: pd.DataFrame) -> str:
    """
    Save the CSV data to a file.

    :param analysisId: The analysis id
    :param df: The monthly consumption data
    :return: The path to the file
    """

    # Create the path if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)

    # Save the CSV data to a file
    save_path = os.path.join(path, f"{analysisId}.csv")
    df.to_csv(save_path, index=False, sep=";", decimal=",", encoding="UTF-8")

    return str(save_path)
