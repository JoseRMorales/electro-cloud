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

PATHS = {
    "consumption": "./tools/data/consumption/",
    "production": "./tools/data/production/",
    "plots": "./tools/data/plots/",
    "output": "./tools/data/output/",
}

SUPABASE_STORAGE = {
    "buckets": {
        "energy_analysis": {
            "name": "energy_analysis",
            "consumption": {
                "path": "data/consumption/",
                "monthly_path": "data/consumption/monthly/",
                "hourly_path": "data/consumption/hourly/",
            },
            "production_path": "data/production/",
            "plots_path": "data/plots/",
            "output_path": "data/output/",
        }
    }
}

SUPABASE_TABLES = {
    "energy_analysis": "energy_analysis",
}
