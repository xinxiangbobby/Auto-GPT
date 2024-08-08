import pytest

from autogpt_server.data import db, graph
from autogpt_server.executor import ExecutionScheduler
from autogpt_server.usecases.sample import create_test_graph, create_test_user
from autogpt_server.util.service import get_service_client


@pytest.mark.skip(reason="flakey test, needs to be investigated")
@pytest.mark.asyncio(scope="session")
async def test_agent_schedule(server):
    await db.connect()
    test_user = await create_test_user()
    test_graph = await graph.create_graph(create_test_graph(), user_id=test_user.id)

    scheduler = get_service_client(ExecutionScheduler)

    schedules = scheduler.get_execution_schedules(test_graph.id, test_user.id)
    assert len(schedules) == 0

    schedule_id = scheduler.add_execution_schedule(
        graph_id=test_graph.id,
        user_id=test_user.id,
        graph_version=1,
        cron="0 0 * * *",
        input_data={"input": "data"},
    )
    assert schedule_id

    schedules = scheduler.get_execution_schedules(test_graph.id, test_user.id)
    assert len(schedules) == 1
    assert schedules[schedule_id] == "0 0 * * *"

    scheduler.update_schedule(schedule_id, is_enabled=False)
    schedules = scheduler.get_execution_schedules(test_graph.id)
    assert len(schedules) == 0
