# import tools.energy_analysis_lib as sa
# import tools.api_wrapper as api
import tools.energy_analysis_lib.core as core
import uuid

# sa.parse_consumption_file(csv_file=consumption_file_path, analysisId="1")

# coords = api.get_coordinates(location="Leganes")
# print(coords)

# api.get_monthly_production(location="Leganes", peakpower=4.55, mountingplace="building", loss=18, angle=20, aspect=-15, analysisId="1")
# api.get_hourly_production(location="Leganes", peakpower=4.55, mountingplace="building", loss=18, angle=20, aspect=-15, analysisId="1")

# sa.consumption_production_chart(location="Leganes", peakpower=4.55, mountingplace="free", loss=0.18, angle=30, aspect=-10, analysisId="1")


# sa.parse_monthly_production_file(analysisId="1")

# sa.parse_hourly_production_file(analysisId="1")

#  print(sa.get_self_consumption_ratio(analysisId="1"))

# sa.get_results_time_slot("1")

# sa.self_consumption_monthly(analysisId="1")

# a = sa.solar_calculation(
#     consumption_file_path,
#     location="Leganes",
#     peakpower=4.55,
#     mountingplace="building",
#     loss=18,
#     angle=20,
#     aspect=-15,
# )
# Print all types of returns in a
# print(a)

# sa.parse_consumption_file(consumption_file_path, analysisId="1234")

# print(PATHS.consumption)

analysisId = uuid.uuid3(uuid.NAMESPACE_DNS, "1")
# To string
analysisId = str(analysisId)


def main():
    with open("tools/data/consumos.csv", "rb") as f:
        core.parse_consumption_file(f, analysisId)


if __name__ == "__main__":
    main()
