# Senior Project Communication Network Module

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Readme Documentation](#readme-documentation)
- [Acknowledgements](#acknowledgements)

## Overview
This project used `Bluetooth low-energy` technology to deploy a `mesh network` in the field. It was developed with the `esp-idf` IoT framework on the ESP32-h2 chip from `Espressif`.

Our Capstone Senior Design client is a research team in the agricultural robots department that is researching robot-assisted agricultural activity. To address their need for a reliable local communication network in the field, we developed this project to use a Bluetooth mesh network to replace LoRa radio to achieve higher bandwidth while maintaining a high range to cover the entire field. 

The project aims to provide an easily deployable local network with a `network management server` and `network status dashboard`. With these components, we aim to address our clients' problems and make it easier for them to adapt to new changes. Additionally, the module is designed to be generalized, flexible, and adaptable for other uses and mediums.

Lastly, since ESP32 BLE Mesh is still a relatively new technology, there are few examples of it with the esp-idf framework. We aim to document the firmware code as a potential reference for others to advance their understanding and implementation of BLE Mesh with ESP32 chip and esp-idf.

## Project Structure
Our whole project structure can be summarized in this picture below (Description of each component below):
![Screenshot 2024-06-23 210852](https://github.com/codecultivatorscrew/Multi-agent-Communication-Network/assets/54468493/ef895f72-a9a2-44a4-9a32-3ceffc56a1ea)

As you can see from the picture, we have four main components:

 1. Python Server (inside Central Server)
 2. ESP32 Root (ESP32 Client)
 3. ESP32 Edge (ESP32 Server)
 4. Raspberry Pi

Below is a detailed description of each component:

`Note make this section breif and keep in high level. Detile will be on the sub folder read me-------------------------------------------`

### 1. Python Server
Our Python server serves contains abstracted network management logics and caches edge node data in the server for quicker access by the client. The existence of the python server allows edge node to constainly update the information whenever the data update is available, which makes disconnection detection easier to manage. It's also responsible for failsafe of the connectbility, so a failure within the network module doesn't crash client's entire program. Features that are included are as follows:
- Three different thread handling communication with the client and the root edge node asynchrounously.
- Python server can be interact through our client API with easy to use event notifier that follows observer pattern to react to incoming message.
- Communicate through client API through socket and root module through UART protocol.
- Support reconnection after socket disconnection.
- 
Description of what the Python Server does, its responsibilities, technologies used, etc. ***[Honghui or Yudi, please fill this. just a brief description]***

### 2. ESP32 Root
Our ESP32 Root, also called ESP32 Client served as our central network. [not sure if we want to mention if it's a custom PCB] It is responsible for managing and coordinating the edge devices and also ensuring efficient communication and data processing. The ESP32 Root is equipped with WiFi and Bluetooth, but we're focusing more on the BLE Mesh Features. Features that are included are as follows:
- Acts as a `main provisioner` for our mesh topology network
- Manage and handle communication between edge devices (data aggregation)
- Ability to do `Remote Provision` (provision nodes outside the range of the root)
- Can act as Non-Volatile or Volatile (Persistent or Non-Persistent Memory)
- [not sure how to explain but `opcode` and UART communication should be mentioned here]

### 3. ESP32 Edge
Our ESP32 Edge, also known as the ESP32 Server, serves as an edge node within the network. It is responsible for gathering data from its respective environment and handling tasks either independently or as directed by the Root. The ESP32 Edge is equipped with WiFi and Bluetooth, but we are focusing more on its BLE Mesh features. The features included are as follows:
- Send a heartbeat message to root every minute
- Store node information and external data, and send it to the Rasberry Pi
- Have the ability to handle everything without Raspberry Pi
- [Not sure what to put else]

### 4. Raspberry Pi
Description of the Raspberry Pi, its functions, tasks it performs, etc.

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

## Acknowledgements
Credits to contributors, libraries, and tools used.

