import uuid
import threading
import time


class TaskManager:
    """Thread-safe in-memory tracker for async timetable generation tasks."""

    def __init__(self):
        self._tasks = {}
        self._lock = threading.Lock()
        self._cancelled = set()

    def create_task(self) -> str:
        self._lazy_cleanup()
        task_id = str(uuid.uuid4())
        with self._lock:
            self._tasks[task_id] = {
                "status": "running",
                "error": None,
                "details": None,
                "created_at": time.time(),
            }
        return task_id

    def complete_task(self, task_id):
        with self._lock:
            if task_id in self._tasks and task_id not in self._cancelled:
                self._tasks[task_id]["status"] = "success"

    def fail_task(self, task_id, error, details=None):
        with self._lock:
            if task_id in self._tasks and task_id not in self._cancelled:
                self._tasks[task_id]["status"] = "error"
                self._tasks[task_id]["error"] = error
                self._tasks[task_id]["details"] = details

    def cancel_task(self, task_id):
        with self._lock:
            self._cancelled.add(task_id)
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "cancelled"

    def is_cancelled(self, task_id):
        return task_id in self._cancelled

    def update_progress(self, task_id, phase, phase_details):
        with self._lock:
            if task_id in self._tasks and task_id not in self._cancelled:
                self._tasks[task_id]["phase"] = phase
                self._tasks[task_id]["phase_details"] = phase_details

    def get_status(self, task_id):
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            return {
                "status": task["status"],
                "error": task.get("error"),
                "details": task.get("details"),
                "phase": task.get("phase"),
                "phase_details": task.get("phase_details"),
            }

    def _lazy_cleanup(self, max_age=600, max_tasks=50):
        now = time.time()
        with self._lock:
            if len(self._tasks) > max_tasks:
                expired = [
                    tid
                    for tid, t in self._tasks.items()
                    if now - t["created_at"] > max_age
                ]
                for tid in expired:
                    del self._tasks[tid]
                    self._cancelled.discard(tid)


task_manager = TaskManager()
