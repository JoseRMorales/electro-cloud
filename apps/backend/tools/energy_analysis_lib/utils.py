import datetime
import io
import pandas as pd
from supabase import create_client, Client
import os


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


def get_supabase_client() -> Client:
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

    return supabase
