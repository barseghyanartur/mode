import asyncio
from unittest.mock import Mock
from mode import Service
import pytest


class S(Service):

    def on_init(self):
        self.on_started_log = Mock()
        self.on_stopped_log = Mock()
        self.on_shutdown_log = Mock()

    async def on_start(self):
        self.on_started_log()

    async def on_stop(self):
        self.on_stopped_log()

    async def on_shutdown(self):
        self.on_shutdown_log()


@pytest.mark.asyncio
async def test_start_stop():
    s = S()
    assert s.state == 'init'
    await s.maybe_start()
    await s.maybe_start()
    assert s.state == 'running'
    s.on_started_log.assert_called_with()
    await s.stop()
    s.on_stopped_log.assert_called_with()
    s.on_shutdown_log.assert_called_with()
    assert s.state == 'stopping'


def test_state_stopped():
    s = S()
    s._started.set()
    s._stopped.set()
    s._shutdown.set()
    assert s.state == 'shutdown'


@pytest.mark.asyncio
async def test_aenter():
    s = S()
    async with s:
        s.on_started_log.assert_called_with()
    s.on_stopped_log.assert_called_with()
    s.on_shutdown_log.assert_called_with()


@pytest.mark.asyncio
async def test_interface():
    s = Service()
    s.on_init()
    await s.on_start()
    await s.on_stop()
    await s.on_shutdown()


def test_repr():
    assert repr(S())


@pytest.mark.asyncio
async def test_subclass_can_override_Service_task():

    class ATaskService(Service):
        values = []

        def on_init(self):
            self.event = asyncio.Event(loop=self.loop)

        @Service.task
        async def _background_task(self):
            self.values.append(1)
            self.event.set()

    class BTaskService(ATaskService):

        @Service.task
        async def _background_task(self):
            self.values.append(2)
            self.event.set()

    service = BTaskService()
    await service.start()
    await service.event.wait()
    await service.stop()

    assert ATaskService.values == [2]
