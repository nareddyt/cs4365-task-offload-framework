import time
import sys
import socket
import pickle
import struct

from taskified import tasks

# Show throughputs every given number of seconds
DEFAULT_THROUGHPUT_PERIOD = 3

# Peer server connection for offload tasking
# https://stackoverflow.com/questions/30988033/sending-live-video-frame-over-network-in-python-opencv
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect(('localhost', 8089))


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


def reconfigure_with_throughput(task_names, loop_count, start_time, end_time,
                                throughput_period, expected_throughput, task_end_index):
    # Calculate FPS of each task
    throughput = int(loop_count / (end_time - start_time))

    # Debug
    print('Average Throughput over', throughput_period, 'seconds:',
          throughput, 'iterations per second')

    # Don't re-adjust in manual mode
    if expected_throughput is None:
        return task_end_index

    # Check if re-adjustment needed
    if throughput >= expected_throughput:
        return task_end_index

    # Last task must be offloaded!
    offload_task_index = task_end_index - 1

    # Don't offload initial task
    if offload_task_index == 0:
        print('Cannot offload initial task!')
        return

    # Offload task
    print('Offloaded task', task_names[offload_task_index])
    return offload_task_index


def offload_to_peer(next_task_num, next_task_args):

    send_data = b''
    next_arg_data = []

    if next_task_args is not None:
        if type(next_task_args) is tuple:
            for arg in next_task_args:
                next_arg_data.append(arg)
        else:
            next_arg_data.append(next_task_args)

    # Send number of args
    send_data += struct.pack("L", len(next_arg_data))
    # Send the next task's number
    send_data += struct.pack("L", next_task_num)

    if len(next_arg_data) > 0:
        for next_arg in next_arg_data:
            data = pickle.dumps(next_arg)
            arg_size = struct.pack("L", len(data))
            send_data += arg_size
            send_data += data

    client_sock.sendall(send_data)

    # data = pickle.dumps(next_task_args)
    # # Send message length first
    # message_size = struct.pack("L", len(data))
    # send_data += message_size
    # send_data += data
    # client_sock.sendall(send_data)



def main():
    # Args parse
    task_end_index, expected_throughput = parse_args()
    print(task_end_index, expected_throughput)

    # Variables for task state
    task_index = 0
    task_names = init_task_names()

    # Variables for calculating throughput
    throughput_period = DEFAULT_THROUGHPUT_PERIOD
    loop_count = 0
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

        # Calculate fps
        end_time = time.time()
        if (end_time - start_time) > throughput_period:
            # Configuration with task throughputs if needed
            task_end_index = reconfigure_with_throughput(
                task_names=task_names,
                loop_count=loop_count,
                start_time=start_time,
                end_time=end_time,
                throughput_period=throughput_period,
                expected_throughput=expected_throughput,
                task_end_index=task_end_index
            )

            # Reset vars for throughput
            loop_count = 0
            start_time = time.time()

        # No need to continue running tasks, end of stream
        if to_continue is False and task_index == 0:
            break

        # Increment index (cyclical)
        task_index += 1

        # Reset to first frame if more function calls are not needed
        # or reached end of sequence
        if to_continue is False or task_index >= task_end_index:

            if to_continue is not False:
                # Send frame to peer server
                offload_to_peer(next_task_num=task_index, next_task_args=next_task_args)

            # Reset vars
            task_index = 0
            loop_count += 1
            next_task_args = None
            continue


if __name__ == '__main__':
    main()
