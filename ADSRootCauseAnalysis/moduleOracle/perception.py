from .moduleOracle import MoudleOracle
from dataclasses import dataclass
from shapely.geometry import box
import numpy as np

@dataclass
class BBox:
    id: int
    x1: float
    y1: float
    x2: float
    y2: float

    def to_polygon(self):
        return box(self.x1, self.y1, self.x2, self.y2)

    @classmethod
    def from_dict(cls, d):
        (x1, y1), (x2, y2) = d['bounding_box']
        return cls(id=d['id'], x1=x1, y1=y1, x2=x2, y2=y2)

class PerceptionOracle(MoudleOracle):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.bboxes_data = kwargs.get('bboxes', {})
        self.bboxes_gt_data = kwargs.get('bboxes_gt', {})
        self.cfg = kwargs.get('cfg', None)

    def _handle_at_timestamp(self, timestamp):
        bboxes = [BBox.from_dict(bb) for bb in self.bboxes_data[timestamp]]
        bboxes_gt = [BBox.from_dict(bb) for bb in self.bboxes_gt_data[timestamp]]
        ious = best_ious(bboxes, bboxes_gt)
        mean_iou = np.mean(ious)
        is_outlier = mean_iou < self.cfg.module_setting.perception.perc_score_threshold
        self.failure = is_outlier
        self.danger_score = 1 - mean_iou



def compute_iou(b1: BBox, b2: BBox) -> float:
    p1 = b1.to_polygon()
    p2 = b2.to_polygon()
    inter = p1.intersection(p2).area
    union = p1.union(p2).area
    return inter / union if union > 0 else 0.0

def best_ious(group1, group2, iou_threshold=0.0):
    used = set()
    ious = []
    for b1 in group1:
        best = None
        best_iou = 0.0
        for idx2, b2 in enumerate(group2):
            if idx2 in used:
                continue
            iou = compute_iou(b1, b2)
            if iou > best_iou:
                best = idx2
                best_iou = iou
        if best is not None and best_iou >= iou_threshold:
            ious.append(round(best_iou, 4))
            used.add(best)
    return ious

