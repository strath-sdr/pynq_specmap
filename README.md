<img src="strathsdr_banner.png" width="100%">

# PYNQ Spectrum Mapping Tool
The repository is only compatible with [PYNQ images v2.7](https://github.com/Xilinx/PYNQ/releases).

## Introduction
This repository presents a spectrum mapping tool for PYNQ enabled devices. The user can interact with Python APIs for downloading, filtering, sorting, processing, and plotting the spectrum map on their Zynq development board. These APIs can be used to integrate the spectrum map into user applications.

<p align="center">
  <img src="./demonstration.gif" width="100%" height="100%" />
</p>
    
Currently, only the UK spectrum map provided by [OFCOM](http://static.ofcom.org.uk/static/spectrum/map.html) can be evaluated.

## Quick Start
Follow the instructions below to install the PYNQ spectrum mapping tool on your development board. **You will need to give your board access to the internet**.
* Power on your PYNQ development board with an SD Card containing a fresh PYNQ v2.7 image.
* Navigate to Jupyter Labs by opening a browser (preferably Chrome) and connecting to `http://<board_ip_address>:9090/lab`.
* We need to open a terminal in Jupyter Lab. Firstly, open a launcher window as shown in the figure below:

<p align="center">
  <img src="../master/open_jupyter_launcher.jpg" width="50%" height="50%" />
<p/>

* Now open a terminal in Jupyter as illustrated below:

<p align="center">
  <img src="../master/open_terminal_window.jpg" width="50%" height="50%" />
<p/>

* Now simply install the spectrum map package through PIP by executing the following command in the terminal:

```sh
pip3 install git+https://github.com/strath-sdr/pynq_spectrum_map
```

The Jupyter notebooks should now be available in the `spectrum-map` folder in your Jupyter Workspace.

## License
[BSD 3-Clause](/LICENSE)
