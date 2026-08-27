from .base import BaseAdapter, AdapterStatus
from .pikalytics import PikalyticsAdapter
from .munchstats import MunchStatsAdapter
from .replica_teams import ReplicaTeamsAdapter
from .labmaus import LabMausAdapter
from .reportworm import ReportWormAdapter
from .cut_explorer import CutExplorerAdapter
from .showdown import ShowdownAdapter
from .vgc_guide import VGCGuideAdapter

REGISTRY: dict[str, type[BaseAdapter]] = {
    a.key: a
    for a in [
        PikalyticsAdapter,
        MunchStatsAdapter,
        ReplicaTeamsAdapter,
        LabMausAdapter,
        ReportWormAdapter,
        CutExplorerAdapter,
        ShowdownAdapter,
        VGCGuideAdapter,
    ]
}

__all__ = ["BaseAdapter", "AdapterStatus", "REGISTRY"]
