import time

from taskified import tasks

# Declare constants
FPS_AVG_WINDOW = 5


# Helper functions
def init_fps_counts():
    return [0] * len(tasks)


def get_task_names():
    return [task.__name__ for task in tasks]


# Variables for state
task_index = 0
fps_counts = init_fps_counts()
task_names = get_task_names()


def run_with_fps(task_func, args):
    # Increment fps counter
    fps_counts[task_index] += 1

    # Call task
    if args is None:
        # No args to pass
        return task_func()
    elif type(args) is tuple:
        # Unzip tuple into args
        return task_func(*args)
    else:
        # Single arg
        return task_func(args)


# To keep track of FPS
start_time = time.time()

# Init tasks args
next_task_args = None

# Keep running tasks in sequential order
while True:

    # Determine which task to run
    task = tasks[task_index]

    # Run task
    to_continue, next_task_args = run_with_fps(task_func=task, args=next_task_args)

    # Calculate fps
    end_time = time.time()
    if (end_time - start_time) > FPS_AVG_WINDOW:
        # Calculate FPS of each task
        real_fps_list = [fps_count / (end_time - start_time) for fps_count in fps_counts]
        print(list(zip(task_names, real_fps_list)))

        # Reset vars for fps
        fps_counts = init_fps_counts()
        start_time = time.time()

    # No need to continue running tasks, end of stream
    if to_continue is False and task_index == 0:
        break

    # Increment index (cyclical)
    task_index += 1

    # Reset to first frame if more function calls are not needed or reached end of sequence
    if to_continue is False or task_index >= len(tasks):
        task_index = 0
        next_task_args = None
        continue
