import os
import zipfile
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from rich.progress import Progress

from fix_cbz_image import console
from fix_cbz_image.converter import convert_img_data, LibJxlError
from tool_helper.console import for_print_path


class TaskMessage:
    file_path: str

    def __init__(self, file_path: str):
        self.file_path = file_path


class TaskCheckingMessage(TaskMessage):
    completed: int
    total: int

    def __init__(self, file_path: str, completed: int, total: int):
        super().__init__(file_path)
        self.completed = completed
        self.total = total


class TaskUpdatingMessage(TaskMessage):
    completed: int
    total: int

    def __init__(self, file_path: str, completed: int, total: int):
        super().__init__(file_path)
        self.completed = completed
        self.total = total


class TaskCompletedMessage(TaskMessage):
    def __init__(self, file_path: str):
        super().__init__(file_path)


class TaskErrorMessage(TaskMessage):
    error: str

    def __init__(self, file_path: str, error: str):
        super().__init__(file_path)
        self.error = error


class HandleTask:
    __threads: ThreadPoolExecutor | None
    __progress: Progress | None
    __queue: Queue[TaskMessage]
    __tasks: dict

    def __init__(self):
        self.__threads = None
        self.__progress = None
        self.__queue = Queue()
        self.__tasks = {}

    def __enter__(self):
        threads = ThreadPoolExecutor()
        progress = Progress()
        self.__threads = threads.__enter__()
        self.__progress = progress.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__progress.__exit__(exc_type, exc_val, exc_tb)
        self.__threads.__exit__(exc_type, exc_val, exc_tb)

    def submit(self, file_path: str):
        task_id = self.__progress.add_task("", visible=False)
        self.__tasks[file_path] = task_id
        self.__threads.submit(process_file, file_path, self)

    def send_message(self, message: TaskMessage):
        self.__queue.put(message)

    def show_progress(self):
        while len(self.__tasks) != 0:
            message = self.__queue.get()
            if not isinstance(message, TaskMessage):
                continue
            task = self.__tasks.get(message.file_path)
            if task is None:
                continue

            if isinstance(message, TaskCheckingMessage):
                self.__progress.update(
                    task, total=message.total, completed=message.completed, visible=True,
                    description=f"[blue]Check {for_print_path(os.getcwd(), message.file_path)}"
                )
            elif isinstance(message, TaskUpdatingMessage):
                self.__progress.update(
                    task, total=message.total, completed=message.completed, visible=True,
                    description=f"[yellow]Update {for_print_path(os.getcwd(), message.file_path)}"
                )
            elif isinstance(message, TaskCompletedMessage):
                self.__progress.update(task, visible=False)
                del self.__tasks[message.file_path]
            elif isinstance(message, TaskErrorMessage):
                console.print(f"[red]{message.error}[/red]")


def process_file(file_path, task: HandleTask):
    if not check_zip_file(file_path, task):
        task.send_message(TaskCompletedMessage(file_path))
        return
    process_zip_file(file_path, task)
    task.send_message(TaskCompletedMessage(file_path))


def check_zip_file(zip_path, task: HandleTask):
    changes_made = False

    with zipfile.ZipFile(zip_path, 'r') as original_zip:
        infolist = original_zip.infolist()
        total = len(infolist)

        for i, item in enumerate(infolist):
            if changes_made:
                break
            with original_zip.open(item.filename) as original_zip_file:
                try:
                    data = original_zip_file.read()
                    if convert_img_data(data, item.filename, dry=True):
                        changes_made = True
                except LibJxlError as e:
                    task.send_message(TaskErrorMessage(zip_path, e.message))
            task.send_message(TaskCheckingMessage(zip_path, i + 1, total))

        task.send_message(TaskCheckingMessage(zip_path, total, total))

    return changes_made


def process_zip_file(zip_path, task: HandleTask):
    temp_zip_path = zip_path + ".tmp"
    changes_made = False

    with zipfile.ZipFile(zip_path, 'r') as original_zip:
        with zipfile.ZipFile(temp_zip_path, 'w', compression=zipfile.ZIP_STORED) as new_zip:
            infolist = original_zip.infolist()
            total = len(infolist)

            for i, item in enumerate(infolist):
                with original_zip.open(item.filename) as original_zip_file:
                    try:
                        data = original_zip_file.read()
                        converted_data = convert_img_data(data, item.filename)
                    except LibJxlError as e:
                        task.send_message(TaskErrorMessage(zip_path, e.message))
                        converted_data = None

                    if converted_data is None:
                        new_zip.writestr(item.filename, data)
                    else:
                        new_data, ext = converted_data
                        new_filename = f"{os.path.splitext(item.filename)[0]}.{ext}"
                        new_zip.writestr(new_filename, new_data)
                        changes_made = True

                task.send_message(TaskUpdatingMessage(zip_path, i + 1, total))

    # Replace the original ZIP file only if changes were made
    if changes_made:
        os.replace(temp_zip_path, zip_path)
    else:
        os.remove(temp_zip_path)
