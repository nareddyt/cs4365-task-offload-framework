# Peer-to-Peer Task Offload Framework

[![standard-readme compliant](https://img.shields.io/badge/standard--readme-OK-green.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

> A framework for IoT devices to offload tasks to the cloud, resulting in efficient peer-to-peer computation.

## Table of Contents

- [Background](#background)
- [Code Structure](#code-structure)
- [Prerequisites](#prerequisites)
- [Install](#install)
- [Usage](#usage)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [License](#license)

## Background

Many IoT devices lack the compute resources to process and analyze data locally. This is not ideal, as most data collected by IoT devices is either noisy or requires computation to extract useful information. A common solution recommended by major cloud providers, such as AWS and GCP, is to send all raw data directly to the cloud. This allows data processing to be auto-scaled to the rate at which data is collected. Unfortunately, this leads to underutilization of the CPU onboard the IoT device. In large-scale deployments of hundreds of IoT devices, collectively making use of all CPU resources could reduce the cost of cloud processing by a large factor.

We implemented a framework that can efficiently use the maximal amount of compute resources on the IoT device while still maintaining a high throughput of data processing. Such a framework would allow data processing to be run directly on the IoT device, but would automatically offload data processing tasks to the cloud when throughput expectations are not met. By making maximal use of local compute resources on the IoT device, this framework reduces the cost of data processing on the cloud, while still allowing tasks to be offloaded to the cloud if greater throughput is required.

_See our CS 4365 [Final Report](https://docs.google.com/document/d/1Dh7aKAofPXTKovecV3e-9cyr0K4ERvkXMdTNScChcp8/edit?usp=sharing) for more details._

## Code Structure

Our framework is designed to work with any IoT application that follows the **Task Interface**.
Our final report contains more information on the design of the **Task Interface**.
`task_interface_example.py` provides a explanation of the **Task Interface** via example code.

For the performance evaluation and demo, we have provided 1 example IoT application in the `ball_tracking_example` folder.
`ball_tracking_example/sequential.py` contains the original IoT example application found in [a blog post](https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/) online.
`ball_tracking_example/taskified.py` contains the modified IoT application that adheres to the **Task Interface**.

`iot_client_coordinator.py` contains the framework code that runs on the IoT device. This is responsible for:

- Collecting data from the IoT sensors (_example: camera_)
- Running tasks on the IoT device
- Collecting metrics on IoT device load
- Offload tasks to the server when required (_The Automatic Scheduler_)

`cloud_server_coordinator.py` contains the framework code that runs on the cloud server. This is responsible for:

- Receiving tasks from the IoT device
- Running the remaining tasks on the server
- Reporting results of computation

## Prerequisites

This project was implemented using `Python 3.7`.
This project should still run on other minor versions of `Python 3`, but we provide no guarantees.

`pip` is required to install python dependencies.

### Optional Requirements

To realistically calculate metrics, the following are required:
- A IoT device with Python Support (Raspberry Pi Zero)
- Compute resources on a cloud provider with Python support (GCP Compute Engine)

**These are optional:** The IoT device and Cloud server can be run in two separate processes on a single development machine.

## Install

Run the following from the root folder:

```bash
pip install -r requirements.txt 
```

## Usage

This section describes multiple usage scenarios.

### IoT Client Only

For debug/demo purposes, we can run all tasks on the client only. 
All computation will happen locally, and the IoT client will never connect to the cloud server.
This run configuration does not represent the intended use-case.

```bash
python3 iot_client_coordinator.py
```

### IoT Client Offloading to Cloud Server

To support offloading tasks to the cloud, the server must be run on a static IP address in the cloud:

```bash
python3 cloud_server_coordinator.py
```

Please make note of the static IP address for the remaining run configurations.
When running the IoT Client (in a new terminal session), 
set the `HOST` environment variable to this static IP address. Examples:

```bash
export HOST='localhost'         # When running server locally for testing
export HOST='35.190.176.6'      # Realistic server in the cloud
```

_Note_: In this example, there are a total of 7 tasks.

_Note_:
The first task must always run on the IoT Client, as it collects sensor data from the IoT device.
The last task must always run on the Cloud Server, as it aggregates data across sensors.

#### IoT Manual Configuration Mode

_Manual Configuration Mode_ only runs a specific, pre-set number of tasks on the IoT Client.
The remainder of the tasks are run on the Cloud Server.

Pass in an argument with the number of tasks to run on the IoT client. Examples:

```bash
python3 iot_client_coordinator 1    # Run only the first task locally
python3 iot_client_coordinator 6    # Run all but the last task locally
python3 iot_client_coordinator 3    # Run the first 3 tasks locally
```

#### IoT Automatic Configuration Mode

_Automatic Configuration Mode_ starts off like _manual configuration mode_,
but automatically re-adjusts the number of tasks offloaded to the cloud server
in order to meet the expected throughput.

In addition to the argument for _manual configuration mode_,
the expected throughput must also be configured via the arguments.

```bash
python3 iot_client_coordinator 6 17     # Start running 6 tasks locally, but re-adjust to meet 17 FPS
python3 iot_client_coordinator 4 28     # Start running 4 tasks locally, but re-adjust to meet 28 FPS
```

## Maintainers

[@nareddyt](https://github.com/nareddyt)
[@rishiy15](https://github.com/rishiy15)

## Contributing

If editing the README, please conform to the [standard-readme](https://github.com/RichardLitt/standard-readme) specification.

## License

MIT © 2019 Tejasvi Nareddy
