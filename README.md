# Breast Cancer Atlas Extension
This extension interactively visualises an anatomical and statistical lymph node atlas of the breast developed using SPECT/CT data. Development of the atlas has been published in *Cancer Imaging* and can be accessed at the following link: https://doi.org/10.1186/s40644-024-00738-z

If you utilise this 3D atlas in your own work, please ensure you cite the article as follows:

Situ, J., Buissink, P., Mu, A. et al. An interactive 3D atlas of sentinel lymph nodes in breast cancer developed using SPECT/CT. *Cancer Imaging* 24, 97 (2024).

![GUI_ss](https://github.com/jsit433/BreastCancerAtlasExtension/assets/80793526/33d0383b-2762-41a7-a089-06af7ab23619)

## Installation Instructions
* Download the folder 'BreastCancerAtlasExtension' by selecting the green 'Code' button > Download ZIP. Unzip the folder and then save this anywhere you like, but please save it somewhere you can access in a later step.
  ![image](https://github.com/jsit433/BreastCancerAtlasExtension/assets/80793526/809c4cd7-be36-4169-a1f9-a95cb085338b)
* Download and install 3D Slicer version 5.2.2 (https://download.slicer.org/?version=5.2.2).
* Start 3D Slicer.
* Under the module selection tab labelled ‘Welcome to Slicer’ select Developer Tools > Extension Wizard.
  ![image](https://github.com/jsit433/BreastCancerAtlasExtension/assets/80793526/c89af3ad-731e-4a80-bcab-c76c6e0d47a6)
* Click 'Select Extension'.
  ![image](https://github.com/jsit433/BreastCancerAtlasExtension/assets/80793526/bd81e73d-cae5-4ef8-8518-f4eb1391aa92)
* Locate the unzipped BreastCancerAtlasExtension-master folder from where you saved it earlier. Ensure the folder you select contains a 'BreastCancerAtlas' folder (you may have to double click twice on 'BreastCancerAtlasExtension-master'). Deselect ‘Enable developer mode’. If it asks you to install command line developer tools please do so.
  ![image](https://github.com/jsit433/BreastCancerAtlasExtension/assets/80793526/2297765c-37c9-45e8-90e0-c884bf122cab)
* After pressing 'Yes', close Slicer and then reopen it.
* The module should load when Slicer is reopened.
  ![image](https://github.com/jsit433/BreastCancerAtlasExtension/assets/80793526/1351fc3a-5cbb-4378-98ac-dd7c3f224835)
* If the information and options in the left control panel do not immediately appear, under the module selection tab labelled 'Welcome to Slicer' select Custom Modules > BreastCancerAtlas
  ![image](https://github.com/jsit433/BreastCancerAtlasExtension/assets/80793526/01931a8a-f858-4dc0-957d-49ea85c46227)
* You can read through the information and change visibility of different atlas components and the statistical analysis type as you prefer.
