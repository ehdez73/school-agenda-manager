import uuid
import threading
import time
import logging


logger = logging.getLogger(__name__)


class TaskManager:
    """Thread-safe in-memory tracker for async timetable generation tasks."""

    def __init__(self):
        self._tasks = {}
        self._lock = threading.Lock()
        self._cancelled = set()
        self._current_task_id = None
        self._last_task_id = None

    def has_running_task(self):
        with self._lock:
            if not self._current_task_id:
                return False
            task = self._tasks.get(self._current_task_id)
            if not task or task.get("status") != "running":
                self._current_task_id = None
                return False
            return True

    def get_current_task_id(self):
        with self._lock:
            if not self._current_task_id:
                return None
            task = self._tasks.get(self._current_task_id)
            if not task or task.get("status") != "running":
                self._current_task_id = None
                return None
            return self._current_task_id

    def get_latest_task_id(self):
        with self._lock:
            if self._last_task_id in self._tasks:
                return self._last_task_id
            return None

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
            self._current_task_id = task_id
            self._last_task_id = task_id
        logger.info("Task created id=%s", task_id)
        return task_id

    def complete_task(self, task_id):
        with self._lock:
            if task_id in self._tasks and task_id not in self._cancelled:
                self._tasks[task_id]["status"] = "success"
                if self._current_task_id == task_id:
                    self._current_task_id = None
                logger.info("Task marked success id=%s", task_id)

    def fail_task(self, task_id, error, details=None):
        with self._lock:
            if task_id in self._tasks and task_id not in self._cancelled:
                self._tasks[task_id]["status"] = "error"
                self._tasks[task_id]["error"] = error
                self._tasks[task_id]["details"] = details
                if self._current_task_id == task_id:
                    self._current_task_id = None
                logger.warning("Task marked error id=%s", task_id)

    def cancel_task(self, task_id):
        with self._lock:
            self._cancelled.add(task_id)
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "cancelled"
            if self._current_task_id == task_id:
                self._current_task_id = None
        logger.info("Task marked cancelled id=%s", task_id)

    def is_cancelled(self, task_id):
        return task_id in self._cancelled

    def update_progress(self, task_id, phase, phase_details):
        with self._lock:
            if task_id in self._tasks and task_id not in self._cancelled:
                self._tasks[task_id]["phase"] = phase
                self._tasks[task_id]["phase_details"] = phase_details
                logger.debug("Task progress updated id=%s phase=%s", task_id, phase)

    def get_status(self, task_id):
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            return {
                "task_id": task_id,
                "status": task["status"],
                "error": task.get("error"),
                "details": task.get("details"),
                "phase": task.get("phase"),
                "phase_details": task.get("phase_details"),
                "created_at": task.get("created_at"),
            }

    def get_current_status(self):
        with self._lock:
            if not self._current_task_id:
                return None
            task = self._tasks.get(self._current_task_id)
            if not task or task.get("status") != "running":
                self._current_task_id = None
                return None
            return {
                "task_id": self._current_task_id,
                "status": task["status"],
                "error": task.get("error"),
                "details": task.get("details"),
                "phase": task.get("phase"),
                "phase_details": task.get("phase_details"),
                "created_at": task.get("created_at"),
            }

    def get_latest_status(self):
        with self._lock:
            if not self._last_task_id:
                return None
            task = self._tasks.get(self._last_task_id)
            if not task:
                self._last_task_id = None
                return None
            return {
                "task_id": self._last_task_id,
                "status": task["status"],
                "error": task.get("error"),
                "details": task.get("details"),
                "phase": task.get("phase"),
                "phase_details": task.get("phase_details"),
                "created_at": task.get("created_at"),
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
                    if self._current_task_id == tid:
                        self._current_task_id = None
                    if self._last_task_id == tid:
                        self._last_task_id = None
                if expired:
                    logger.info("Task cleanup removed expired tasks count=%d", len(expired))


task_manager = TaskManager()
