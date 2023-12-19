# """Asynchronous Python client for Withings."""
#
# import aiohttp
# from aresponses import ResponsesMockServer
# import pytest
#
# from aiowithings import (
#     NotificationCategory,
#     WebhookCall,
#     WithingsClient,
#     get_measurement_type_from_notification_category,
# )
# from syrupy import SnapshotAssertion
#
# from . import load_fixture
#
# WITHINGS_URL = "wbsapi.withings.net"
#
#
# async def test_subscribing(
#     aresponses: ResponsesMockServer,
# ) -> None:
#     """Test subscribing to webhook updates."""
#     aresponses.add(
#         WITHINGS_URL,
#         "/notify",
#         "POST",
#         aresponses.Response(
#             status=200,
#             headers={"Content-Type": "application/json"},
#             text=load_fixture("notify_subscribe.json"),
#         ),
#         body_pattern="action=subscribe&callbackurl=https%3A%2F%2Ftest.com%2Fcallback&appli=4",
#     )
#     async with aiohttp.ClientSession() as session:
#         withings = WithingsClient(session=session)
#         withings.authenticate("test")
#         await withings.subscribe_notification(
#             "https://test.com/callback",
#             NotificationCategory.PRESSURE,
#         )
#         await withings.close()
#
#
# async def test_revoking(
#     aresponses: ResponsesMockServer,
# ) -> None:
#     """Test subscribing to webhook updates."""
#     aresponses.add(
#         WITHINGS_URL,
#         "/notify",
#         "POST",
#         aresponses.Response(
#             status=200,
#             headers={"Content-Type": "application/json"},
#             text=load_fixture("notify_revoke.json"),
#         ),
#         body_pattern="action=revoke&callbackurl=https%3A%2F%2Ftest.com%2Fcallback&appli=4",
#     )
#     async with aiohttp.ClientSession() as session:
#         withings = WithingsClient(session=session)
#         withings.authenticate("test")
#         await withings.revoke_notification_configurations(
#             "https://test.com/callback",
#             NotificationCategory.PRESSURE,
#         )
#         await withings.close()
#
#
# async def test_list_subscriptions(
#     aresponses: ResponsesMockServer,
#     snapshot: SnapshotAssertion,
# ) -> None:
#     """Test retrieving subscriptions."""
#     aresponses.add(
#         WITHINGS_URL,
#         "/notify",
#         "POST",
#         aresponses.Response(
#             status=200,
#             headers={"Content-Type": "application/json"},
#             text=load_fixture("notify_list.json"),
#         ),
#         body_pattern="action=list&appli=1",
#     )
#     async with aiohttp.ClientSession() as session:
#         withings = WithingsClient(session=session)
#         withings.authenticate("test")
#         response = await withings.list_notification_configurations(
#             NotificationCategory.WEIGHT,
#         )
#         assert response == snapshot
#         await withings.close()
#
#
# async def test_list_all_subscriptions(
#     aresponses: ResponsesMockServer,
# ) -> None:
#     """Test retrieving all subscriptions."""
#     aresponses.add(
#         WITHINGS_URL,
#         "/notify",
#         "POST",
#         aresponses.Response(
#             status=200,
#             headers={"Content-Type": "application/json"},
#             text=load_fixture("notify_list.json"),
#         ),
#         body_pattern="action=list",
#     )
#     async with aiohttp.ClientSession() as session:
#         withings = WithingsClient(session=session)
#         withings.authenticate("test")
#         response = await withings.list_notification_configurations()
#         assert response
#         await withings.close()
#
#
# @pytest.mark.parametrize(
#     "notification_category",
#     list(NotificationCategory),
#     ids=[nc.name for nc in NotificationCategory],
# )
# async def test_measurement_points_to_get(
#     notification_category: NotificationCategory,
#     snapshot: SnapshotAssertion,
# ) -> None:
#     """Test if we receive the right updated measurement points."""
#     assert (
#         get_measurement_type_from_notification_category(notification_category)
#         == snapshot
#     )
#
#
# async def test_webhook_object(snapshot: SnapshotAssertion) -> None:
#     """Test if the webhook call transforms in a good object."""
#     data = {
#         "userid": 12345,
#         "appli": 1,
#         "startdate": 1530576000,
#         "enddate": 1530698753,
#     }
#     assert WebhookCall.from_api(data) == snapshot
