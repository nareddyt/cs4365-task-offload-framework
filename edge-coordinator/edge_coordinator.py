import time
import sys

from taskified import tasks

# Show throughputs every given number of seconds
DEFAULT_THROUGHPUT_PERIOD = 3


# Helper functions
def init_fps_counts():
    return [0] * len(tasks)


def init_task_names():
    return [task.__name__ for task in tasks]


def parse_args():
    # Default to all tasks
    if len(sys.argv) == 1:
        return len(tasks), None

    # Parse manual configuration init
    end_index = int(sys.argv[1])

    # Check validity
    if not 0 < end_index <= len(tasks):
        raise AssertionError('Manual Configuration number of tasks to run is not valid')

    # Check for automatic configuration
    if len(sys.argv) == 2:
        return end_index, None

    # Automatic configuration enabled, parse expected throughput
    expected_throughput = int(sys.argv[2])

    # Check validity
    if expected_throughput <= 0:
        raise AssertionError('Automatic Configuration expected throughput is not valid')

    return end_index, expected_throughput


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


def reconfigure_with_throughput(task_call_counts, start_time, end_time,
                                task_names, throughput_period, expected_throughput):
    # Calculate FPS of each task
    throughput_list = [int(call_count / (end_time - start_time))
                       for call_count in task_call_counts]

    # Debug
    print('Average Throughput over', throughput_period, 'seconds',
          list(zip(task_names, throughput_list)))

    # Don't re-adjust in manual mode
    if expected_throughput is None:
        return

    pass


def main():

    # Args parse
    task_end_index, expected_throughput = parse_args()
    print(task_end_index, expected_throughput)

    # Variables for task state
    task_index = 0
    task_names = init_task_names()

    # Variables for calculating throughput
    throughput_period = DEFAULT_THROUGHPUT_PERIOD
    task_call_counts = init_fps_counts()
    start_time = time.time()

    # Init tasks args
    next_task_args = None

    # Keep running tasks in sequential order
    while True:

        # Determine which task to run
        task = tasks[task_index]

        # Run task
        to_continue, next_task_args = run_task(task_func=task,
                                               args=next_task_args)

        # Increment fps counter
        task_call_counts[task_index] += 1

        # Calculate fps
        end_time = time.time()
        if (end_time - start_time) > throughput_period:
            # Configuration with task throughputs if needed
            reconfigure_with_throughput(task_call_counts=task_call_counts,
                                        start_time=start_time,
                                        end_time=end_time,
                                        task_names=task_names,
                                        throughput_period=throughput_period,
                                        expected_throughput=expected_throughput)

            # Reset vars for throughput
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
