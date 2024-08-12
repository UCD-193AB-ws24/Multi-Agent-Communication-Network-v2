# Senior Project Communication Network Module

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Readme Documentation](#readme-documentation)
- [Acknowledgements](#acknowledgements)

## Overview
This project used `Bluetooth low-energy` technology to deploy a `mesh network` in the field. It was developed with the `esp-idf` IoT framework on the ESP32-h2 chip from `Espressif`.

Our Capstone Senior Design client is a research team in the agricultural robots department that is researching `robot-assisted agricultural activity`. To address their need for a reliable local communication network in the field, we developed this project to use a Bluetooth mesh network to replace LoRa radio to achieve `higher bandwidth` while maintaining a `high range` to cover the entire field. 

The project aims to provide an `easily deployable local network` with a `network management server` and `network status dashboard`. With these components, we aim to address our clients' problems and make it easier for them to adapt to new changes. Additionally, the module is designed to be generalized, flexible, and adaptable for other uses and mediums.

Lastly, since ESP32 BLE Mesh is still a relatively new technology, there are few examples of it with the esp-idf framework. We aim to document the firmware code as a potential reference for others to advance their understanding and implementation of BLE Mesh with ESP32 chip and esp-idf.

## Project Structure `====`
Our whole project structure can be summarized as below:
![Screenshot 2024-06-23 210852](https://github.com/codecultivatorscrew/Multi-agent-Communication-Network/assets/54468493/ef895f72-a9a2-44a4-9a32-3ceffc56a1ea)

There are 3 main components consisted in this project:

 1. Network Managing Server (Runs in the central PC managing the network data and serves the APIs request)
 2. ESP32 Root Network Module
    - Root (Core and provisioner of the network, attached to PC)
    - Edge (Nodes in the network, attached to edge device)
 3. APIs in both root device (PC) and edge device (Rasberry Pi)

The BLE mesh network is established with the firmware we developed for the ESP32 `Root` and `Edge` network Modules. The modules will listen to and `execute network commands` from the UART channel and `propagate data` through the UART channel to the `application level`. The APIs we developed encapsulate the commonly used commands and UART signal process (elaborate in esp module documentation) for easy interaction at the application level with network modules. The `Network Managing Server` in the PC serves as another processing layer to monitor the network status, cache edge node data trace, and serve more complex logic to the root client software via socket communications  (elaborate in Server documentation).

The 3 components are designed to be loosely coupled to provide flexibility in selecting a physical edge device and choosing a software-level language/platform.
 - The network module (root/edge) communicates with applications via a widely supported UART protocol that is simple, reliable, and easy to integrate. The module also provides the options of 1) a USB-UART type-C port and 2) a defined RX-TX UART pins connection, minimizing the requirement on the application side as long as it can craft a UART signal in the desired format.
 - The Network Managing Server is not 'required' to use the network module as it just adds another layer to help reduce work on managing the network.
 - The software interacts with the Network Managing Server and can be written in any language as long as it can establish a socket connection to the Server.

## Logic Flow Chart


## Repo Folder Structure
This repo contains the Application level `network managing server` and `client-side APIs.` The folder structure is as follows:

- `/API`
  - `/Root-C-API` (containing root client-side API in c)
  - `/Root-Python-API` (containing root client-side API in Python, more up-to-date)

- `/Python-Server` (containing codes that run the middle layer network manager server and serve the APIs)

Note: detailed information is provided in the subfolder readme file.

## Getting Started

## Related Documentation
- [Python Server](https://github.com/codecultivatorscrew/Multi-agent-Communication-Network/blob/main/Python-Server)
- [Python APIs](https://github.com/codecultivatorscrew/Multi-agent-Communication-Network/blob/main/API/Root-Python-API)
- [ESP32 BLE Mesh Custom Root](https://github.com/codecultivatorscrew/esp_custom_root)
- [ESP32 BLE Mesh Custom Edge](https://github.com/codecultivatorscrew/esp_custom_edge)
- [Additional Components](./docs/additional-components.md)
- Testers

## Acknowledgements
Credits to contributors, libraries, and tools used.

