from typing import List

from aicssegmentation.workflow.workflow_definition import WorkflowDefinition
from napari.layers.base.base import Layer
from qtpy.QtWidgets import (
    QComboBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from qtpy.QtGui import QStandardItem, QStandardItemModel
from qtpy import QtCore

from organelle_segmenter_plugin2.model.channel import Channel
from organelle_segmenter_plugin2.model.segmenter_model import SegmenterModel
from organelle_segmenter_plugin2.controller._interfaces import IWorkflowSelectController
from organelle_segmenter_plugin2.core.view import View
from organelle_segmenter_plugin2.widgets.form import Form
from organelle_segmenter_plugin2.widgets.warning_message import WarningMessage
from organelle_segmenter_plugin2.util.ui_utils import UiUtils

from organelle_segmenter_plugin2.widgets.workflow_dropdown import WorkflowDropDown
from ._main_template import MainTemplate


class WorkflowSelectView(View):

    _combo_layers: QComboBox
    _combo_channels: QComboBox
    _load_image_warning: WarningMessage
    _workflow_grid: WorkflowDropDown
    # _combo_workflows: QComboBox
    # _workflows: List[WorkflowDefinition]
    # _workflow_names: List[str]

    def __init__(self, controller: IWorkflowSelectController):
        super().__init__(template_class=MainTemplate)

        if controller is None:
            raise ValueError("controller")
        self._controller = controller
        self.setObjectName("workflowSelectView")

    def load(self, model: SegmenterModel):
        self._setup_ui()

        self.update_layers(model.layers, model.selected_layer)
        self.update_channels(model.channels, model.selected_channel)
        self._load_workflows(model.workflows)

    #    # JAH: combo_box_workflows
    #     # self._workflows = self._controller._workflow_engine._load_workflow_definitions()
    #     # self.update_workflows(self._workflows)
    #     self.update_workflows(model.workflows)

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Title
        workflow_selection_title = QLabel("Workflow selection steps:")
        workflow_selection_title.setObjectName("workflowSelectionTitle")

        # Warning
        self._load_image_warning = WarningMessage("Open a 3D image in Napari first!")
        self._load_image_warning.setVisible(False)

        # Dropdowns
        layers_dropdown = UiUtils.dropdown_row("1.", "Select organelle's 3D Napari image layer", enabled=False)
        self._combo_layers = layers_dropdown.widget
        self._combo_layers.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self._combo_layers.setMaxVisibleItems(20)
        self._combo_layers.activated.connect(self._combo_layers_activated)

        channels_dropdown = UiUtils.dropdown_row("2.", "Select a 3D image data channel (0)", enabled=False)
        self._combo_channels = channels_dropdown.widget
        self._combo_channels.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self._combo_channels.setMaxVisibleItems(20)
        self._combo_channels.activated.connect(self._combo_channels_activated)

        layer_channel_selections = QWidget()
        layer_channel_selections.setLayout(Form([layers_dropdown, channels_dropdown]))

        # # JAH dropdown to replace WorkflowDD widget
        # workflows_dropdown = UiUtils.dropdown_row("3.", "Select a workflow", enabled=False)
        # self._combo_workflows = workflows_dropdown.widget
        # self._combo_channels.setStyleSheet("QComboBox { combobox-popup: 0; }")
        # self._combo_workflows.setMaxVisibleItems(20)
        # self._combo_workflows.activated.connect(self._combo_workflows_activated)

        # # JAH
        # layer_channel_selections.setLayout(Form([layers_dropdown, channels_dropdown, workflows_dropdown]))

        # Add all widgets
        widgets = [
            workflow_selection_title,
            self._load_image_warning,
            layer_channel_selections,
        ]
        for widget in widgets:
            layout.addWidget(widget)

        self._workflow_grid = WorkflowDropDown()
        self._workflow_grid.workflowSelected.connect(self._workflow_selected)
        self.layout().addWidget(self._workflow_grid)

    def update_layers(self, layers: List[str], selected_layer: Layer = None):
        """
        Update / repopulate the list of selectable layers
        Inputs:
            layers: List of layer names
            selected_layer_name: (optional) name of the layer to pre-select
        """
        self._reset_combo_box(self._combo_layers)

        if layers is None or len(layers) == 0:
            self._load_image_warning.setVisible(True)
            self._combo_layers.setEnabled(False)
        else:
            # reverse layer list when adding to combobox
            # to mimic layer list on napari ui
            self._combo_layers.addItems(layers[::-1])
            if selected_layer is not None:
                self._combo_layers.setCurrentText(selected_layer.name)
            self._combo_layers.setEnabled(True)
            self._load_image_warning.setVisible(False)

    def update_channels(self, channels: List[Channel], selected_channel: Channel = None):
        """
        Update / repopulate the list of selectable channels
        Inputs:
            channels: List of channel names
        """
        self._reset_combo_box(self._combo_channels)

        if channels is None or len(channels) == 0:
            self._combo_channels.setEnabled(False)
        else:
            model = QStandardItemModel()
            model.appendRow(QStandardItem(self._combo_channels.itemText(0)))

            for channel in channels:
                item = QStandardItem(channel.display_name)
                item.setData(channel, QtCore.Qt.UserRole)
                model.appendRow(item)

            self._combo_channels.setModel(model)

            if selected_channel is not None:
                # TODO relying on display name isn't the best as it will probably
                #      cause issues if channel names aren't unique
                # TODO refactor by making Channel derive from QStandardItem and do something like this:
                #      selected_index = model.indexFromItem(selected_channel)
                #      self.combo_channels.setCurrentIndex(selected_index)
                self._combo_channels.setCurrentText(selected_channel.display_name)

            self._combo_channels.setEnabled(True)

    def update_workflows(self, enabled: bool):
        """
        Update state of workflow list
        Inputs:
            enabled: True to enable the list, False to disable it
        """
        self._workflow_grid.setEnabled(enabled)

    def _load_workflows(self, workflows: List[WorkflowDefinition]):
        """
        Load workflows into workflow grid
        """
        # self._workflow = workflows
        # self._workflow_names = [wf.name for wf in workflows]
        self._workflow_grid.load_workflows(workflows)

    def _reset_combo_box(self, combo: QComboBox):
        """
        Reset a combo box to its original state, keeping the header but removing all other items
        """
        if combo.count() > 0:
            header = combo.itemText(0)
            combo.clear()
            combo.addItem(header)

    #####################################################################
    # Event handlers
    #####################################################################

    def _combo_layers_activated(self, index: int):
        if index == 0:  # index 0 is the dropdown header
            self._controller.unselect_layer()
        else:
            self._controller.select_layer(self._combo_layers.itemText(index))

    def _combo_channels_activated(self, index: int):
        if index == 0:
            self._controller.unselect_channel()
        else:
            self._controller.select_channel(self._combo_channels.itemData(index, role=QtCore.Qt.UserRole))

    def _workflow_selected(self, workflow_name: str):
        self._controller.select_workflow(workflow_name)