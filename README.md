# Senior Project Communication Network Module

## Table of Contents
- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Readme Documentation](#readme-documentation)
- [Acknowledgements](#acknowledgements)

## Introduction
This project is based on our Capstone Senior Design. Our client is working on agricultural robots that use the LoRA network for communication. The problem with LoRA is that while it offers long-range connectivity, it has low bandwidth. Our client wants to increase the bandwidth while maintaining the high range. This project aims to solve that problem.

Our solution is a communication network module using BLE Mesh on the ESP32 Devkit Module. Our goal is to achieve a working BLE Mesh communication module with a Python server and network dashboard. With these components, we aim to address our client's problems and provide an easier way for them to adapt to new changes. Additionally, we aim to make our project adaptable for other uses and mediums, potentially as a reference for other contributors since ESP32 BLE Mesh is still a relatively new technology. Our project will help others advance their understanding and implementation of ESP32 BLE Mesh.

## Project Structure
Our whole project structure can be summarized in this picture below (Description of each component below):
![Screenshot 2024-06-23 210852](https://github.com/codecultivatorscrew/Multi-agent-Communication-Network/assets/54468493/ef895f72-a9a2-44a4-9a32-3ceffc56a1ea)

As you can see from the picture, we have four main components:

 1. Python Server (inside Central Server)
 2. ESP32 Root (ESP32 Client)
 3. ESP32 Edge (ESP32 Server)
 4. Raspberry Pi

Below is a detailed description of each component:

### 1. Python Server
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

## Getting Started
General setup and installation instructions.

## Readme Documentation
- [Python Server](./docs/python-server.md)
- [ESP Custom Root](https://github.com/codecultivatorscrew/esp_custom_root)
- [ESP32 BLE Mesh Edge Custom Model](https://github.com/codecultivatorscrew/esp_custom_edge)
- [Additional Components](./docs/additional-components.md)

## Acknowledgements
Credits to contributors, libraries, and tools used.

