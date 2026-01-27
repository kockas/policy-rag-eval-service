from __future__ import annotations

import asyncio
from dataclasses import dataclass

from policy_rag_eval.models.run import RunState
from policy_rag_eval.stores.runs import InMemoryRunStore, RunTaskRegistry
from policy_rag_eval.stores.events import InMemoryEventStore

@dataclass
class AsyncRunner:
    run_store: InMemoryRunStore
    tasks: RunTaskRegistry
    event_store: InMemoryEventStore

    async def _run(self, run_id: str, question: str) -> None:
        """
        The actual execution body (async).
        Later this becomes: ingest/retrieve/generate/eval pipeline.
        """
        self.run_store.set_state(run_id, RunState.RUNNING)
        self.event_store.append(run_id, "run_started", {"question": question})

        try:
            # Simulate I/O-bound work. Replace with real RAG later.
            await asyncio.sleep(1.0)

            # Mark success
            self.run_store.finish(run_id, RunState.SUCCEEDED)
            self.event_store.append(run_id, "run_succeeded")

        except asyncio.CancelledError:
            # If we add cancellation endpoint later.
            self.run_store.finish(run_id, RunState.FAILED)
            self.event_store.append(run_id, "run_failed", {"reason": "cancelled"})
            raise

        except Exception:
            self.run_store.finish(run_id, RunState.FAILED)
            self.event_store.append(run_id, "run_failed", {"reason": "exception", "error": str(e)})

    def submit(self, run_id: str, question: str) -> None:
        """
        Schedule the coroutine on the running event loop.
        FastAPI/uvicorn already run an event loop.
        """
        task = asyncio.create_task(self._run(run_id=run_id, question=question))
        self.tasks.put(run_id, task)

        def _cleanup(t: asyncio.Task) -> None:
            self.tasks.pop(run_id)

        task.add_done_callback(_cleanup)
