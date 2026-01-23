from __future__ import annotations

import asyncio
from dataclasses import dataclass

from policy_rag_eval.models.run import RunState
from policy_rag_eval.stores.runs import InMemoryRunStore, RunTaskRegistry


@dataclass
class AsyncRunner:
    run_store: InMemoryRunStore
    tasks: RunTaskRegistry

    async def _run(self, run_id: str, question: str) -> None:
        """
        The actual execution body (async).
        Later this becomes: ingest/retrieve/generate/eval pipeline.
        """
        self.run_store.set_state(run_id, RunState.RUNNING)

        try:
            # Simulate I/O-bound work. Replace with real RAG later.
            await asyncio.sleep(1.0)

            # Mark success
            self.run_store.finish(run_id, RunState.SUCCEEDED)

        except asyncio.CancelledError:
            # If we add cancellation endpoint later.
            self.run_store.finish(run_id, RunState.FAILED)
            raise

        except Exception:
            self.run_store.finish(run_id, RunState.FAILED)

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
