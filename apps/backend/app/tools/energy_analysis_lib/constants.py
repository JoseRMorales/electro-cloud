import os

TIME_SLOTS = {
    "nocturna": {
        "Valle": [(1, 8)],  # 00:00 - 07:59
        "Llana": [
            (9, 10),
            (15, 18),
            (23, 24),
        ],  # 08:00 - 09:59, 14:00 - 17:59, 22:00 - 23:59
        "Punta": [(11, 14), (19, 22)],  # 10:00 - 13:59, 18:00 - 21:59
    },
    "14h": {
        "Promocionadas": [(23, 12)],  # 22:00 - 11:59
        "No promocionadas": [(13, 22)],  # 12:00 - 21:59
    },
    "6h": {
        "Promocionadas": [(2, 7)],  # 01:00 - 06:59
        "No promocionadas": [(8, 1)],  # 07:00 - 00:59
    },
    "16h": {
        "Promocionadas": [(18, 9)],  # 17:00 - 08:59
        "No promocionadas": [(10, 17)],  # 09:00 - 16:59
    },
}

output_path = os.environ.get("OUTPUT_PATH", "output")

PATHS = {
    "consumption": os.path.join(output_path, "consumption"),
    "production": os.path.join(output_path, "production"),
    "plots": os.path.join(output_path, "plots"),
    "results": os.path.join(output_path, "results"),
    "time_slots": os.path.join(output_path, "time_slots"),
    "locations": os.path.join(output_path, "locations"),
}

PATHS["consumption_parsed_hourly"] = os.path.join(PATHS["consumption"], "parsed_hourly")

PATHS["consumption_parsed_monthly"] = os.path.join(
    PATHS["consumption"], "parsed_monthly"
)

PATHS["production_parsed_hourly"] = os.path.join(PATHS["production"], "parsed_hourly")

PATHS["production_parsed_monthly"] = os.path.join(PATHS["production"], "parsed_monthly")
PATHS["production_hourly"] = os.path.join(PATHS["production"], "hourly")
PATHS["production_monthly"] = os.path.join(PATHS["production"], "monthly")
PATHS["results_self_consumption"] = os.path.join(PATHS["results"], "self_consumption")
PATHS["plots_consumption_production_chart"] = os.path.join(
    PATHS["plots"], "consumption_production_chart"
)
PATHS["plots_monthly"] = os.path.join(PATHS["plots"], "monthly")
