# GNSS and Precision Time War Room

## Introduction

GNSS (Global Navigation Satellite System) is a term used to describe any constellation of satellites that provides positioning, navigation, and timing services across the globe. The most well-known is GPS (Global Positioning System), but several others, including Galileo, GLONASS, and BeiDou, are also in operation. By making use of signals from at least four satellites, GNSS receivers can determine their position on Earth to within a few metres. GNSS satellites contain precise and accurate atomic clocks and broadcast time, which can be used to determine the time to within a few nanoseconds.

However, the signals from GNSS will not always be perfectly consistent, due to environmental interference from the atmosphere, relativistic effects, etc. By comparing the signal from GNSS with a local source of precise time, we can determine the Allan variance of the GNSS time and its stability. This can be useful for a variety of purposes, such as monitoring the quality and signal strength of GNSS signals.

## Problem Description

Although software already exists for viewing some data from GNSS receivers, it has a few issues, including only running for a short amount of time before running out of memory, and not being optimised for the matrix of displays in the Cyber Lab.

It would be useful to to have a display of GNSS data and quality information, as this could be useful for a variety of purposes, such as:

- Monitoring the quality and signal strength of GNSS signals, e.g. to determine the best location for a GNSS receiver
- Comparing GNSS time with time derived from Precision Time Protocol (PTP) to determine the accuracy and precision of GNSS time
- Calculating the Allan variance of GNSS to determine the stability of GNSS time

This would be useful to have in the Cyber Lab in the Ashby Building, as it would provide a visual representation of GNSS data and quality information that could be used for research and teaching purposes. As the Ashby building also has receivers for ADS-B (aircraft positioning) and AIS (ship positioning), it would also be useful to have a display of this data alongside the GNSS satellite data to provide a more complete picture of positioning and navigation data.

## Goals and requirements

The goal of this project is to create a system that can read in data from GNSS receivers, read precise time on a Raspberry Pi, compare the two and extract useful statistics from the data. All this information should then be shown to the user, taking advantage of the large matrix of displays in the Cyber Lab to maximise the display of information in a visually appealing way. The UI will be running on the Windows computer connected to the HDMI ports for the screens in the Cyber Lab, and be built with Python and a suitable UI library.

To compare the GNSS time with the precise time from the Raspberry Pi, the system will likely need to make use of the 1 Pulse Per Second (1PPS) signal from the GNSS receiver, and compare it with the same signal from the Raspberry Pi using an oscilloscope. This will allow the system to accurately measure the difference between the two, which can then be used for later calculations.

If time is available, the system should be extended to support receiving and displaying ADS-B for aircraft tracking, and AIS for ship tracking, as these are also useful for navigation and tracking purposes.

## Success Criteria

- Read in data from GNSS receivers
- Read precise time on raspberry pi, making use of PTP
- Display GNSS data
- Display location of satellites, which network they are part of, etc
- Display comparison between GNSS timing and PTP
- Display additional statistics derived from data (Allan variance, etc.)
- Display ADS-B and AIS data

## Expected Project Development Plan

See attached GANTT chart
