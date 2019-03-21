import time
import sys

from taskified import tasks

# Show FPS every given number of seconds
FPS_CALC_REPEAT_TIME = 3


# Helper functions
def init_fps_counts():
    return [0] * len(tasks)


def init_task_names():
    return [task.__name__ for task in tasks]


def init_task_limit():
    # Default to all tasks
    if len(sys.argv) == 1:
        return len(tasks)

    end_index = int(sys.argv[1])

    # Check validity
    if not 0 < end_index <= len(tasks):
        raise AssertionError('Manual Configuration number of tasks to run is not valid')

    return end_index


def run_task(task_func, args):
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


def decide_with_fps(task_call_counts, start_time, end_time, task_names):
    # Calculate FPS of each task
    throughput_list = [call_count / (end_time - start_time)
                       for call_count in task_call_counts]

    # Debug
    print('Average Throughput over', FPS_CALC_REPEAT_TIME, 'seconds',
          list(zip(task_names, throughput_list)))


def main():
    # Variables for task state
    task_index = 0
    task_names = init_task_names()
    task_end_index = init_task_limit()

    # Variables for calculating throughput
    task_call_counts = init_fps_counts()
    start_time = time.time()

    # Init tasks args
    next_task_args = None

    # Keep running tasks in sequential order
    while True:

        # Determine which task to run
        task = tasks[task_index]

        # Run task
        to_continue, next_task_args = run_task(task_func=task, args=next_task_args)

        # Increment fps counter
        task_call_counts[task_index] += 1

        # Calculate fps
        end_time = time.time()
        if (end_time - start_time) > FPS_CALC_REPEAT_TIME:
            decide_with_fps(task_call_counts, start_time, end_time, task_names)

            # Reset vars for fps
            task_call_counts = init_fps_counts()
            start_time = time.time()

        # No need to continue running tasks, end of stream
        if to_continue is False and task_index == 0:
            break

        # Increment index (cyclical)
        task_index += 1

        # Reset to first frame if more function calls are not needed or reached end of sequence
        if to_continue is False or task_index >= task_end_index:
            task_index = 0
            next_task_args = None
            continue


if __name__ == '__main__':
    main()
