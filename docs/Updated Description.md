# GNSS and Precision Time War Room

## Introduction

GNSS (Global Navigation Satellite System) is a term used to describe any constellation of satellites that provides positioning, navigation, and timing services across the globe. The most well-known is GPS (Global Positioning System), but several others, including Galileo, GLONASS, and BeiDou, are also in operation. By making use of signals from at least four satellites, GNSS receivers can determine their position on Earth to within a few metres. GNSS satellites contain precise and accurate atomic clocks and broadcast time, which can be used by the receiver to determine the time to within a few nanoseconds.

However, the signals from GNSS satellites will not always be perfectly consistent, due to environmental interference from the atmosphere, relativistic effects, etc. By comparing the signal from GNSS with a local source of precise time, we can determine the Allan variance of the GNSS time and its stability. This can be useful for a variety of purposes, such as monitoring the quality and signal strength of GNSS signals.

## Problem Description

Although software already exists for viewing some data from GNSS receivers, they have a few issues, including only running for a short amount of time before running out of memory, not being optimised for the matrix of displays in the Cyber Lab, and normally requiring the receiver to be attached to the same device displaying the data. Additionally, they do not combine this with the data from a precise time source, to display the precision of the GNSS time.

This would be useful to have in the Cyber Lab in the Ashby Building, as it would provide a visual representation of GNSS data and quality information that could be used for research and teaching purposes, and be used as a display piece. As the Ashby building also has receivers for ADS-B (aircraft positioning) and AIS (ship positioning), it would also be useful to have a display of this data alongside the GNSS satellite data to provide a more complete picture of positioning and navigation data.

## Goals and requirements

The goal of this project is to create a system that can read in data from GNSS receivers, read another precise, accurate, time signal, compare the two and extract useful statistics from the data. All this information should then be shown to the user, taking advantage of the large matrix of displays in the Cyber Lab to maximise the display of information in a visually appealing way. The UI will be running on the Windows computer connected to the HDMI ports for the screens in the Cyber Lab.

It would be useful to to have a display of GNSS data and quality information:

- Monitoring the location of GNSS satellites currently in view
- Which network the satellites are part of (GPS, Galileo, etc.)
- Signal strength of each satellite (i.e. signal to noise ratio)
- Measured latitude, longitude, and altitude of the GNSS receiver
- Any other attributes that can be derived, e.g. nearest town/city, etc.
- Monitoring the quality of GNSS signals, useful to e.g. determine the best location for a GNSS receiver
- Comparing GNSS time with time derived from Precision Time Protocol (PTP) to determine the accuracy and precision of GNSS time
- Calculating Allan variance of GNSS time to determine its stability

As it may be desirable to display the data in a range of other locations, the system should additionally provide a web interface, allowing users to view the data in a browser. The system must be flexible to running in a range of environments, eg. all running on the same system, or split across multiple. The system should be as easy as possible to set up and run, and include instructions for doing so.

If time is available, the system should be extended to support receiving and displaying ADS-B for aircraft tracking, and AIS for ship tracking, as these are also useful for navigation and tracking purposes. It would also be useful to have a history of the data, to see if any degradation in signal quality has occurred over time.

### Requirements

- A window should display the location of satellites over a map of the earth
- In the map of the earth, the user should be able to move around the point being focused on
- In the map of the earth, the user should be able to zoom in and out
- The network each satellite is part of should be indicated by a unique colour, with a key showing which colour is which network
- Map should display ADS-B (Automatic Dependent Surveillance–Broadcast, for aircraft) data
- Map should display AIS (Automatic identification system, for marine vessels) data
- A window should display the elevation and azimuth and elevation of each satellite (e.g. on a polar grid)
- The system should allow for multiple windows of the same type, e.g. two maps focused on different points
- A window should display a bar chart of signal strength for each satellite
- A window should display raw GNSS NMEA messages
- A window should show statistics derived from GNSS messages (Latitude/longitude, time, altitude) along with information on the signal quality (dilution of precision, fix quality)
- A window should display a comparison between GNSS timing and the precise, accurate time source
- This window should display additional statistics derived from data (Allan variance, etc.)
- Each window should be resizable, and adapt to a reasonable range of sizes
- The application should allows multiple colour schemes to be selected from, e.g. a light theme to adapt to brighter environments
- Application can be instead run as a web interface, where the applicable windows are instead presented as options in a combobox
- A 3D globe should be available to provide an additional way to display the locations of satellites
- The system should be able to run for long periods of time without crashing or encountering other issues
- The system should be able to display data in real-time
- As the idea for the project was originally inspired by the movie WarGames (1983), the system should have a similar aesthetic to the "war room" in the movie (colour scheme, font, etc.)
- Application should be configurable through a configuration file in a human readable format, e.g. no need to change the code to change which windows appear on startup
- Chosen map projection should attempt to minimise distortion, rather than preserving Rhumb lines as straight lines (i.e. Mercator projection), or equal-area projections (i.e. Equal Earth projection)
- Data from both GNSS receiver and precise time source are published to an MQTT broker
- MQTT should have a secure configuration by default to prevent unauthorised access, as otherwise anybody could publish data to the broker
- System should be able to run on both Linux and Windows

## Technical Approach

Both the frontend for displaying data to the user, and the backend for reading in data from GNSS receivers and the Raspberry Pi, will be written in Python, as suitable libraries exist for both, and Python works well for rapid prototyping and development. To reduce the risk of errors and enforce a standard code quality, pylint will be used throughout the project. Changes will be tracked with git, and the project will be hosted on the EEECS GitLab.

The main frontend will be written using the PyQt6 library, as it provides a simple and flexible way to create GUIs in Python. To read in data from the GNSS receiver, the system will make use of the pyserial and pynmeagps libraries.

To support communication between the sources of data and any frontends, an MQTT broker will be used, as it provides a lightweight and easy-to-use way to send data between different systems. The paho-mqtt library will be used to both publish and subscribe to MQTT topics. The web interface will be created with Flask, as it is a very minimal and easy-to-use framework for creating web applications in Python.

To compare the GNSS time with the precise time from the Raspberry Pi, the system will likely need to make use of the 1 Pulse Per Second (1PPS) signal from the GNSS receiver, and compare it with the same signal from the Raspberry Pi using an oscilloscope. This will allow the system to accurately measure the difference between the two, which can then be used for later calculations.

## Risks

- As the system requires dealing with hardware which was not already on-hand at the beginning of the project, there is a risk of delays due to hardware taking longer than expected to arrive or set up. To mitigate this, the software side of the solution will be developed in parallel, meaning in the result of delays, the software can still be developed and tested.
- As the Ashby building may be closed over Christmas, it would not be possible to test with live data during this time. To mitigate this, a timestamped log of data will be created, which can be replayed to simulate live data, has been recorded.
- In the case where the GNSS receiver is damaged, either the prerecorded data, or the other other ArduSimple receiver that was ordered, may be used.
- Finding a suitable font for the UI may pose a challenge, as the font used in the original WarGames does not appear to be available anywhere.
- Finding the latitude and longitude of the satellites may be difficult, as the receiver instead provides an azimuth and elevation, relative to the view of the receiver.
- Any other delay that could not be anticipated, mitigated by leaving room for movement towards the end of the development period.

## Project Development Plan

See GANTT chart in `Updated development plan.pdf`

Changes from initial development plan:

- Had not planned for needing to select which GNSS receiver to use. However, as the software/GUI project was already planned to be conducted in parallel, this did not significantly effect the overall development of the project.
- Had not anticipated other university modules taking up as much time as they did, meaning I had to take a complete break from the project at the start of December. However, more work than anticipated was able to be completed over Christmas to make up for this.
- Original plan/problem description had not included MQTT. Adding it did not effect the overall development plan of the project.
- Original plan had not included web interface. Adding it did not effect the overall development plan of the project.
- PTP/Time analysis had to be moved to after initial demo as it was not able to be started early enough.
- Moved start date of dissertation to be the end of January rather than the middle of March, in case other modules require more time than expected again.

For the most part, the initial schedule has been followed, with adjustments only made where needed, and when new features were added to the plan.

## Initial UI Designs

![alt text](./UI%20Designs/image.png)

![alt text](./UI%20Designs/image-1.png)

![alt text](./UI%20Designs/image-2.png)

![alt text](./UI%20Designs/image-3.png)
