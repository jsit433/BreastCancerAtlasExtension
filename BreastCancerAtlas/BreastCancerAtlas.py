import logging
import os

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin


#
# BreastCancerAtlas
#

class BreastCancerAtlas(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "BreastCancerAtlas"
        self.parent.categories = ["Custom Modules"]
        self.parent.dependencies = []
        self.parent.contributors = ["Poppy Buissink and Josephine Situ (University of Auckland)"]
        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", switchToModule)


#
# Register sample data sets in Sample Data module
#

def switchToModule():
    """
    Load scene for module and switch to this module
    """
    slicer.util.loadScene(os.path.join(os.path.dirname(__file__), 'Resources/Atlas/slicer_scene_for_module.mrb'))
    slicer.util.selectModule("BreastCancerAtlas")


#
# BreastCancerAtlasWidget
#

class BreastCancerAtlasWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.clearNode = "false"
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False
        self.tableNode = None
        self.pressed = ""
        self.clicked = ""

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # change layout to improve usability
        slicer.app.layoutManager().threeDWidget(0).threeDController().setVisible(True)
        slicer.app.layoutManager().threeDWidget(0).threeDController().setShowMaximizeViewButton(False)
        slicer.app.layoutManager().tableWidget(0).tableController().setVisible(False)
        slicer.util.setDataProbeVisible(False)
        slicer.util.setApplicationLogoVisible(False)
        slicer.util.setModuleHelpSectionVisible(False)
        slicer.util.setModulePanelTitleVisible(False)
        # Show 3D view layout
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
        # reset the 3D view so that the model is shown correctly
        slicer.app.layoutManager().threeDWidget(0).threeDView().rotateToViewAxis(3)
        slicer.app.layoutManager().threeDWidget(0).threeDView().resetFocalPoint()
        # change the background colour
        slicer.app.layoutManager().threeDWidget(0).mrmlViewNode().SetBackgroundColor(0.95, 0.95, 0.95)
        slicer.app.layoutManager().threeDWidget(0).mrmlViewNode().SetBackgroundColor2(0.75, 0.75, 0.75)

        # Load widget from .ui file (created by Qt Designer).
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/BreastCancerAtlas.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)


        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = BreastCancerAtlasLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
        self.ui.bayesianButton.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.bootstrappingButton.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.frequentistButton.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.numberLabelButton.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.nameLabelButton.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.noLabelButton.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.leftBreastCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.rightBreastCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.pectoralisMajorCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.pectoralisMinorCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.latissimusDorsiCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.repSLNOnlyCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.ESTROCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.greenSLNCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.muscleOpacitySlider.connect('valueChanged(double)', self.muscleOpacitySliderValueChanged)
        self.ui.L1CheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.L2CheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.L3CheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.L4CheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.IMNCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.IC4CheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.INTPECTCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.ESTROOpacitySlider.connect('valueChanged(double)', self.ESTROOpacitySliderValueChanged)
        self.ui.breastOpacitySlider.connect('valueChanged(double)', self.breastOpacitySliderValueChanged)
        self.ui.noSelectButton.connect('clicked(bool)', self.clearNodeSelection)
        self.ui.SLNFieldModelCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.SLNFieldVolOpacitySlider.connect('valueChanged(double)', self.SLNFieldVolumeOpacitySliderValueChanged)

        # getting markups for breast regions and setting observers
        # right breast
        Rb0Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode45')
        self.DisplayNodeRb0 = Rb0Node.GetDisplayNode()
        self.MarkupNodeRb0 = self.DisplayNodeRb0.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb0, self.DisplayNodeRb0.ActionEvent, self.Rb0pressed)

        Rb1Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode23')
        self.DisplayNodeRb1 = Rb1Node.GetDisplayNode()
        self.MarkupNodeRb1 = self.DisplayNodeRb1.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb1, self.DisplayNodeRb1.ActionEvent, self.Rb1pressed)

        Rb2Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode46')
        self.DisplayNodeRb2 = Rb2Node.GetDisplayNode()
        self.MarkupNodeRb2 = self.DisplayNodeRb2.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb2, self.DisplayNodeRb2.ActionEvent, self.Rb2pressed)

        Rb3Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode36')
        self.DisplayNodeRb3 = Rb3Node.GetDisplayNode()
        self.MarkupNodeRb3 = self.DisplayNodeRb3.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb3, self.DisplayNodeRb3.ActionEvent, self.Rb3pressed)

        Rb4Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode37')
        self.DisplayNodeRb4 = Rb4Node.GetDisplayNode()
        self.MarkupNodeRb4 = self.DisplayNodeRb4.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb4, self.DisplayNodeRb4.ActionEvent, self.Rb4pressed)

        Rb5Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode38')
        self.DisplayNodeRb5 = Rb5Node.GetDisplayNode()
        self.MarkupNodeRb5 = self.DisplayNodeRb5.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb5, self.DisplayNodeRb5.ActionEvent, self.Rb5pressed)

        Rb6Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode39')
        self.DisplayNodeRb6 = Rb6Node.GetDisplayNode()
        self.MarkupNodeRb6 = self.DisplayNodeRb6.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb6, self.DisplayNodeRb6.ActionEvent, self.Rb6pressed)

        Rb7Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode40')
        self.DisplayNodeRb7 = Rb7Node.GetDisplayNode()
        self.MarkupNodeRb7 = self.DisplayNodeRb7.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb7, self.DisplayNodeRb7.ActionEvent, self.Rb7pressed)

        Rb8Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode41')
        self.DisplayNodeRb8 = Rb8Node.GetDisplayNode()
        self.MarkupNodeRb8 = self.DisplayNodeRb8.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb8, self.DisplayNodeRb8.ActionEvent, self.Rb8pressed)

        Rb9Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode42')
        self.DisplayNodeRb9 = Rb9Node.GetDisplayNode()
        self.MarkupNodeRb9 = self.DisplayNodeRb9.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb9, self.DisplayNodeRb9.ActionEvent, self.Rb9pressed)

        Rb10Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode43')
        self.DisplayNodeRb10 = Rb10Node.GetDisplayNode()
        self.MarkupNodeRb10 = self.DisplayNodeRb10.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb10, self.DisplayNodeRb10.ActionEvent, self.Rb10pressed)

        Rb11Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode44')
        self.DisplayNodeRb11 = Rb11Node.GetDisplayNode()
        self.MarkupNodeRb11 = self.DisplayNodeRb11.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb11, self.DisplayNodeRb11.ActionEvent, self.Rb11pressed)

        Rb12Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode22')
        self.DisplayNodeRb12 = Rb12Node.GetDisplayNode()
        self.MarkupNodeRb12 = self.DisplayNodeRb12.GetMarkupsNode()
        self.addObserver(self.DisplayNodeRb12, self.DisplayNodeRb12.ActionEvent, self.Rb12pressed)

        # left breast
        Lb0Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode34')
        self.DisplayNodeLb0 = Lb0Node.GetDisplayNode()
        self.MarkupNodeLb0 = self.DisplayNodeLb0.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb0, self.DisplayNodeLb0.ActionEvent, self.Lb0pressed)

        Lb1Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode12')
        self.DisplayNodeLb1 = Lb1Node.GetDisplayNode()
        self.MarkupNodeLb1 = self.DisplayNodeLb1.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb1, self.DisplayNodeLb1.ActionEvent, self.Lb1pressed)

        Lb2Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode16')
        self.DisplayNodeLb2 = Lb2Node.GetDisplayNode()
        self.MarkupNodeLb2 = self.DisplayNodeLb2.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb2, self.DisplayNodeLb2.ActionEvent, self.Lb2pressed)

        Lb3Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode19')
        self.DisplayNodeLb3 = Lb3Node.GetDisplayNode()
        self.MarkupNodeLb3 = self.DisplayNodeLb3.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb3, self.DisplayNodeLb3.ActionEvent, self.Lb3pressed)

        Lb4Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode26')
        self.DisplayNodeLb4 = Lb4Node.GetDisplayNode()
        self.MarkupNodeLb4 = self.DisplayNodeLb4.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb4, self.DisplayNodeLb4.ActionEvent, self.Lb4pressed)

        Lb5Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode27')
        self.DisplayNodeLb5 = Lb5Node.GetDisplayNode()
        self.MarkupNodeLb5 = self.DisplayNodeLb5.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb5, self.DisplayNodeLb5.ActionEvent, self.Lb5pressed)

        Lb6Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode28')
        self.DisplayNodeLb6 = Lb6Node.GetDisplayNode()
        self.MarkupNodeLb6 = self.DisplayNodeLb6.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb6, self.DisplayNodeLb6.ActionEvent, self.Lb6pressed)

        Lb7Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode29')
        self.DisplayNodeLb7 = Lb7Node.GetDisplayNode()
        self.MarkupNodeLb7 = self.DisplayNodeLb7.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb7, self.DisplayNodeLb7.ActionEvent, self.Lb7pressed)

        Lb8Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode30')
        self.DisplayNodeLb8 = Lb8Node.GetDisplayNode()
        self.MarkupNodeLb8 = self.DisplayNodeLb8.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb8, self.DisplayNodeLb8.ActionEvent, self.Lb8pressed)

        Lb9Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode31')
        self.DisplayNodeLb9 = Lb9Node.GetDisplayNode()
        self.MarkupNodeLb9 = self.DisplayNodeLb9.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb9, self.DisplayNodeLb9.ActionEvent, self.Lb9pressed)

        Lb10Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode32')
        self.DisplayNodeLb10 = Lb10Node.GetDisplayNode()
        self.MarkupNodeLb10 = self.DisplayNodeLb10.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb10, self.DisplayNodeLb10.ActionEvent, self.Lb10pressed)

        Lb11Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode33')
        self.DisplayNodeLb11 = Lb11Node.GetDisplayNode()
        self.MarkupNodeLb11 = self.DisplayNodeLb11.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb11, self.DisplayNodeLb11.ActionEvent, self.Lb11pressed)

        Lb12Node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode7')
        self.DisplayNodeLb12 = Lb12Node.GetDisplayNode()
        self.MarkupNodeLb12 = self.DisplayNodeLb12.GetMarkupsNode()
        self.addObserver(self.DisplayNodeLb12, self.DisplayNodeLb12.ActionEvent, self.Lb12pressed)

        # getting markups for SLNs and setting observers

        lmedSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode24')
        self.DisplayNodelmedSLNs = lmedSLNsNode.GetDisplayNode()
        self.MarkupNodelmedSLNs = self.DisplayNodelmedSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNodelmedSLNs, self.DisplayNodelmedSLNs.ActionEvent, self.lmedSLNspressed)

        lINSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode48')
        self.DisplayNodelINSLNs = lINSLNsNode.GetDisplayNode()
        self.MarkupNodelINSLNs = self.DisplayNodelINSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNodelINSLNs, self.DisplayNodelINSLNs.ActionEvent, self.lINSLNspressed)

        rINSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode25')
        self.DisplayNoderINSLNs = rINSLNsNode.GetDisplayNode()
        self.MarkupNoderINSLNs = self.DisplayNoderINSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNoderINSLNs, self.DisplayNoderINSLNs.ActionEvent, self.rINSLNspressed)

        la2SLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode4')
        self.DisplayNodela2SLNs = la2SLNsNode.GetDisplayNode()
        self.MarkupNodela2SLNs = self.DisplayNodela2SLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNodela2SLNs, self.DisplayNodela2SLNs.ActionEvent, self.la2SLNspressed)

        ra2SLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode13')
        self.DisplayNodera2SLNs = ra2SLNsNode.GetDisplayNode()
        self.MarkupNodera2SLNs = self.DisplayNodera2SLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNodera2SLNs, self.DisplayNodera2SLNs.ActionEvent, self.ra2SLNspressed)

        laaSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode6')
        self.DisplayNodelaaSLNs = laaSLNsNode.GetDisplayNode()
        self.MarkupNodelaaSLNs = self.DisplayNodelaaSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNodelaaSLNs, self.DisplayNodelaaSLNs.ActionEvent, self.laaSLNspressed)

        raaSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode15')
        self.DisplayNoderaaSLNs = raaSLNsNode.GetDisplayNode()
        self.MarkupNoderaaSLNs = self.DisplayNoderaaSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNoderaaSLNs, self.DisplayNoderaaSLNs.ActionEvent, self.raaSLNspressed)

        lamSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode9')
        self.DisplayNodelamSLNs = lamSLNsNode.GetDisplayNode()
        self.MarkupNodelamSLNs = self.DisplayNodelamSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNodelamSLNs, self.DisplayNodelamSLNs.ActionEvent, self.lamSLNspressed)

        ramSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode17')
        self.DisplayNoderamSLNs = ramSLNsNode.GetDisplayNode()
        self.MarkupNoderamSLNs = self.DisplayNoderamSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNoderamSLNs, self.DisplayNoderamSLNs.ActionEvent, self.ramSLNspressed)

        lapSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode10')
        self.DisplayNodelapSLNs = lapSLNsNode.GetDisplayNode()
        self.MarkupNodelapSLNs = self.DisplayNodelapSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNodelapSLNs, self.DisplayNodelapSLNs.ActionEvent, self.lapSLNspressed)

        rapSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode18')
        self.DisplayNoderapSLNs = rapSLNsNode.GetDisplayNode()
        self.MarkupNoderapSLNs = self.DisplayNoderapSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNoderapSLNs, self.DisplayNoderapSLNs.ActionEvent, self.rapSLNspressed)

        lipSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode2')
        self.DisplayNodelipSLNs = lipSLNsNode.GetDisplayNode()
        self.MarkupNodelipSLNs = self.DisplayNodelipSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNodelipSLNs, self.DisplayNodelipSLNs.ActionEvent, self.lipSLNspressed)

        ripSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode3')
        self.DisplayNoderipSLNs = ripSLNsNode.GetDisplayNode()
        self.MarkupNoderipSLNs = self.DisplayNoderipSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNoderipSLNs, self.DisplayNoderipSLNs.ActionEvent, self.ripSLNspressed)

        licsSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode1')
        self.DisplayNodelicsSLNs = licsSLNsNode.GetDisplayNode()
        self.MarkupNodelicsSLNs = self.DisplayNodelicsSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNodelicsSLNs, self.DisplayNodelicsSLNs.ActionEvent, self.licsSLNspressed)

        ricsSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode21')
        self.DisplayNodericsSLNs = ricsSLNsNode.GetDisplayNode()
        self.MarkupNodericsSLNs = self.DisplayNodericsSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNodericsSLNs, self.DisplayNodericsSLNs.ActionEvent, self.ricsSLNspressed)

        lalSLNsNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode8')
        self.DisplayNodelalSLNs = lalSLNsNode.GetDisplayNode()
        self.MarkupNodelalSLNs = self.DisplayNodelalSLNs.GetMarkupsNode()
        self.addObserver(self.DisplayNodelalSLNs, self.DisplayNodelalSLNs.ActionEvent, self.lalSLNspressed)

        # getting markups for representative SLNs and setting observers (except ra3, la3 and rsc)
        la3RNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode5')
        self.DisplayNodela3R = la3RNode.GetDisplayNode()
        self.MarkupNodela3R = self.DisplayNodela3R.GetMarkupsNode()
        self.addObserver(self.DisplayNodela3R, self.DisplayNodela3R.ActionEvent, self.la3SLNspressed)

        ra3RNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode14')
        self.DisplayNodera3R = ra3RNode.GetDisplayNode()
        self.MarkupNodera3R = self.DisplayNodera3R.GetMarkupsNode()
        self.addObserver(self.DisplayNodera3R, self.DisplayNodera3R.ActionEvent, self.ra3SLNspressed)

        rscRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode20')
        self.DisplayNoderscR = rscRNode.GetDisplayNode()
        self.MarkupNoderscR = self.DisplayNoderscR.GetMarkupsNode()
        self.addObserver(self.DisplayNoderscR, self.DisplayNoderscR.ActionEvent, self.rscSLNspressed)

        lalRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode11')
        self.DisplayNodelalR = lalRNode.GetDisplayNode()
        self.MarkupNodelalR = self.DisplayNodelalR.GetMarkupsNode()
        self.addObserver(self.DisplayNodelalR, self.DisplayNodelalR.ActionEvent, self.lalSLNspressed)

        lamRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode35')
        self.DisplayNodelamR = lamRNode.GetDisplayNode()
        self.MarkupNodelamR = self.DisplayNodelamR.GetMarkupsNode()
        self.addObserver(self.DisplayNodelamR, self.DisplayNodelamR.ActionEvent, self.lamSLNspressed)

        lapRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode47')
        self.DisplayNodelapR = lapRNode.GetDisplayNode()
        self.MarkupNodelapR = self.DisplayNodelapR.GetMarkupsNode()
        self.addObserver(self.DisplayNodelapR, self.DisplayNodelapR.ActionEvent, self.lapSLNspressed)

        ramRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode49')
        self.DisplayNoderamR = ramRNode.GetDisplayNode()
        self.MarkupNoderamR = self.DisplayNoderamR.GetMarkupsNode()
        self.addObserver(self.DisplayNoderamR, self.DisplayNoderamR.ActionEvent, self.ramSLNspressed)

        rapRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode50')
        self.DisplayNoderapR = rapRNode.GetDisplayNode()
        self.MarkupNoderapR = self.DisplayNoderapR.GetMarkupsNode()
        self.addObserver(self.DisplayNoderapR, self.DisplayNoderapR.ActionEvent, self.rapSLNspressed)

        ricsRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode52')
        self.DisplayNodericsR = ricsRNode.GetDisplayNode()
        self.MarkupNodericsR = self.DisplayNodericsR.GetMarkupsNode()
        self.addObserver(self.DisplayNodericsR, self.DisplayNodericsR.ActionEvent, self.ricsSLNspressed)

        rINRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode53')
        self.DisplayNoderINR = rINRNode.GetDisplayNode()
        self.MarkupNoderINR = self.DisplayNoderINR.GetMarkupsNode()
        self.addObserver(self.DisplayNoderINR, self.DisplayNoderINR.ActionEvent, self.rINSLNspressed)

        lINRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode51')
        self.DisplayNodelINR = lINRNode.GetDisplayNode()
        self.MarkupNodelINR = self.DisplayNodelINR.GetMarkupsNode()
        self.addObserver(self.DisplayNodelINR, self.DisplayNodelINR.ActionEvent, self.lINSLNspressed)

        lmedRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode54')
        self.DisplayNodelmedR = lmedRNode.GetDisplayNode()
        self.MarkupNodelmedR = self.DisplayNodelmedR.GetMarkupsNode()
        self.addObserver(self.DisplayNodelmedR, self.DisplayNodelmedR.ActionEvent, self.lmedSLNspressed)

        rmedRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode67')
        self.DisplayNodermedR = rmedRNode.GetDisplayNode()
        self.MarkupNodermedR = self.DisplayNodermedR.GetMarkupsNode()
        self.addObserver(self.DisplayNodermedR, self.DisplayNodermedR.ActionEvent, self.rmedSLNspressed)

        ra2RNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode55')
        self.DisplayNodera2R = ra2RNode.GetDisplayNode()
        self.MarkupNodera2R = self.DisplayNodera2R.GetMarkupsNode()
        self.addObserver(self.DisplayNodera2R, self.DisplayNodera2R.ActionEvent, self.ra2SLNspressed)

        la2RNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode56')
        self.DisplayNodela2R = la2RNode.GetDisplayNode()
        self.MarkupNodela2R = self.DisplayNodela2R.GetMarkupsNode()
        self.addObserver(self.DisplayNodela2R, self.DisplayNodela2R.ActionEvent, self.la2SLNspressed)

        laaRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode57')
        self.DisplayNodelaaR = laaRNode.GetDisplayNode()
        self.MarkupNodelaaR = self.DisplayNodelaaR.GetMarkupsNode()
        self.addObserver(self.DisplayNodelaaR, self.DisplayNodelaaR.ActionEvent, self.laaSLNspressed)

        lipRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode58')
        self.DisplayNodelipR = lipRNode.GetDisplayNode()
        self.MarkupNodelipR = self.DisplayNodelipR.GetMarkupsNode()
        self.addObserver(self.DisplayNodelipR, self.DisplayNodelipR.ActionEvent, self.lipSLNspressed)

        raaRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode59')
        self.DisplayNoderaaR = raaRNode.GetDisplayNode()
        self.MarkupNoderaaR = self.DisplayNoderaaR.GetMarkupsNode()
        self.addObserver(self.DisplayNoderaaR, self.DisplayNoderaaR.ActionEvent, self.raaSLNspressed)

        ripRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode60')
        self.DisplayNoderipR = ripRNode.GetDisplayNode()
        self.MarkupNoderipR = self.DisplayNoderipR.GetMarkupsNode()
        self.addObserver(self.DisplayNoderipR, self.DisplayNoderipR.ActionEvent, self.ripSLNspressed)

        licsRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode61')
        self.DisplayNodelicsR = licsRNode.GetDisplayNode()
        self.MarkupNodelicsR = self.DisplayNodelicsR.GetMarkupsNode()
        self.addObserver(self.DisplayNodelicsR, self.DisplayNodelicsR.ActionEvent, self.licsSLNspressed)

        ralRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode63')
        self.DisplayNoderalR = ralRNode.GetDisplayNode()
        self.MarkupNoderalR = self.DisplayNoderalR.GetMarkupsNode()
        self.addObserver(self.DisplayNoderalR, self.DisplayNoderalR.ActionEvent, self.ralSLNspressed)

        lscRNode = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode64')
        self.DisplayNodelscR = lscRNode.GetDisplayNode()
        self.MarkupNodelscR = self.DisplayNodelscR.GetMarkupsNode()
        self.addObserver(self.DisplayNodelscR, self.DisplayNodelscR.ActionEvent, self.lscSLNspressed)

        # getting display nodes for the SLN field volumes
        la2Volume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode29')
        self.la2VolumeDisplayNode = la2Volume.GetDisplayNode()

        laaVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode33')
        self.laaVolumeDisplayNode = laaVolume.GetDisplayNode()

        lalVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode34')
        self.lalVolumeDisplayNode = lalVolume.GetDisplayNode()

        lamVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode35')
        self.lamVolumeDisplayNode = lamVolume.GetDisplayNode()

        lapVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode36')
        self.lapVolumeDisplayNode = lapVolume.GetDisplayNode()

        ra2Volume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode37')
        self.ra2VolumeDisplayNode = ra2Volume.GetDisplayNode()

        raaVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode38')
        self.raaVolumeDisplayNode = raaVolume.GetDisplayNode()

        ramVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode39')
        self.ramVolumeDisplayNode = ramVolume.GetDisplayNode()

        rapVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode40')
        self.rapVolumeDisplayNode = rapVolume.GetDisplayNode()

        ricsVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode41')
        self.ricsVolumeDisplayNode = ricsVolume.GetDisplayNode()

        medVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode42')
        self.medVolumeDisplayNode = medVolume.GetDisplayNode()

        RINVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode43')
        self.RINVolumeDisplayNode = RINVolume.GetDisplayNode()

        laipVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode44')
        self.laipVolumeDisplayNode = laipVolume.GetDisplayNode()

        raipVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode45')
        self.raipVolumeDisplayNode = raipVolume.GetDisplayNode()

        licsVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode46')
        self.licsVolumeDisplayNode = licsVolume.GetDisplayNode()

        LINVolume = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode47')
        self.LINVolumeDisplayNode = LINVolume.GetDisplayNode()

        # getting display nodes for muscles
        pecMajSegNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSegmentationNode6')
        self.pecMajSegDisplayNode = pecMajSegNode.GetDisplayNode()

        pecMinSegNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSegmentationNode3')
        self.pecMinSegDisplayNode = pecMinSegNode.GetDisplayNode()

        latDorSegNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSegmentationNode4')
        self.latDorSegDisplayNode = latDorSegNode.GetDisplayNode()

        # get the display nodes for ESTRO contours
        # RIGHT
        ESTRO_RIGHT_IMN_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode11')
        self.ESTRO_R_IMN_DisplayNode = ESTRO_RIGHT_IMN_Node.GetDisplayNode()

        ESTRO_RIGHT_IC4_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode12')
        self.ESTRO_R_IC4_DisplayNode = ESTRO_RIGHT_IC4_Node.GetDisplayNode()

        ESTRO_RIGHT_INTPECT_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode13')
        self.ESTRO_R_INTPECT_DisplayNode = ESTRO_RIGHT_INTPECT_Node.GetDisplayNode()

        ESTRO_RIGHT_L1_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode14')
        self.ESTRO_R_L1_DisplayNode = ESTRO_RIGHT_L1_Node.GetDisplayNode()

        ESTRO_RIGHT_L2_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode15')
        self.ESTRO_R_L2_DisplayNode = ESTRO_RIGHT_L2_Node.GetDisplayNode()

        ESTRO_RIGHT_L3_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode16')
        self.ESTRO_R_L3_DisplayNode = ESTRO_RIGHT_L3_Node.GetDisplayNode()

        ESTRO_RIGHT_L4_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode17')
        self.ESTRO_R_L4_DisplayNode = ESTRO_RIGHT_L4_Node.GetDisplayNode()

        # LEFT

        ESTRO_LEFT_IMN_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode4')
        self.ESTRO_L_IMN_DisplayNode = ESTRO_LEFT_IMN_Node.GetDisplayNode()

        ESTRO_LEFT_IC4_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode5')
        self.ESTRO_L_IC4_DisplayNode = ESTRO_LEFT_IC4_Node.GetDisplayNode()

        ESTRO_LEFT_INTPECT_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode6')
        self.ESTRO_L_INTPECT_DisplayNode = ESTRO_LEFT_INTPECT_Node.GetDisplayNode()

        ESTRO_LEFT_L1_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode7')
        self.ESTRO_L_L1_DisplayNode = ESTRO_LEFT_L1_Node.GetDisplayNode()

        ESTRO_LEFT_L2_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode8')
        self.ESTRO_L_L2_DisplayNode = ESTRO_LEFT_L2_Node.GetDisplayNode()

        ESTRO_LEFT_L3_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode9')
        self.ESTRO_L_L3_DisplayNode = ESTRO_LEFT_L3_Node.GetDisplayNode()

        ESTRO_LEFT_L4_Node = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode10')
        self.ESTRO_L_L4_DisplayNode = ESTRO_LEFT_L4_Node.GetDisplayNode()

        # get the display nodes for the breast regions
        RbreastSegNode = slicer.mrmlScene.GetNodeByID('vtkMRMLSegmentationNode5')
        self.RbreastSegDisplayNode = RbreastSegNode.GetDisplayNode()

        LbFatModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode18')
        self.LbFatDisplayNode = LbFatModelNode.GetDisplayNode()

        Lb0ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode19')
        self.Lb0DisplayNode = Lb0ModelNode.GetDisplayNode()

        Lb1ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode32')
        self.Lb1DisplayNode = Lb1ModelNode.GetDisplayNode()

        Lb2ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode30')
        self.Lb2DisplayNode = Lb2ModelNode.GetDisplayNode()

        Lb3ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode31')
        self.Lb3DisplayNode = Lb3ModelNode.GetDisplayNode()

        Lb4ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode28')
        self.Lb4DisplayNode = Lb4ModelNode.GetDisplayNode()

        Lb5ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode27')
        self.Lb5DisplayNode = Lb5ModelNode.GetDisplayNode()

        Lb6ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode26')
        self.Lb6DisplayNode = Lb6ModelNode.GetDisplayNode()

        Lb7ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode25')
        self.Lb7DisplayNode = Lb7ModelNode.GetDisplayNode()

        Lb8ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode24')
        self.Lb8DisplayNode = Lb8ModelNode.GetDisplayNode()

        Lb9ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode23')
        self.Lb9DisplayNode = Lb9ModelNode.GetDisplayNode()

        Lb10ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode22')
        self.Lb10DisplayNode = Lb10ModelNode.GetDisplayNode()

        Lb11ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode21')
        self.Lb11DisplayNode = Lb11ModelNode.GetDisplayNode()

        Lb12ModelNode = slicer.mrmlScene.GetNodeByID('vtkMRMLModelNode20')
        self.Lb12DisplayNode = Lb12ModelNode.GetDisplayNode()

        # initialise the parameter node when the module is reloaded
        if self.parent.isEntered:
            self.initializeParameterNode()

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def muscleOpacitySliderValueChanged(self, newValue):
        """
        Change the muscle segment opacity when the user interacts with the slider
        """
        self.latDorSegDisplayNode.SetOpacity(newValue)
        self.pecMinSegDisplayNode.SetOpacity(newValue)
        self.pecMajSegDisplayNode.SetOpacity(newValue)

    def ESTROOpacitySliderValueChanged(self, newValue):
        """
        Change the ESTRO segment opacity when the user interacts with the slider
        """
        self.ESTRO_L_IMN_DisplayNode.SetOpacity(newValue)
        self.ESTRO_L_IC4_DisplayNode.SetOpacity(newValue)
        self.ESTRO_L_INTPECT_DisplayNode.SetOpacity(newValue)
        self.ESTRO_L_L1_DisplayNode.SetOpacity(newValue)
        self.ESTRO_L_L2_DisplayNode.SetOpacity(newValue)
        self.ESTRO_L_L3_DisplayNode.SetOpacity(newValue)
        self.ESTRO_L_L4_DisplayNode.SetOpacity(newValue)
        self.ESTRO_R_IMN_DisplayNode.SetOpacity(newValue)
        self.ESTRO_R_IC4_DisplayNode.SetOpacity(newValue)
        self.ESTRO_R_INTPECT_DisplayNode.SetOpacity(newValue)
        self.ESTRO_R_L1_DisplayNode.SetOpacity(newValue)
        self.ESTRO_R_L2_DisplayNode.SetOpacity(newValue)
        self.ESTRO_R_L3_DisplayNode.SetOpacity(newValue)
        self.ESTRO_R_L4_DisplayNode.SetOpacity(newValue)

    def breastOpacitySliderValueChanged(self, newValue):
        """
        Change the breast segment opacity when the user interacts with the slider
        """
        self.RbreastSegDisplayNode.SetOpacity(newValue)
        self.Lb0DisplayNode.SetOpacity(newValue)
        self.Lb1DisplayNode.SetOpacity(newValue)
        self.Lb2DisplayNode.SetOpacity(newValue)
        self.Lb3DisplayNode.SetOpacity(newValue)
        self.Lb4DisplayNode.SetOpacity(newValue)
        self.Lb5DisplayNode.SetOpacity(newValue)
        self.Lb6DisplayNode.SetOpacity(newValue)
        self.Lb7DisplayNode.SetOpacity(newValue)
        self.Lb8DisplayNode.SetOpacity(newValue)
        self.Lb9DisplayNode.SetOpacity(newValue)
        self.Lb10DisplayNode.SetOpacity(newValue)
        self.Lb11DisplayNode.SetOpacity(newValue)
        self.Lb12DisplayNode.SetOpacity(newValue)
        self.LbFatDisplayNode.SetOpacity(newValue)

    def SLNFieldVolumeOpacitySliderValueChanged(self, newValue):
        """
        Change the SLN field volumes opacity when the user interacts with the slider
        """
        # in 3D view
        self.la2VolumeDisplayNode.SetOpacity(newValue)
        self.laaVolumeDisplayNode.SetOpacity(newValue)
        self.lalVolumeDisplayNode.SetOpacity(newValue)
        self.lamVolumeDisplayNode.SetOpacity(newValue)
        self.lapVolumeDisplayNode.SetOpacity(newValue)
        self.ra2VolumeDisplayNode.SetOpacity(newValue)
        self.raaVolumeDisplayNode.SetOpacity(newValue)
        self.ramVolumeDisplayNode.SetOpacity(newValue)
        self.rapVolumeDisplayNode.SetOpacity(newValue)
        self.ricsVolumeDisplayNode.SetOpacity(newValue)
        self.medVolumeDisplayNode.SetOpacity(newValue)
        self.RINVolumeDisplayNode.SetOpacity(newValue)
        self.laipVolumeDisplayNode.SetOpacity(newValue)
        self.raipVolumeDisplayNode.SetOpacity(newValue)
        self.licsVolumeDisplayNode.SetOpacity(newValue)
        self.LINVolumeDisplayNode.SetOpacity(newValue)
        # in slice view
        self.la2VolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.laaVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.lalVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.lamVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.lapVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.ra2VolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.raaVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.ramVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.rapVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.ricsVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.medVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.RINVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.laipVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.raipVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.licsVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)
        self.LINVolumeDisplayNode.SetSliceIntersectionOpacity(newValue)

    def Rb0pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # change the layout to show table
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode14')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode14')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode114')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode114')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode64')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode64')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change label colour and names
            self.pressed = 'Rb0'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_4", 1, 0, 0)

    def Rb1pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode15')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode15')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode115')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode115')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode65')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode65')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change label colours and values
            self.pressed = 'Rb1'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_6", 1, 0, 0)

    def Rb2pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode16')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode16')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode116')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode116')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode66')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode66')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Rb2'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_7", 1, 0, 0)

    def Rb3pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode17')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode17')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode117')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode117')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode67')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode67')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Rb3'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_8", 1, 0, 0)

    def Rb4pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode18')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode18')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode118')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode118')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode68')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode68')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Rb4'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_9", 1, 0, 0)

    def Rb5pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode19')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode19')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode119')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode119')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode69')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode69')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Rb5'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_10", 1, 0, 0)

    def Rb6pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode20')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode20')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode120')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode120')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode70')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode70')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Rb6'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_11", 1, 0, 0)

    def Rb7pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode21')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode21')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode121')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode121')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode71')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode71')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Rb7'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_12", 1, 0, 0)

    def Rb8pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode22')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode22')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode122')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode122')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode72')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode72')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Rb8'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_13", 1, 0, 0)

    def Rb9pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode23')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode23')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode123')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode123')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode73')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode73')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Rb9'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_14", 1, 0, 0)

    def Rb10pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode24')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode24')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode124')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode124')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode74')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode74')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Rb10'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_15", 1, 0, 0)

    def Rb11pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode25')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode25')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode125')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode125')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode75')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode75')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Rb11'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_17", 1, 0, 0)

    def Rb12pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode26')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode26')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode126')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode126')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode76')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode76')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Rb12'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_5", 1, 0, 0)

    def Lb0pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode1')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode1')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode101')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode101')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode51')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode51')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb0'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb0DisplayNode.SetColor(1, 0, 0)

    def Lb1pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode2')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode2')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode102')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode102')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode52')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode52')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb1'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb1DisplayNode.SetColor(1, 0, 0)
    def Lb2pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode3')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode3')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode103')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode103')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode53')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode53')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb2'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb2DisplayNode.SetColor(1, 0, 0)

    def Lb3pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode4')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode4')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode104')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode104')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode54')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode54')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb3'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb3DisplayNode.SetColor(1, 0, 0)

    def Lb4pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode5')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode5')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode105')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode105')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode55')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode55')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb4'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb4DisplayNode.SetColor(1, 0, 0)

    def Lb5pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode6')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode6')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode106')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode106')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode56')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode56')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb5'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb5DisplayNode.SetColor(1, 0, 0)

    def Lb6pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode7')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode7')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode107')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode107')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode57')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode57')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb6'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb6DisplayNode.SetColor(1, 0, 0)

    def Lb7pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode8')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode8')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode108')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode108')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode58')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode58')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb7'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb7DisplayNode.SetColor(1, 0, 0)

    def Lb8pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode9')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode9')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode109')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode109')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode59')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode59')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb8'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb8DisplayNode.SetColor(1, 0, 0)

    def Lb9pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode10')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode10')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode110')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode110')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode60')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode60')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb9'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb9DisplayNode.SetColor(1, 0, 0)

    def Lb10pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode11')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode11')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode111')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode111')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode61')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode61')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb10'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb10DisplayNode.SetColor(1, 0, 0)

    def Lb11pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode12')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode12')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode112')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode112')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode62')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode62')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb11'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb11DisplayNode.SetColor(1, 0, 0)

    def Lb12pressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode13')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode13')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode113')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode113')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode63')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode63')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'Lb12'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left breast'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.Lb12DisplayNode.SetColor(1, 0, 0)

    def rmedSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode49')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode49')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode149')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode149')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode99')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode99')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'rmed'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodermedR.SetSelectedColor(1, 0, 0)

    def lmedSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # show the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode37')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode37')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode137')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode137')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode87')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode87')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            self.pressed = 'lmed'
            # change the label colours and values
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodelmedR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelmedSLNs.SetSelectedColor(1, 0, 0)

    def lINSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # show the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode35')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode35')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode135')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode135')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode85')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode85')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'lIN'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodelINR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelINSLNs.SetSelectedColor(1, 0, 0)

    def rINSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # show the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode47')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode47')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode147')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode147')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode97')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode97')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'rIN'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNoderINR.SetSelectedColor(1, 0, 0)
            self.DisplayNoderINSLNs.SetSelectedColor(1, 0, 0)

    def la2SLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode27')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode27')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode127')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode127')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode77')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode77')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'la2'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodela2R.SetSelectedColor(1, 0, 0)
            self.DisplayNodela2SLNs.SetSelectedColor(1, 0, 0)

    def la3SLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode28')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode28')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode128')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode128')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode78')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode78')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'la3'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodela3R.SetSelectedColor(1, 0, 0)

    def laaSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode29')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode29')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode129')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode129')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode79')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode79')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'laa'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodelaaR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelaaSLNs.SetSelectedColor(1, 0, 0)

    def lalSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode30')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode30')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode130')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode130')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode80')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode80')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'lal'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodelalR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelalSLNs.SetSelectedColor(1, 0, 0)

    def lamSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode31')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode31')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode131')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode131')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode81')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode81')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'lam'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodelamR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelamSLNs.SetSelectedColor(1, 0, 0)

    def lapSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode32')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode32')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode132')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode132')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode82')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode82')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'lap'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodelapR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelapSLNs.SetSelectedColor(1, 0, 0)

    def licsSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode34')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode34')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode134')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode134')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode84')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode84')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label values and colours
            self.pressed = 'lics'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodelicsR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelicsSLNs.SetSelectedColor(1, 0, 0)

    def lipSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode36')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode36')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode136')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode136')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode86')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode86')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'lip'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodelipR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelipSLNs.SetSelectedColor(1, 0, 0)

    def ra2SLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode39')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode39')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode139')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode139')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode89')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode89')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'ra2'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodera2R.SetSelectedColor(1, 0, 0)
            self.DisplayNodera2SLNs.SetSelectedColor(1, 0, 0)

    def ra3SLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode40')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode40')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode140')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode140')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode90')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode90')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'ra3'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodera3R.SetSelectedColor(1, 0, 0)

    def raaSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode41')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode41')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode141')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode141')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode91')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode91')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'raa'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNoderaaR.SetSelectedColor(1, 0, 0)
            self.DisplayNoderaaSLNs.SetSelectedColor(1, 0, 0)

    def ramSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode43')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode43')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode143')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode143')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode93')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode93')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'ram'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNoderamR.SetSelectedColor(1, 0, 0)
            self.DisplayNoderamSLNs.SetSelectedColor(1, 0, 0)

    def rapSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode44')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode44')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode144')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode144')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode94')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode94')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'rap'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNoderapR.SetSelectedColor(1, 0, 0)
            self.DisplayNoderapSLNs.SetSelectedColor(1, 0, 0)

    def ripSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode48')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode48')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode148')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode148')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode98')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode98')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'rip'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNoderipR.SetSelectedColor(1, 0, 0)
            self.DisplayNoderipSLNs.SetSelectedColor(1, 0, 0)

    def rscSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode50')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode50')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode150')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode150')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode100')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode100')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'rsc'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNoderscR.SetSelectedColor(1, 0, 0)

    def ricsSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode46')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode46')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode146')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode146')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode96')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode96')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'rics'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodericsR.SetSelectedColor(1, 0, 0)
            self.DisplayNodericsSLNs.SetSelectedColor(1, 0, 0)

    def ralSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode42')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode42')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode142')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode142')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode92')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode92')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'ral'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'right SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNoderalR.SetSelectedColor(1, 0, 0)

    def lscSLNspressed(self, caller, event):
        """
        Called when the user interacts with this markup and acts to display the relevant table
        """
        # don't do anything if ESTRO contours are showing
        if self._parameterNode.GetParameter("ESTROVis") == 'false':
            # show the table view
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayout3DTableView)
            # find the relevant table
            if self._parameterNode.GetParameter("bayesianVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode38')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode38')
            elif self._parameterNode.GetParameter("frequentistVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode138')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode138')
            elif self._parameterNode.GetParameter("bootstrappingVis") == 'true':
                slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID('vtkMRMLTableNode88')
                self.tableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLTableNode88')
            # show table
            slicer.app.applicationLogic().PropagateTableSelection()
            # change the label colours and values
            self.pressed = 'lsc'
            if self._parameterNode.GetParameter("numberLabelVis") == "true":
                self.clicked = 'left SLN'
                self.MakeCPLabelNumbers()
            self.SetColoursBack()
            self.DisplayNodelscR.SetSelectedColor(1, 0, 0)

    def KeepPressedRed(self):
        """
        Set the SLN or breast region which was most recently pressed back to red
        """
        if self.pressed == 'Rb0':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_4", 1, 0, 0)
        if self.pressed == 'Rb1':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_6", 1, 0, 0)
        if self.pressed == 'Rb2':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_7", 1, 0, 0)
        if self.pressed == 'Rb3':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_8", 1, 0, 0)
        if self.pressed == 'Rb4':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_9", 1, 0, 0)
        if self.pressed == 'Rb5':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_10", 1, 0, 0)
        if self.pressed == 'Rb6':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_11", 1, 0, 0)
        if self.pressed == 'Rb7':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_12", 1, 0, 0)
        if self.pressed == 'Rb8':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_13", 1, 0, 0)
        if self.pressed == 'Rb9':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_14", 1, 0, 0)
        if self.pressed == 'Rb10':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_15", 1, 0, 0)
        if self.pressed == 'Rb11':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_17", 1, 0, 0)
        if self.pressed == 'Rb12':
            self.RbreastSegDisplayNode.SetSegmentOverrideColor("Segment_5", 1, 0, 0)
        if self.pressed == 'Lb0':
            self.Lb0DisplayNode.SetColor(1, 0, 0)
        if self.pressed == 'Lb1':
            self.Lb1DisplayNode.SetColor(1, 0, 0)
        if self.pressed == 'Lb2':
            self.Lb2DisplayNode.SetColor(1, 0, 0)
        if self.pressed == 'Lb3':
            self.Lb3DisplayNode.SetColor(1, 0, 0)
        if self.pressed == 'Lb4':
            self.Lb4DisplayNode.SetColor(1, 0, 0)
        if self.pressed == 'Lb5':
            self.Lb5DisplayNode.SetColor(1, 0, 0)
        if self.pressed == 'Lb6':
            self.Lb6DisplayNode.SetColor(1, 0, 0)
        if self.pressed == 'Lb7':
            self.Lb7DisplayNode.SetColor(1, 0, 0)
        if self.pressed == 'Lb8':
            self.Lb8DisplayNode.SetColor(1, 0, 0)
        if self.pressed == 'Lb9':
            self.Lb9DisplayNode.SetColor(1, 0, 0)
        if self.pressed == 'Lb10':
            self.Lb10DisplayNode.SetColor(1, 0, 0)
        if self.pressed == 'Lb11':
            self.Lb11DisplayNode.SetColor(1, 0, 0)
        if self.pressed == 'Lb12':
            self.Lb12DisplayNode.SetColor(1, 0, 0)
        # SLNs
        if self.pressed == 'lmed':
            self.DisplayNodelmedR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelmedSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'lIN':
            self.DisplayNodelINR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelINSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'rmed':
            self.DisplayNodermedR.SetSelectedColor(1, 0, 0)
        if self.pressed == 'rIN':
            self.DisplayNoderINR.SetSelectedColor(1, 0, 0)
            self.DisplayNoderINSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'la2':
            self.DisplayNodela2R.SetSelectedColor(1, 0, 0)
            self.DisplayNodela2SLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'ra2':
            self.DisplayNodera2R.SetSelectedColor(1, 0, 0)
            self.DisplayNodera2SLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'la3':
            self.DisplayNodela3R.SetSelectedColor(1, 0, 0)
        if self.pressed == 'ra3':
            self.DisplayNodera3R.SetSelectedColor(1, 0, 0)
        if self.pressed == 'laa':
            self.DisplayNodelaaR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelaaSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'raa':
            self.DisplayNoderaaR.SetSelectedColor(1, 0, 0)
            self.DisplayNoderaaSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'lal':
            self.DisplayNodelalR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelalSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'lap':
            self.DisplayNodelapR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelapSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'rap':
            self.DisplayNoderapR.SetSelectedColor(1, 0, 0)
            self.DisplayNoderapSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'lam':
            self.DisplayNodelamR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelamSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'ram':
            self.DisplayNoderamR.SetSelectedColor(1, 0, 0)
            self.DisplayNoderamSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'lics':
            self.DisplayNodelicsR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelicsSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'rics':
            self.DisplayNodericsR.SetSelectedColor(1, 0, 0)
            self.DisplayNodericsSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'lip':
            self.DisplayNodelipR.SetSelectedColor(1, 0, 0)
            self.DisplayNodelipSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'rip':
            self.DisplayNoderipR.SetSelectedColor(1, 0, 0)
            self.DisplayNoderipSLNs.SetSelectedColor(1, 0, 0)
        if self.pressed == 'rsc':
            self.DisplayNoderscR.SetSelectedColor(1, 0, 0)
        if self.pressed == 'lsc':
            self.DisplayNodelscR.SetSelectedColor(1, 0, 0)
        if self.pressed == 'ral':
            self.DisplayNoderalR.SetSelectedColor(1, 0, 0)

    def MakeCPLabelNumbers(self):
        """
        Change the control point label to the relevant statistic
        """
        # set the rest to names
        self.MakeCPLabelNames()

        # change the left SLN numbers if a left breast region was clicked
        num_rows = self.tableNode.GetNumberOfRows()
        if self.clicked == "left breast":
            # change the left SLN numbers
            for i in range(num_rows):
                if self.tableNode.GetCellText(i, 0) == "MED: Mediastinal":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodelmedR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "IN: Interval":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodelINR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "A2: Axilla Level II":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodela2R.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "A3: Axilla Level III":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodela3R.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "AA: Axilla Level I (anterior)":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodelaaR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "AM: Axilla Level I (medial)":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodelamR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "AP: Axilla Level I (posterior)":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodelapR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "AIP: Axilla Level I (interpectoral)":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodelipR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "IM: Internal Mammary":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodelicsR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "AL: Axilla Level I (lateral)":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodelalR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "SC: Supraclavicular":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodelscR.SetNthControlPointLabel(0, (label[0]+'%'))
            # make the right SLN labels hidden
            self.MarkupNodermedR.SetNthControlPointLabel(0, '')
            self.MarkupNoderscR.SetNthControlPointLabel(0, '')
            self.MarkupNoderalR.SetNthControlPointLabel(0, '')
            self.MarkupNodericsR.SetNthControlPointLabel(0, '')
            self.MarkupNoderipR.SetNthControlPointLabel(0, '')
            self.MarkupNoderapR.SetNthControlPointLabel(0, '')
            self.MarkupNoderamR.SetNthControlPointLabel(0, '')
            self.MarkupNoderaaR.SetNthControlPointLabel(0, '')
            self.MarkupNodera3R.SetNthControlPointLabel(0, '')
            self.MarkupNodera2R.SetNthControlPointLabel(0, '')
            self.MarkupNoderINR.SetNthControlPointLabel(0, '')

        # change the right SLN numbers if a right breast region was clicked
        if self.clicked == 'right breast':
            # change the right SLN numbers
            for i in range(num_rows):
                if self.tableNode.GetCellText(i, 0) == "MED: Mediastinal":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodermedR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "IN: Interval":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNoderINR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "A2: Axilla Level II":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodera2R.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "A3: Axilla Level III":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodera3R.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "AA: Axilla Level I (anterior)":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNoderaaR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "AM: Axilla Level I (medial)":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNoderamR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "AP: Axilla Level I (posterior)":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNoderapR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "AIP: Axilla Level I (interpectoral)":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNoderipR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "IM: Internal Mammary":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodericsR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "SC: Supraclavicular":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNoderscR.SetNthControlPointLabel(0, (label[0]+'%'))
                if self.tableNode.GetCellText(i, 0) == "AL: Axilla Level I (lateral)":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNoderalR.SetNthControlPointLabel(0, (label[0]+'%'))
            # make the left SLN labels hidden
            self.MarkupNodelmedR.SetNthControlPointLabel(0, '')
            self.MarkupNodelINR.SetNthControlPointLabel(0, '')
            self.MarkupNodela2R.SetNthControlPointLabel(0, '')
            self.MarkupNodela3R.SetNthControlPointLabel(0, '')
            self.MarkupNodelaaR.SetNthControlPointLabel(0, '')
            self.MarkupNodelamR.SetNthControlPointLabel(0, '')
            self.MarkupNodelapR.SetNthControlPointLabel(0, '')
            self.MarkupNodelipR.SetNthControlPointLabel(0, '')
            self.MarkupNodelicsR.SetNthControlPointLabel(0, '')
            self.MarkupNodelalR.SetNthControlPointLabel(0, '')
            self.MarkupNodelscR.SetNthControlPointLabel(0, '')

        # change the left breast numbers and colours if a left SLN was clicked
        if self.clicked == 'left SLN':
            # change the left breast numbers
            for i in range(num_rows):
                if self.tableNode.GetCellText(i, 0) == "0":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeLb0.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb0.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "1":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeLb1.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb1.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "2":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeLb2.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb2.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "3":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeLb3.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb3.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "4":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeLb4.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb4.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "5":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeLb5.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb5.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "6":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeLb6.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb6.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "7":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeLb7.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb7.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "8":
                    value = self.tableNode.GetCellText(i, 1)
                    self.MarkupNodeLb8.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb8.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "9":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeLb9.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb9.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "10":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeLb10.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb10.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "11":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeLb11.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb11.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "12":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeLb12.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeLb12.SetSelectedColor(1.0, 1.0, 1.0)

        # change the right breast numbers and colours if a right SLN was clicked
        if self.clicked == 'right SLN':
            # change the right breast numbers
            for i in range(num_rows):
                if self.tableNode.GetCellText(i, 0) == "0":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb0.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb0.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "1":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb1.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb1.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "2":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb2.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb2.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "3":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb3.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb3.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "4":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb4.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb4.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "5":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb5.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb5.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "6":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb6.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb6.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "7":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb7.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb7.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "8":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb8.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb8.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "9":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb9.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb9.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "10":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb10.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb10.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "11":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb11.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb11.SetSelectedColor(1.0, 1.0, 1.0)
                if self.tableNode.GetCellText(i, 0) == "12":
                    value = self.tableNode.GetCellText(i, 1)
                    label = value.split()
                    self.MarkupNodeRb12.SetNthControlPointLabel(0, (label[0]+'%'))
                    self.DisplayNodeRb12.SetSelectedColor(1.0, 1.0, 1.0)

    def MakeCPLabelNames(self):
        """
        Change the control point label to the relevant name
        """
        # set SLN control points to names
        self.MarkupNodelmedR.SetNthControlPointLabel(0, 'MED')
        self.MarkupNodermedR.SetNthControlPointLabel(0, 'MED')
        self.MarkupNodelINR.SetNthControlPointLabel(0, 'IN')
        self.MarkupNoderINR.SetNthControlPointLabel(0, 'IN')
        self.MarkupNodela2R.SetNthControlPointLabel(0, 'A2')
        self.MarkupNodera2R.SetNthControlPointLabel(0, 'A2')
        self.MarkupNodela3R.SetNthControlPointLabel(0, 'A3')
        self.MarkupNodera3R.SetNthControlPointLabel(0, 'A3')
        self.MarkupNodelaaR.SetNthControlPointLabel(0, 'AA')
        self.MarkupNoderaaR.SetNthControlPointLabel(0, 'AA')
        self.MarkupNodelamR.SetNthControlPointLabel(0, 'AM')
        self.MarkupNoderamR.SetNthControlPointLabel(0, 'AM')
        self.MarkupNodelapR.SetNthControlPointLabel(0, 'AP')
        self.MarkupNoderapR.SetNthControlPointLabel(0, 'AP')
        self.MarkupNodelipR.SetNthControlPointLabel(0, 'AIP')
        self.MarkupNoderipR.SetNthControlPointLabel(0, 'AIP')
        self.MarkupNodelicsR.SetNthControlPointLabel(0, 'IM')
        self.MarkupNodericsR.SetNthControlPointLabel(0, 'IM')
        self.MarkupNodelalR.SetNthControlPointLabel(0, 'AL')
        self.MarkupNoderalR.SetNthControlPointLabel(0, 'AL')
        self.MarkupNodelscR.SetNthControlPointLabel(0, 'SC')
        self.MarkupNoderscR.SetNthControlPointLabel(0, 'SC')
        # set breast control points to names
        self.MarkupNodeRb0.SetNthControlPointLabel(0, '0')
        self.MarkupNodeRb1.SetNthControlPointLabel(0, '1')
        self.MarkupNodeRb2.SetNthControlPointLabel(0, '2')
        self.MarkupNodeRb3.SetNthControlPointLabel(0, '3')
        self.MarkupNodeRb4.SetNthControlPointLabel(0, '4')
        self.MarkupNodeRb5.SetNthControlPointLabel(0, '5')
        self.MarkupNodeRb6.SetNthControlPointLabel(0, '6')
        self.MarkupNodeRb7.SetNthControlPointLabel(0, '7')
        self.MarkupNodeRb8.SetNthControlPointLabel(0, '8')
        self.MarkupNodeRb9.SetNthControlPointLabel(0, '9')
        self.MarkupNodeRb10.SetNthControlPointLabel(0, '10')
        self.MarkupNodeRb11.SetNthControlPointLabel(0, '11')
        self.MarkupNodeRb12.SetNthControlPointLabel(0, '12')
        self.MarkupNodeLb0.SetNthControlPointLabel(0, '0')
        self.MarkupNodeLb1.SetNthControlPointLabel(0, '1')
        self.MarkupNodeLb2.SetNthControlPointLabel(0, '2')
        self.MarkupNodeLb3.SetNthControlPointLabel(0, '3')
        self.MarkupNodeLb4.SetNthControlPointLabel(0, '4')
        self.MarkupNodeLb5.SetNthControlPointLabel(0, '5')
        self.MarkupNodeLb6.SetNthControlPointLabel(0, '6')
        self.MarkupNodeLb7.SetNthControlPointLabel(0, '7')
        self.MarkupNodeLb8.SetNthControlPointLabel(0, '8')
        self.MarkupNodeLb9.SetNthControlPointLabel(0, '9')
        self.MarkupNodeLb10.SetNthControlPointLabel(0, '10')
        self.MarkupNodeLb11.SetNthControlPointLabel(0, '11')
        self.MarkupNodeLb12.SetNthControlPointLabel(0, '12')
        # change breast label colour back
        self.DisplayNodeRb0.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeRb1.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeRb2.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeRb3.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeRb4.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeRb5.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeRb6.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeRb7.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeRb8.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeRb9.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeRb10.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeRb11.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeRb12.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb0.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb1.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb2.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb3.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb4.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb5.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb6.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb7.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb8.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb9.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb10.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb11.SetSelectedColor(0.0, 0.0, 0.0)
        self.DisplayNodeLb12.SetSelectedColor(0.0, 0.0, 0.0)

        if self.clearNode == "false":
            self.KeepPressedRed()
    def MakeCPLabelNone(self):
        """
        Removes the SLN control point labels
        """
        self.MarkupNodelmedR.SetNthControlPointLabel(0, '')
        self.MarkupNodermedR.SetNthControlPointLabel(0, '')
        self.MarkupNodelINR.SetNthControlPointLabel(0, '')
        self.MarkupNoderINR.SetNthControlPointLabel(0, '')
        self.MarkupNodela2R.SetNthControlPointLabel(0, '')
        self.MarkupNodera2R.SetNthControlPointLabel(0, '')
        self.MarkupNodela3R.SetNthControlPointLabel(0, '')
        self.MarkupNodera3R.SetNthControlPointLabel(0, '')
        self.MarkupNodelaaR.SetNthControlPointLabel(0, '')
        self.MarkupNoderaaR.SetNthControlPointLabel(0, '')
        self.MarkupNodelamR.SetNthControlPointLabel(0, '')
        self.MarkupNoderamR.SetNthControlPointLabel(0, '')
        self.MarkupNodelapR.SetNthControlPointLabel(0, '')
        self.MarkupNoderapR.SetNthControlPointLabel(0, '')
        self.MarkupNodelipR.SetNthControlPointLabel(0, '')
        self.MarkupNoderipR.SetNthControlPointLabel(0, '')
        self.MarkupNodelicsR.SetNthControlPointLabel(0, '')
        self.MarkupNodericsR.SetNthControlPointLabel(0, '')
        self.MarkupNodelalR.SetNthControlPointLabel(0, '')
        self.MarkupNoderscR.SetNthControlPointLabel(0, '')
        self.MarkupNoderalR.SetNthControlPointLabel(0, '')
        self.MarkupNodelscR.SetNthControlPointLabel(0, '')

    def SetColoursBack(self):
        """
        Change the SLN colour to either green or their individual colours. Change the breast region colour to original.
        """
        # check if the SLNs should all be green
        if self._parameterNode.GetParameter("greenSLNs") == "true":
            # make all the SLNs green
            self.DisplayNodelalSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelalR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelamSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelamR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelapSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelapR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNoderamSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNoderamR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNoderapSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNoderapR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodericsSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodericsR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNoderINSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNoderINR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelINSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelINR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelmedSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelmedR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodera2SLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodera2R.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodela2SLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodela2R.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelaaSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelaaR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelipSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelipR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNoderaaSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNoderaaR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNoderipSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNoderipR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelicsSLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelicsR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelscR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNoderscR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodermedR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNoderalR.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodera3R.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodela3R.SetSelectedColor(0.0, 0.6666666666666666, 0.0)

        # check if the SLNs should have individual node field colours
        elif self._parameterNode.GetParameter("greenSLNs") == "false":
            # make the SLNs separate colours
            self.DisplayNodelalSLNs.SetSelectedColor(0, 0.422, 0.622)
            self.DisplayNodelalR.SetSelectedColor(0, 0.422, 0.622)
            self.DisplayNodelamSLNs.SetSelectedColor(0.3333333333333333, 0.6666666666666666, 1.0)
            self.DisplayNodelamR.SetSelectedColor(0.3333333333333333, 0.6666666666666666, 1.0)
            self.DisplayNodelapSLNs.SetSelectedColor(0.3333333333333333, 1.0, 1.0)
            self.DisplayNodelapR.SetSelectedColor(0.3333333333333333, 1.0, 1.0)
            self.DisplayNoderamSLNs.SetSelectedColor(0.3333333333333333, 0.6666666666666666, 1.0)
            self.DisplayNoderamR.SetSelectedColor(0.3333333333333333, 0.6666666666666666, 1.0)
            self.DisplayNoderapSLNs.SetSelectedColor(0.3333333333333333, 1.0, 1.0)
            self.DisplayNoderapR.SetSelectedColor(0.3333333333333333, 1.0, 1.0)
            self.DisplayNodericsSLNs.SetSelectedColor(1.0, 1.0, 0.0)
            self.DisplayNodericsR.SetSelectedColor(1.0, 1.0, 0.0)
            self.DisplayNoderINSLNs.SetSelectedColor(0.858, 0.647, 1.000)
            self.DisplayNoderINR.SetSelectedColor(0.858, 0.647, 1.000)
            self.DisplayNodelINSLNs.SetSelectedColor(0.858, 0.647, 1.000)
            self.DisplayNodelINR.SetSelectedColor(0.858, 0.647, 1.000)
            self.DisplayNodelmedSLNs.SetSelectedColor(0.4412, 0.2549, 0.1843)
            self.DisplayNodelmedR.SetSelectedColor(0.4412, 0.2549, 0.1843)
            self.DisplayNodera2SLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodera2R.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodela2SLNs.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodela2R.SetSelectedColor(0.0, 0.6666666666666666, 0.0)
            self.DisplayNodelaaSLNs.SetSelectedColor(0.0, 0.0, 1.0)
            self.DisplayNodelaaR.SetSelectedColor(0.0, 0.0, 1.0)
            self.DisplayNodelipSLNs.SetSelectedColor(0.988, 0.416, 0.012)
            self.DisplayNodelipR.SetSelectedColor(0.988, 0.416, 0.012)
            self.DisplayNoderaaSLNs.SetSelectedColor(0.0, 0.0, 1.0)
            self.DisplayNoderaaR.SetSelectedColor(0.0, 0.0, 1.0)
            self.DisplayNoderipSLNs.SetSelectedColor(0.988, 0.416, 0.012)
            self.DisplayNoderipR.SetSelectedColor(0.988, 0.416, 0.012)
            self.DisplayNodelicsSLNs.SetSelectedColor(1.0, 1.0, 0.0)
            self.DisplayNodelicsR.SetSelectedColor(1.0, 1.0, 0.0)
            self.DisplayNodelscR.SetSelectedColor(0.666, 0.000, 0.498)
            self.DisplayNoderscR.SetSelectedColor(0.666, 0.000, 0.498)
            self.DisplayNodermedR.SetSelectedColor(0.4412, 0.2549, 0.1843)
            self.DisplayNoderalR.SetSelectedColor(0, 0.422, 0.622)
            self.DisplayNodera3R.SetSelectedColor(1.0, 0.33333, 1.0)
            self.DisplayNodela3R.SetSelectedColor(1.0, 0.33333, 1.0)

        # set the breast segments back as well
        self.Lb0DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.Lb1DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.Lb2DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.Lb3DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.Lb4DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.Lb5DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.Lb6DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.Lb7DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.Lb8DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.Lb9DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.Lb10DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.Lb11DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.Lb12DisplayNode.SetColor(0.874, 0.666, 0.545)
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_4")
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_5")
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_6")
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_7")
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_8")
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_9")
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_10")
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_11")
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_12")
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_13")
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_14")
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_15")
        self.RbreastSegDisplayNode.UnsetSegmentOverrideColor("Segment_17")

        if self.clearNode == "false":
            self.KeepPressedRed()

    def clearNodeSelection(self):
        """
        Stop showing table and reset the atlas if pressed
        """
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
        self.clearNode = "true"
        self.SetColoursBack()
        if self._parameterNode.GetParameter("numberLabelVis") == "true":
            self.MakeCPLabelNames()
        self.clearNode = "false"
        self.clicked = ''
        self.pressed = ''

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.
        self.setParameterNode(self.logic.getParameterNode())

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None and self.hasObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent,
                                                                self.updateGUIFromParameterNode):
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

        # Initial model update
        self.updateParameterNodeFromGUI()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        # Update checkboxes and radiobuttons
        self.ui.bayesianButton.checked = (self._parameterNode.GetParameter("bayesianVis") == "true")
        self.ui.bootstrappingButton.checked = (self._parameterNode.GetParameter("bootstrappingVis") == "true")
        self.ui.frequentistButton.checked = (self._parameterNode.GetParameter("frequentistVis") == "true")
        self.ui.numberLabelButton.checked = (self._parameterNode.GetParameter("numberLabelVis") == "true")
        self.ui.nameLabelButton.checked = (self._parameterNode.GetParameter("nameLabelVis") == "true")
        self.ui.noLabelButton.checked = (self._parameterNode.GetParameter("noLabelVis") == "true")
        self.ui.leftBreastCheckBox.checked = (self._parameterNode.GetParameter("LbVis") == "true")
        self.ui.rightBreastCheckBox.checked = (self._parameterNode.GetParameter("RbVis") == "true")
        self.ui.pectoralisMajorCheckBox.checked = (self._parameterNode.GetParameter("pecMajVis") == "true")
        self.ui.pectoralisMinorCheckBox.checked = (self._parameterNode.GetParameter("pecMinVis") == "true")
        self.ui.latissimusDorsiCheckBox.checked = (self._parameterNode.GetParameter("latDorVis") == "true")
        self.ui.repSLNOnlyCheckBox.checked = (self._parameterNode.GetParameter("repSLNVis") == "true")
        self.ui.ESTROCheckBox.checked = (self._parameterNode.GetParameter("ESTROVis") == "true")
        self.ui.greenSLNCheckBox.checked = (self._parameterNode.GetParameter("greenSLNs") == "true")
        self.ui.L1CheckBox.checked = (self._parameterNode.GetParameter("L1Vis") == "true")
        self.ui.L2CheckBox.checked = (self._parameterNode.GetParameter("L2Vis") == "true")
        self.ui.L3CheckBox.checked = (self._parameterNode.GetParameter("L3Vis") == "true")
        self.ui.L4CheckBox.checked = (self._parameterNode.GetParameter("L4Vis") == "true")
        self.ui.IMNCheckBox.checked = (self._parameterNode.GetParameter("IMNVis") == "true")
        self.ui.IC4CheckBox.checked = (self._parameterNode.GetParameter("IC4Vis") == "true")
        self.ui.INTPECTCheckBox.checked = (self._parameterNode.GetParameter("INTPECTVis") == "true")
        self.ui.SLNFieldModelCheckBox.checked = (self._parameterNode.GetParameter("SLNVolVis") == "true")

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        # update the parameter node based on the state of the check boxes and radiobuttons
        self._parameterNode.SetParameter("bayesianVis", "true" if self.ui.bayesianButton.checked else "false")
        self._parameterNode.SetParameter("bootstrappingVis", "true" if self.ui.bootstrappingButton.checked else "false")
        self._parameterNode.SetParameter("frequentistVis", "true" if self.ui.frequentistButton.checked else "false")
        self._parameterNode.SetParameter("numberLabelVis", "true" if self.ui.numberLabelButton.checked else "false")
        self._parameterNode.SetParameter("nameLabelVis", "true" if self.ui.nameLabelButton.checked else "false")
        self._parameterNode.SetParameter("noLabelVis", "true" if self.ui.noLabelButton.checked else "false")
        self._parameterNode.SetParameter("LbVis", "true" if self.ui.leftBreastCheckBox.checked else "false")
        self._parameterNode.SetParameter("RbVis", "true" if self.ui.rightBreastCheckBox.checked else "false")
        self._parameterNode.SetParameter("pecMajVis", "true" if self.ui.pectoralisMajorCheckBox.checked else "false")
        self._parameterNode.SetParameter("pecMinVis", "true" if self.ui.pectoralisMinorCheckBox.checked else "false")
        self._parameterNode.SetParameter("latDorVis", "true" if self.ui.latissimusDorsiCheckBox.checked else "false")
        self._parameterNode.SetParameter("repSLNVis", "true" if self.ui.repSLNOnlyCheckBox.checked else "false")
        self._parameterNode.SetParameter("ESTROVis", "true" if self.ui.ESTROCheckBox.checked else "false")
        self._parameterNode.SetParameter("greenSLNs", "true" if self.ui.greenSLNCheckBox.checked else "false")
        self._parameterNode.SetParameter("L1Vis", "true" if self.ui.L1CheckBox.checked else "false")
        self._parameterNode.SetParameter("L2Vis", "true" if self.ui.L2CheckBox.checked else "false")
        self._parameterNode.SetParameter("L3Vis", "true" if self.ui.L3CheckBox.checked else "false")
        self._parameterNode.SetParameter("L4Vis", "true" if self.ui.L4CheckBox.checked else "false")
        self._parameterNode.SetParameter("IMNVis", "true" if self.ui.IMNCheckBox.checked else "false")
        self._parameterNode.SetParameter("IC4Vis", "true" if self.ui.IC4CheckBox.checked else "false")
        self._parameterNode.SetParameter("INTPECTVis", "true" if self.ui.INTPECTCheckBox.checked else "false")
        self._parameterNode.SetParameter("SLNVolVis", "true" if self.ui.SLNFieldModelCheckBox.checked else "false")

        self._parameterNode.EndModify(wasModified)  # End modification of properties

        # Compute changes in model visibility
        self.process()

    def process(self):
        """
         Run the processing to change visibility of components in the model
        """
        # change the visibility between the representative SLNs and full atlas
        if self._parameterNode.GetParameter("repSLNVis") == "true":
            # hide the full atlas (no full atlas for ra3, la3, rsc, lsc,  ral)
            self.DisplayNodelalSLNs.SetVisibility(False)
            self.DisplayNodelamSLNs.SetVisibility(False)
            self.DisplayNodelapSLNs.SetVisibility(False)
            self.DisplayNoderamSLNs.SetVisibility(False)
            self.DisplayNoderapSLNs.SetVisibility(False)
            self.DisplayNodericsSLNs.SetVisibility(False)
            self.DisplayNoderINSLNs.SetVisibility(False)
            self.DisplayNodelINSLNs.SetVisibility(False)
            self.DisplayNodelmedSLNs.SetVisibility(False)
            self.DisplayNodera2SLNs.SetVisibility(False)
            self.DisplayNodela2SLNs.SetVisibility(False)
            self.DisplayNodelaaSLNs.SetVisibility(False)
            self.DisplayNodelipSLNs.SetVisibility(False)
            self.DisplayNoderaaSLNs.SetVisibility(False)
            self.DisplayNoderipSLNs.SetVisibility(False)
            self.DisplayNodelicsSLNs.SetVisibility(False)

        elif self._parameterNode.GetParameter("repSLNVis") == "false":
            # show the full atlas (no full atlas for ra3, la3, rsc, lsc, ral)
            self.DisplayNodelalSLNs.SetVisibility(True)
            self.DisplayNodelamSLNs.SetVisibility(True)
            self.DisplayNodelapSLNs.SetVisibility(True)
            self.DisplayNoderamSLNs.SetVisibility(True)
            self.DisplayNoderapSLNs.SetVisibility(True)
            self.DisplayNodericsSLNs.SetVisibility(True)
            self.DisplayNoderINSLNs.SetVisibility(True)
            self.DisplayNodelINSLNs.SetVisibility(True)
            self.DisplayNodelmedSLNs.SetVisibility(True)
            self.DisplayNodera2SLNs.SetVisibility(True)
            self.DisplayNodela2SLNs.SetVisibility(True)
            self.DisplayNodelaaSLNs.SetVisibility(True)
            self.DisplayNodelipSLNs.SetVisibility(True)
            self.DisplayNoderaaSLNs.SetVisibility(True)
            self.DisplayNoderipSLNs.SetVisibility(True)
            self.DisplayNodelicsSLNs.SetVisibility(True)

        # change the control point label to names if selected
        if self._parameterNode.GetParameter("nameLabelVis") == "true":
            self.MakeCPLabelNames()
        if self._parameterNode.GetParameter("numberLabelVis") == "true":
            if self.tableNode is not None:
                self.MakeCPLabelNumbers()
            else:
                self.MakeCPLabelNames()
        if self._parameterNode.GetParameter("noLabelVis") == "true":
            self.MakeCPLabelNone()

        # change the colour of the SLNs and breast regions which aren't selected
        self.SetColoursBack()

        # recall pressed functions to change stats table type without additional interaction
        # check that the table is showing first
        if slicer.app.layoutManager().activeMRMLTableViewNode().IsViewVisibleInLayout() == True:
            # breast regions
            if self.pressed == 'Rb0':
                self.Rb0pressed(self, self._parameterNode)
            if self.pressed == 'Rb1':
                self.Rb1pressed(self, self._parameterNode)
            if self.pressed == 'Rb2':
                self.Rb2pressed(self, self._parameterNode)
            if self.pressed == 'Rb3':
                self.Rb3pressed(self, self._parameterNode)
            if self.pressed == 'Rb4':
                self.Rb4pressed(self, self._parameterNode)
            if self.pressed == 'Rb5':
                self.Rb5pressed(self, self._parameterNode)
            if self.pressed == 'Rb6':
                self.Rb6pressed(self, self._parameterNode)
            if self.pressed == 'Rb7':
                self.Rb7pressed(self, self._parameterNode)
            if self.pressed == 'Rb8':
                self.Rb8pressed(self, self._parameterNode)
            if self.pressed == 'Rb9':
                self.Rb9pressed(self, self._parameterNode)
            if self.pressed == 'Rb10':
                self.Rb10pressed(self, self._parameterNode)
            if self.pressed == 'Rb11':
                self.Rb11pressed(self, self._parameterNode)
            if self.pressed == 'Rb12':
                self.Rb12pressed(self, self._parameterNode)
            if self.pressed == 'Lb0':
                self.Lb0pressed(self, self._parameterNode)
            if self.pressed == 'Lb1':
                self.Lb1pressed(self, self._parameterNode)
            if self.pressed == 'Lb2':
                self.Lb2pressed(self, self._parameterNode)
            if self.pressed == 'Lb3':
                self.Lb3pressed(self, self._parameterNode)
            if self.pressed == 'Lb4':
                self.Lb4pressed(self, self._parameterNode)
            if self.pressed == 'Lb5':
                self.Lb5pressed(self, self._parameterNode)
            if self.pressed == 'Lb6':
                self.Lb6pressed(self, self._parameterNode)
            if self.pressed == 'Lb7':
                self.Lb7pressed(self, self._parameterNode)
            if self.pressed == 'Lb8':
                self.Lb8pressed(self, self._parameterNode)
            if self.pressed == 'Lb9':
                self.Lb9pressed(self, self._parameterNode)
            if self.pressed == 'Lb10':
                self.Lb10pressed(self, self._parameterNode)
            if self.pressed == 'Lb11':
                self.Lb11pressed(self, self._parameterNode)
            if self.pressed == 'Lb12':
                self.Lb12pressed(self, self._parameterNode)
            # SLNs
            if self.pressed == 'lmed':
                self.lmedSLNspressed(self, self._parameterNode)
            if self.pressed == 'lIN':
                self.lINSLNspressed(self, self._parameterNode)
            if self.pressed == 'rmed':
                self.rmedSLNspressed(self, self._parameterNode)
            if self.pressed == 'rIN':
                self.rINSLNspressed(self, self._parameterNode)
            if self.pressed == 'la2':
                self.la2SLNspressed(self, self._parameterNode)
            if self.pressed == 'ra2':
                self.ra2SLNspressed(self, self._parameterNode)
            if self.pressed == 'la3':
                self.la3SLNspressed(self, self._parameterNode)
            if self.pressed == 'ra3':
                self.ra3SLNspressed(self, self._parameterNode)
            if self.pressed == 'laa':
                self.laaSLNspressed(self, self._parameterNode)
            if self.pressed == 'raa':
                self.raaSLNspressed(self, self._parameterNode)
            if self.pressed == 'lal':
                self.lalSLNspressed(self, self._parameterNode)
            if self.pressed == 'lap':
                self.lapSLNspressed(self, self._parameterNode)
            if self.pressed == 'rap':
                self.rapSLNspressed(self, self._parameterNode)
            if self.pressed == 'lam':
                self.lamSLNspressed(self, self._parameterNode)
            if self.pressed == 'ram':
                self.ramSLNspressed(self, self._parameterNode)
            if self.pressed == 'lics':
                self.licsSLNspressed(self, self._parameterNode)
            if self.pressed == 'rics':
                self.ricsSLNspressed(self, self._parameterNode)
            if self.pressed == 'lip':
                self.lipSLNspressed(self, self._parameterNode)
            if self.pressed == 'rip':
                self.ripSLNspressed(self, self._parameterNode)
            if self.pressed == 'rsc':
                self.rscSLNspressed(self, self._parameterNode)
            if self.pressed == 'lsc':
                self.lscSLNspressed(self, self._parameterNode)
            if self.pressed == 'ral':
                self.ralSLNspressed(self, self._parameterNode)

        # change the visibility of the SLN field volumes
        if self._parameterNode.GetParameter("SLNVolVis") == 'true':
            self.la2VolumeDisplayNode.SetVisibility(True)
            self.laaVolumeDisplayNode.SetVisibility(True)
            self.lalVolumeDisplayNode.SetVisibility(True)
            self.lamVolumeDisplayNode.SetVisibility(True)
            self.lapVolumeDisplayNode.SetVisibility(True)
            self.ra2VolumeDisplayNode.SetVisibility(True)
            self.raaVolumeDisplayNode.SetVisibility(True)
            self.ramVolumeDisplayNode.SetVisibility(True)
            self.rapVolumeDisplayNode.SetVisibility(True)
            self.ricsVolumeDisplayNode.SetVisibility(True)
            self.medVolumeDisplayNode.SetVisibility(True)
            self.RINVolumeDisplayNode.SetVisibility(True)
            self.laipVolumeDisplayNode.SetVisibility(True)
            self.raipVolumeDisplayNode.SetVisibility(True)
            self.licsVolumeDisplayNode.SetVisibility(True)
            self.LINVolumeDisplayNode.SetVisibility(True)

        if self._parameterNode.GetParameter("SLNVolVis") == 'false':
            self.la2VolumeDisplayNode.SetVisibility(False)
            self.laaVolumeDisplayNode.SetVisibility(False)
            self.lalVolumeDisplayNode.SetVisibility(False)
            self.lamVolumeDisplayNode.SetVisibility(False)
            self.lapVolumeDisplayNode.SetVisibility(False)
            self.ra2VolumeDisplayNode.SetVisibility(False)
            self.raaVolumeDisplayNode.SetVisibility(False)
            self.ramVolumeDisplayNode.SetVisibility(False)
            self.rapVolumeDisplayNode.SetVisibility(False)
            self.ricsVolumeDisplayNode.SetVisibility(False)
            self.medVolumeDisplayNode.SetVisibility(False)
            self.RINVolumeDisplayNode.SetVisibility(False)
            self.laipVolumeDisplayNode.SetVisibility(False)
            self.raipVolumeDisplayNode.SetVisibility(False)
            self.licsVolumeDisplayNode.SetVisibility(False)
            self.LINVolumeDisplayNode.SetVisibility(False)

        # change the view and ESTRO visibility based on check box selection
        if self._parameterNode.GetParameter("ESTROVis") == 'true':
            # change to the four up view
            slicer.app.layoutManager().resetSliceViews()
            slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
            # make the atlas back to original
            self.MakeCPLabelNames()
            self.SetColoursBack()

            # make the individual segment buttons enabled
            self.ui.L1CheckBox.setEnabled(True)
            self.ui.L2CheckBox.setEnabled(True)
            self.ui.L3CheckBox.setEnabled(True)
            self.ui.L4CheckBox.setEnabled(True)
            self.ui.IMNCheckBox.setEnabled(True)
            self.ui.IC4CheckBox.setEnabled(True)
            self.ui.INTPECTCheckBox.setEnabled(True)

            # turn on visibility of left and right estro segmentations
            # check if each segment should be displayed before showing it
            if self._parameterNode.GetParameter("L1Vis") == 'true':
                # show L1 segment
                self.ESTRO_L_L1_DisplayNode.SetVisibility(True)
                self.ESTRO_R_L1_DisplayNode.SetVisibility(True)
            if self._parameterNode.GetParameter("L2Vis") == 'true':
                # show L2 segment
                self.ESTRO_L_L2_DisplayNode.SetVisibility(True)
                self.ESTRO_R_L2_DisplayNode.SetVisibility(True)
            if self._parameterNode.GetParameter("L3Vis") == 'true':
                # show L3 segment
                self.ESTRO_L_L3_DisplayNode.SetVisibility(True)
                self.ESTRO_R_L3_DisplayNode.SetVisibility(True)
            if self._parameterNode.GetParameter("L4Vis") == 'true':
                # show L4 segment
                self.ESTRO_L_L4_DisplayNode.SetVisibility(True)
                self.ESTRO_R_L4_DisplayNode.SetVisibility(True)
            if self._parameterNode.GetParameter("IMNVis") == 'true':
                # show IMN segment
                self.ESTRO_L_IMN_DisplayNode.SetVisibility(True)
                self.ESTRO_R_IMN_DisplayNode.SetVisibility(True)
            if self._parameterNode.GetParameter("IC4Vis") == 'true':
                # show IC4 segment
                self.ESTRO_L_IC4_DisplayNode.SetVisibility(True)
                self.ESTRO_R_IC4_DisplayNode.SetVisibility(True)
            if self._parameterNode.GetParameter("INTPECTVis") == 'true':
                # show INTPECT segment
                self.ESTRO_L_INTPECT_DisplayNode.SetVisibility(True)
                self.ESTRO_R_INTPECT_DisplayNode.SetVisibility(True)

            # hide segments if they shouldn't be shown
            if self._parameterNode.GetParameter("L1Vis") == 'false':
                # don't show L1 segment
                self.ESTRO_L_L1_DisplayNode.SetVisibility(False)
                self.ESTRO_R_L1_DisplayNode.SetVisibility(False)
            if self._parameterNode.GetParameter("L2Vis") == 'false':
                # don't show L2 segment
                self.ESTRO_L_L2_DisplayNode.SetVisibility(False)
                self.ESTRO_R_L2_DisplayNode.SetVisibility(False)
            if self._parameterNode.GetParameter("L3Vis") == 'false':
                # don't show L3 segment
                self.ESTRO_L_L3_DisplayNode.SetVisibility(False)
                self.ESTRO_R_L3_DisplayNode.SetVisibility(False)
            if self._parameterNode.GetParameter("L4Vis") == 'false':
                # don't show L4 segment
                self.ESTRO_L_L4_DisplayNode.SetVisibility(False)
                self.ESTRO_R_L4_DisplayNode.SetVisibility(False)
            if self._parameterNode.GetParameter("IMNVis") == 'false':
                # don't show IMN segment
                self.ESTRO_L_IMN_DisplayNode.SetVisibility(False)
                self.ESTRO_R_IMN_DisplayNode.SetVisibility(False)
            if self._parameterNode.GetParameter("IC4Vis") == 'false':
                # don't show IC4 segment
                self.ESTRO_L_IC4_DisplayNode.SetVisibility(False)
                self.ESTRO_R_IC4_DisplayNode.SetVisibility(False)
            if self._parameterNode.GetParameter("INTPECTVis") == 'false':
                # don't show INTPECT segment
                self.ESTRO_L_INTPECT_DisplayNode.SetVisibility(False)
                self.ESTRO_R_INTPECT_DisplayNode.SetVisibility(False)

        elif self._parameterNode.GetParameter("ESTROVis") == 'false':
            # change to the 3D view
            # make sure not showing table node
            if slicer.app.layoutManager().activeMRMLTableViewNode().IsViewVisibleInLayout() == False:
                slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)

            # turn off visibility of all left and right estro segmentations
            self.ESTRO_L_IMN_DisplayNode.SetVisibility(False)
            self.ESTRO_R_IMN_DisplayNode.SetVisibility(False)
            self.ESTRO_L_IC4_DisplayNode.SetVisibility(False)
            self.ESTRO_R_IC4_DisplayNode.SetVisibility(False)
            self.ESTRO_L_INTPECT_DisplayNode.SetVisibility(False)
            self.ESTRO_R_INTPECT_DisplayNode.SetVisibility(False)
            self.ESTRO_L_L1_DisplayNode.SetVisibility(False)
            self.ESTRO_R_L1_DisplayNode.SetVisibility(False)
            self.ESTRO_L_L2_DisplayNode.SetVisibility(False)
            self.ESTRO_R_L2_DisplayNode.SetVisibility(False)
            self.ESTRO_L_L3_DisplayNode.SetVisibility(False)
            self.ESTRO_R_L3_DisplayNode.SetVisibility(False)
            self.ESTRO_L_L4_DisplayNode.SetVisibility(False)
            self.ESTRO_R_L4_DisplayNode.SetVisibility(False)

            # make the buttons for individual ESTRO segments disabled
            self.ui.L1CheckBox.setEnabled(False)
            self.ui.L2CheckBox.setEnabled(False)
            self.ui.L3CheckBox.setEnabled(False)
            self.ui.L4CheckBox.setEnabled(False)
            self.ui.IMNCheckBox.setEnabled(False)
            self.ui.IC4CheckBox.setEnabled(False)
            self.ui.INTPECTCheckBox.setEnabled(False)

        # change visibility of muscles based on check box selection
        # pectoralis major
        if self._parameterNode.GetParameter("pecMajVis") == 'true':
            self.pecMajSegDisplayNode.SetSegmentVisibility('Segment_1', True)  # do not change to SetVisibility
        elif self._parameterNode.GetParameter("pecMajVis") == 'false':
            self.pecMajSegDisplayNode.SetSegmentVisibility('Segment_1', False)  # do not change to SetVisibility

        # pectoralis minor
        if self._parameterNode.GetParameter("pecMinVis") == 'true':
            self.pecMinSegDisplayNode.SetVisibility(True)
        elif self._parameterNode.GetParameter("pecMinVis") == 'false':
            self.pecMinSegDisplayNode.SetVisibility(False)

        # latissimus dorsi
        if self._parameterNode.GetParameter("latDorVis") == 'true':
            self.latDorSegDisplayNode.SetVisibility(True)
        elif self._parameterNode.GetParameter("latDorVis") == 'false':
            self.latDorSegDisplayNode.SetVisibility(False)

        # change the breast visibility based on the check box selection
        if self._parameterNode.GetParameter("LbVis") == "true":
            if self._parameterNode.GetParameter("RbVis") == "true":
                # show both breasts
                # check if visibility needs to change
                if self.RbreastSegDisplayNode.GetVisibility() == 0:
                    # show right breast
                    self.RbreastSegDisplayNode.SetVisibility(True)
                    self.DisplayNodeRb0.SetVisibility(True)
                    self.DisplayNodeRb1.SetVisibility(True)
                    self.DisplayNodeRb2.SetVisibility(True)
                    self.DisplayNodeRb3.SetVisibility(True)
                    self.DisplayNodeRb4.SetVisibility(True)
                    self.DisplayNodeRb5.SetVisibility(True)
                    self.DisplayNodeRb6.SetVisibility(True)
                    self.DisplayNodeRb7.SetVisibility(True)
                    self.DisplayNodeRb8.SetVisibility(True)
                    self.DisplayNodeRb9.SetVisibility(True)
                    self.DisplayNodeRb10.SetVisibility(True)
                    self.DisplayNodeRb11.SetVisibility(True)
                    self.DisplayNodeRb12.SetVisibility(True)

                if self.Lb0DisplayNode.GetVisibility() == 0:
                    # show left breast
                    self.DisplayNodeLb0.SetVisibility(True)
                    self.DisplayNodeLb1.SetVisibility(True)
                    self.DisplayNodeLb2.SetVisibility(True)
                    self.DisplayNodeLb3.SetVisibility(True)
                    self.DisplayNodeLb4.SetVisibility(True)
                    self.DisplayNodeLb5.SetVisibility(True)
                    self.DisplayNodeLb6.SetVisibility(True)
                    self.DisplayNodeLb7.SetVisibility(True)
                    self.DisplayNodeLb8.SetVisibility(True)
                    self.DisplayNodeLb9.SetVisibility(True)
                    self.DisplayNodeLb10.SetVisibility(True)
                    self.DisplayNodeLb11.SetVisibility(True)
                    self.DisplayNodeLb12.SetVisibility(True)
                    self.Lb0DisplayNode.SetVisibility(True)
                    self.Lb1DisplayNode.SetVisibility(True)
                    self.Lb2DisplayNode.SetVisibility(True)
                    self.Lb3DisplayNode.SetVisibility(True)
                    self.Lb4DisplayNode.SetVisibility(True)
                    self.Lb5DisplayNode.SetVisibility(True)
                    self.Lb6DisplayNode.SetVisibility(True)
                    self.Lb7DisplayNode.SetVisibility(True)
                    self.Lb8DisplayNode.SetVisibility(True)
                    self.Lb9DisplayNode.SetVisibility(True)
                    self.Lb10DisplayNode.SetVisibility(True)
                    self.Lb11DisplayNode.SetVisibility(True)
                    self.Lb12DisplayNode.SetVisibility(True)
                    self.LbFatDisplayNode.SetVisibility(True)
            else:
                # show left breast only
                if self.RbreastSegDisplayNode.GetVisibility() == 1:
                    # hide right breast
                    self.RbreastSegDisplayNode.SetVisibility(False)
                    self.DisplayNodeRb0.SetVisibility(False)
                    self.DisplayNodeRb1.SetVisibility(False)
                    self.DisplayNodeRb2.SetVisibility(False)
                    self.DisplayNodeRb3.SetVisibility(False)
                    self.DisplayNodeRb4.SetVisibility(False)
                    self.DisplayNodeRb5.SetVisibility(False)
                    self.DisplayNodeRb6.SetVisibility(False)
                    self.DisplayNodeRb7.SetVisibility(False)
                    self.DisplayNodeRb8.SetVisibility(False)
                    self.DisplayNodeRb9.SetVisibility(False)
                    self.DisplayNodeRb10.SetVisibility(False)
                    self.DisplayNodeRb11.SetVisibility(False)
                    self.DisplayNodeRb12.SetVisibility(False)

                if self.Lb0DisplayNode.GetVisibility() == 0:
                    # show left breast
                    self.DisplayNodeLb0.SetVisibility(True)
                    self.DisplayNodeLb1.SetVisibility(True)
                    self.DisplayNodeLb2.SetVisibility(True)
                    self.DisplayNodeLb3.SetVisibility(True)
                    self.DisplayNodeLb4.SetVisibility(True)
                    self.DisplayNodeLb5.SetVisibility(True)
                    self.DisplayNodeLb6.SetVisibility(True)
                    self.DisplayNodeLb7.SetVisibility(True)
                    self.DisplayNodeLb8.SetVisibility(True)
                    self.DisplayNodeLb9.SetVisibility(True)
                    self.DisplayNodeLb10.SetVisibility(True)
                    self.DisplayNodeLb11.SetVisibility(True)
                    self.DisplayNodeLb12.SetVisibility(True)
                    self.Lb0DisplayNode.SetVisibility(True)
                    self.Lb1DisplayNode.SetVisibility(True)
                    self.Lb2DisplayNode.SetVisibility(True)
                    self.Lb3DisplayNode.SetVisibility(True)
                    self.Lb4DisplayNode.SetVisibility(True)
                    self.Lb5DisplayNode.SetVisibility(True)
                    self.Lb6DisplayNode.SetVisibility(True)
                    self.Lb7DisplayNode.SetVisibility(True)
                    self.Lb8DisplayNode.SetVisibility(True)
                    self.Lb9DisplayNode.SetVisibility(True)
                    self.Lb10DisplayNode.SetVisibility(True)
                    self.Lb11DisplayNode.SetVisibility(True)
                    self.Lb12DisplayNode.SetVisibility(True)
                    self.LbFatDisplayNode.SetVisibility(True)

        elif self._parameterNode.GetParameter("RbVis") == "true":
            # show right breast
            if self.RbreastSegDisplayNode.GetVisibility() == 0:
                # show right breast
                self.RbreastSegDisplayNode.SetVisibility(True)
                self.DisplayNodeRb0.SetVisibility(True)
                self.DisplayNodeRb1.SetVisibility(True)
                self.DisplayNodeRb2.SetVisibility(True)
                self.DisplayNodeRb3.SetVisibility(True)
                self.DisplayNodeRb4.SetVisibility(True)
                self.DisplayNodeRb5.SetVisibility(True)
                self.DisplayNodeRb6.SetVisibility(True)
                self.DisplayNodeRb7.SetVisibility(True)
                self.DisplayNodeRb8.SetVisibility(True)
                self.DisplayNodeRb9.SetVisibility(True)
                self.DisplayNodeRb10.SetVisibility(True)
                self.DisplayNodeRb11.SetVisibility(True)
                self.DisplayNodeRb12.SetVisibility(True)

            if self.Lb0DisplayNode.GetVisibility() == 1:
                # hide left breast
                self.DisplayNodeLb0.SetVisibility(False)
                self.DisplayNodeLb1.SetVisibility(False)
                self.DisplayNodeLb2.SetVisibility(False)
                self.DisplayNodeLb3.SetVisibility(False)
                self.DisplayNodeLb4.SetVisibility(False)
                self.DisplayNodeLb5.SetVisibility(False)
                self.DisplayNodeLb6.SetVisibility(False)
                self.DisplayNodeLb7.SetVisibility(False)
                self.DisplayNodeLb8.SetVisibility(False)
                self.DisplayNodeLb9.SetVisibility(False)
                self.DisplayNodeLb10.SetVisibility(False)
                self.DisplayNodeLb11.SetVisibility(False)
                self.DisplayNodeLb12.SetVisibility(False)
                self.Lb0DisplayNode.SetVisibility(False)
                self.Lb1DisplayNode.SetVisibility(False)
                self.Lb2DisplayNode.SetVisibility(False)
                self.Lb3DisplayNode.SetVisibility(False)
                self.Lb4DisplayNode.SetVisibility(False)
                self.Lb5DisplayNode.SetVisibility(False)
                self.Lb6DisplayNode.SetVisibility(False)
                self.Lb7DisplayNode.SetVisibility(False)
                self.Lb8DisplayNode.SetVisibility(False)
                self.Lb9DisplayNode.SetVisibility(False)
                self.Lb10DisplayNode.SetVisibility(False)
                self.Lb11DisplayNode.SetVisibility(False)
                self.Lb12DisplayNode.SetVisibility(False)
                self.LbFatDisplayNode.SetVisibility(False)
        else:
            # show neither breast
            if self.RbreastSegDisplayNode.GetVisibility() == 1:
                # hide right breast
                self.RbreastSegDisplayNode.SetVisibility(False)
                self.DisplayNodeRb0.SetVisibility(False)
                self.DisplayNodeRb1.SetVisibility(False)
                self.DisplayNodeRb2.SetVisibility(False)
                self.DisplayNodeRb3.SetVisibility(False)
                self.DisplayNodeRb4.SetVisibility(False)
                self.DisplayNodeRb5.SetVisibility(False)
                self.DisplayNodeRb6.SetVisibility(False)
                self.DisplayNodeRb7.SetVisibility(False)
                self.DisplayNodeRb8.SetVisibility(False)
                self.DisplayNodeRb9.SetVisibility(False)
                self.DisplayNodeRb10.SetVisibility(False)
                self.DisplayNodeRb11.SetVisibility(False)
                self.DisplayNodeRb12.SetVisibility(False)

            if self.Lb0DisplayNode.GetVisibility() == 1:
                # hide left breast
                self.DisplayNodeLb0.SetVisibility(False)
                self.DisplayNodeLb1.SetVisibility(False)
                self.DisplayNodeLb2.SetVisibility(False)
                self.DisplayNodeLb3.SetVisibility(False)
                self.DisplayNodeLb4.SetVisibility(False)
                self.DisplayNodeLb5.SetVisibility(False)
                self.DisplayNodeLb6.SetVisibility(False)
                self.DisplayNodeLb7.SetVisibility(False)
                self.DisplayNodeLb8.SetVisibility(False)
                self.DisplayNodeLb9.SetVisibility(False)
                self.DisplayNodeLb10.SetVisibility(False)
                self.DisplayNodeLb11.SetVisibility(False)
                self.DisplayNodeLb12.SetVisibility(False)
                self.Lb0DisplayNode.SetVisibility(False)
                self.Lb1DisplayNode.SetVisibility(False)
                self.Lb2DisplayNode.SetVisibility(False)
                self.Lb3DisplayNode.SetVisibility(False)
                self.Lb4DisplayNode.SetVisibility(False)
                self.Lb5DisplayNode.SetVisibility(False)
                self.Lb6DisplayNode.SetVisibility(False)
                self.Lb7DisplayNode.SetVisibility(False)
                self.Lb8DisplayNode.SetVisibility(False)
                self.Lb9DisplayNode.SetVisibility(False)
                self.Lb10DisplayNode.SetVisibility(False)
                self.Lb11DisplayNode.SetVisibility(False)
                self.Lb12DisplayNode.SetVisibility(False)
                self.LbFatDisplayNode.SetVisibility(False)

#
# BreastCancerAtlasLogic
#

class BreastCancerAtlasLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)
