import datetime


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
