# PCR-GLOBWB with BMI
This repository contains code of the global hydrologic model PCR-GLOBWB extended with Basic Model Interface (BMI) functionality.
The code is developed and applied with GLOFRIM, a globally applicable computational framework for integrated hydrological–hydrodynamic modelling (Hoch et al., 2017, https://www.geosci-model-dev.net/10/3913/2017/).

The repository containing GLOFRIM code can be found here:https://github.com/openearth/glofrim.

An online documentation is available here: https://glofrim.readthedocs.io/en/latest/.

## Basic Model Interface (BMI)
The Basic Model Interface (BMI) is a library specification to simplify the coupling of models.
The BMI is a non-invasive interface that allows for accessing model code via a defined set of function to simplify conversion of an existing model to a reusable, plug-and-play model component.

More info can be found here: https://csdms.colorado.edu/wiki/BMI_Description.

## Important note
Maintanence and development of the code are independent of the original PCR-GLOBWB source code. It may thus be that certain features of the original version are not (yet) covered here.

For instance, the here provided code was only tested at 30 arcmin spatial resolution
Current efforts are untertaken to merge the different developments.

To use the package, it is required to have pcraster 4.1 installed. The code and installation instructions can be found here: http://pcraster.geo.uu.nl/pcraster-4-1-0/.

For installation, it is possible to do this with `pip install -e path/to/PCR_BMI`.

## Usage
If you want to use the code, you are free to download and apply it within the GNU GPL 3.0 license.

In case of applicatoin in any reports, please refer to the above mentioned article as well as the release on Zenodo.

For inquiries, feedback, criticism, and research ideas please create an issue in this repository.


