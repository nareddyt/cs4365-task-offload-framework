# Define 4 tasks that run in sequence


def task1():
    """
    Initial task that gathers data, therefore does not need any other arguments.
    """

    # Gather data from IoT sensor
    pass

    # Return success and arg for next task
    return True, 'arg1'


def task2(arg1):
    """
    Second task that depends on the output of the first task.
    """

    # Do computation
    pass

    # Return success and multiple args for next task
    return True, ('arg1', 'arg2', 'arg3')


def task3(arg1, arg2, arg3):
    """
    Third task that depends on the output of the second task.
    Performs some basic filtering on the data.
    """

    # Do computation
    pass

    # Do filter
    if arg1 == arg2:
        # Return failure, next task will not be run
        return False

    # Otherwise return success, args for next task
    return True, 'arg4'


def task4(arg4):
    """
    Last task that depends on the output of the third task.
    Does not return any results, as this is the last task.
    """

    # Report results
    pass

    # End of tasks
    return False


# Export sequential ordering of tasks
tasks = [
    task1,
    task2,
    task3,
    task4
]
