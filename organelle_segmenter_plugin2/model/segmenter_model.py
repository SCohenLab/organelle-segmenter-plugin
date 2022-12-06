from dataclasses import dataclass
from typing import List
from napari.layers import Layer
from .channel import Channel

# from aicssegmentation.workflow import Workflow
from infer_subc_2d.workflow import Workflow


@dataclass
class SegmenterModel:
    """
    Main Segmenter plugin model
    """

    layers: List[str] = None
    selected_layer: Layer = None
    # for infer_subc_2d we actually want to select Z's not channels
    # TODO: change channels to zslices & selected_zslice
    channels: List[str] = None
    selected_channel: Channel = None
    workflows: List[str] = None
    active_workflow: Workflow = None

    def reset(self):
        """
        Reset model state
        """
        self.layers = None
        self.selected_layer = None
        self.channels = None
        self.selected_channel = None
        self.workflows = None
        self.active_workflow = None
