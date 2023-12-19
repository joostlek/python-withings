# """Asynchronous Python client for Withings."""
# from datetime import datetime, timezone
#
# import aiohttp
# from aresponses import ResponsesMockServer
#
# from aiowithings import WithingsClient
# from aiowithings.models import MeasurementType
# from syrupy import SnapshotAssertion
#
# from . import load_fixture
#
# WITHINGS_URL = "wbsapi.withings.net"
#
#
# async def test_get_measurement_since(
#     aresponses: ResponsesMockServer,
#     snapshot: SnapshotAssertion,
# ) -> None:
#     """Test retrieving measurements."""
#     aresponses.add(
#         WITHINGS_URL,
#         "/measure",
#         "POST",
#         aresponses.Response(
#             status=200,
#             headers={"Content-Type": "application/json"},
#             text=load_fixture("measurement.json"),
#         ),
#     )
#     async with aiohttp.ClientSession() as session:
#         withings = WithingsClient(session=session)
#         withings.authenticate("test")
#         response = await withings.get_measurement_since(
#             datetime.now(tz=timezone.utc),
#             measurement_types=[MeasurementType.WEIGHT],
#         )
#         assert response == snapshot
#         await withings.close()
#
#
# async def test_get_measurement_period(
#     aresponses: ResponsesMockServer,
#     snapshot: SnapshotAssertion,
# ) -> None:
#     """Test retrieving measurements."""
#     aresponses.add(
#         WITHINGS_URL,
#         "/measure",
#         "POST",
#         aresponses.Response(
#             status=200,
#             headers={"Content-Type": "application/json"},
#             text=load_fixture("measurement.json"),
#         ),
#     )
#     async with aiohttp.ClientSession() as session:
#         withings = WithingsClient(session=session)
#         withings.authenticate("test")
#         response = await withings.get_measurement_in_period(
#             start_date=datetime.now(tz=timezone.utc),
#             end_date=datetime.now(tz=timezone.utc),
#         )
#         assert response == snapshot
#         await withings.close()
