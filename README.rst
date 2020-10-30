PCR-GLOBWB with BMI
====================

This repository contains code of the global hydrologic model PCR-GLOBWB extended with Basic Model Interface (BMI) functionality, hereafter named PCR-BMI.
The code is developed and applied with GLOFRIM, a globally applicable computational framework for integrated hydrological–hydrodynamic modelling (https://glofrim.readthedocs.io/).

The default PCR-GLOBWB model *without* BMI functionality can be found here as Zenodo release (https://doi.org/10.5281/zenodo.595656).

Basic Model Interface (BMI)
-------------------------------

The Basic Model Interface (BMI) is a library specification to simplify the coupling of models.
The BMI is a non-invasive interface that allows for accessing model code via a defined set of function to simplify conversion of an existing model to a reusable, plug-and-play model component.

More info can be found here: https://csdms.colorado.edu/wiki/BMI_Description.

Important note
---------------

Maintanence and development of the code are independent of the original PCR-GLOBWB source code. It may thus be that certain features of the original version are not (yet) covered here.

For instance, the here provided code was only tested at 30 arcmin spatial resolution. Current efforts are untertaken to merge the different developments.

To use the package, it is required to have pcraster 4.1 or higher installed. The code and installation instructions can be found here: https://pcraster.geo.uu.nl/getting-started/.

For installation of PCR-BMI, it is possible to do this with

.. code-block:: console

    pip install git+https://github.com/UU-Hydro/PCR_BMI.git

or 

.. code-block:: console

    python path/to/PCR_BMI/setup.py develop

It is furthermore important to know that the DynRout extension, which is used in some of the test cases of GLOFRIM with PCR-GLOBWB, is not part of the code stored in this repository. 
If you want to receive the code of DynRout (which does not have a BMI, unfortunately), please contact the developers.

Usage
------

If you want to use the code, you are free to download, apply, and share it within the GNU GPL 3.0 license.

In case of application of this code or parts of it in any reports, please refer to the articles in the reference section as well as the Zenodo-release (version and DOI).

To make use of the BMI functions in PCR-GLOBWB, a typical workflow would look like this:

.. code-block:: python

    from pcrglobwb_bmi_v203 import pcrglobwb_bmi

    config_pcr = 'path/to/a/model/configurations/file.cfg'

    model_pcr = pcrglobwb_bmi.pcrglobwbBMI()

    # initiate PCR-GLOBWB
    model_pcr.initialize(config_pcr)

    # spin-up PCR-GLOBWB
    model_pcr.spinup()

    # update PCR-GLOBWB for 1 timestep (i.e. 1 day)
    model_pcr.update(1)

    # retrieve the values of a model variable as array
    Q = model_pcr.get_var('discharge')

    # overwrite values of a model variable
    model_pcr.set_var('discharge', Q)

Exposed variables
------------------

Note: Not all PCR-GLOBWB variables are exposed and can be retrieved/overwritten with BMI functions. 
Depending on modelling requirements, exposing additional variables may be needed.

Currently exposed variables are:

- discharge
- landSurfaceRunoff
- topWaterLayer
- channelStorage
- waterBodyStorage
- cellArea
- lddMap

Contributing
-------------

For inquiries, feedback, criticism, and research ideas please create an issue in this repository.

Contact
--------

Jannis Hoch PhD

email: j.m.hoch@uu.nl

References
-----------

- Hoch et al., 2017, https://doi.org/10.5194/gmd-10-3913-2017

- Hoch et al., 2019, https://doi.org/10.5194/nhess-19-1723-2019 



