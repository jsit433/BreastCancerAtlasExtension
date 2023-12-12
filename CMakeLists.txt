cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(BreastCancerAtlasExtension)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/BreastCancerAtlasExtension")
set(EXTENSION_CATEGORY "Custom Module")
set(EXTENSION_CONTRIBUTORS "Poppy Buissink (University of Auckland), Josephine Situ (University of Auckland)")
set(EXTENSION_DESCRIPTION "This module contains an interactive 3D anatomical atlas and statistical analyses and aims to improve understanding of metastasis of breast cancer to lymph nodes ")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/BreastCancerAtlasExtension.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/BreastCancerAtlasExtension/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(BreastCancerAtlas)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
