import pathlib
import json
from ADSRootCauseAnalysis.utils.common import load_json
import glob
from enum import IntFlag
from ADSRootCauseAnalysis.moduleOracle import PerceptionOracle, PredictionOracle, PlanningOracle, ControllerOracle
from collections import OrderedDict, defaultdict
import warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)


class RCHandler:
    def __init__(self, cfg):
        self.cfg = cfg
        self.base_dir = pathlib.Path(cfg.log_dir)
        self.meta_data = load_json(self.base_dir.joinpath('metadata.json'))
        self.timestamps = self._get_valid_timestamps()
        self.__get_data()
        self.__get_actual_traj_actor_view()
        self.__build_oracles()

    def _get_valid_timestamps(self):
        timestamps = []
        for data_file in glob.glob(self.base_dir.joinpath('actors').joinpath('*.json').as_posix()):
            timestamp = int(data_file.split('-')[-1].split('.')[0])
            timestamps.append(timestamp)
        return sorted(timestamps)

    def __get_actual_traj_actor_view(self):
        self.actual_traj_actor_view = {}
        pose_timestamps = sorted(self.data['actors'].keys())
        for pt in pose_timestamps:
            for actor_id, actor_data in self.data['actors'][pt].items():
                if actor_id not in self.actual_traj_actor_view:
                    self.actual_traj_actor_view[actor_id] = {}
                    self.actual_traj_actor_view[actor_id]['extent'] = actor_data['extent']
                    self.actual_traj_actor_view[actor_id]['location'] = OrderedDict(
                    )
                    self.actual_traj_actor_view[actor_id]['location'][pt] = actor_data['location']
                else:
                    self.actual_traj_actor_view[actor_id]['location'][pt] = actor_data['location']
        for actor_id, actor_data in self.data['actors'][50].items():
            x, y = actor_data['location']['x'], actor_data['location']['y']
            ego_x, ego_y = float(self.data['pose'][50]['x']), float(
                self.data['pose'][50]['y'])
            if abs(x-ego_x) < 0.5 and abs(y-ego_y) < 0.5:
                self.ego_id = actor_id
                break

    def __get_data(self):
        self.profile_categories = ['actors', 'bboxes', 'bboxes_gt', 'pose',
                                   'predictions', 'predictions_with_perception',
                                   'waypoint']
        self.data = {}
        for pc in self.profile_categories:
            self.data[pc] = {}
            for data_file in glob.glob(self.base_dir.joinpath(pc).joinpath('*.json').as_posix()):
                timestamp = int(data_file.split('-')[-1].split('.')[0])
                self.data[pc][timestamp] = load_json(data_file)

    def __build_oracles(self):
        self.perception_oracle = PerceptionOracle(
            bboxes=self.data['bboxes'], bboxes_gt=self.data['bboxes_gt'],
            cfg=self.cfg)
        self.prediction_oracle = PredictionOracle(
            predictions=self.data['predictions_with_perception'], pose=self.data['pose'],
            actual_traj_actor_view=self.actual_traj_actor_view, ego_id=self.ego_id, 
            meta_data=self.meta_data, cfg=self.cfg)
        self.planning_oracle = PlanningOracle(
            planning_data=self.data['waypoint'], predictions=self.data['predictions'],
            predictions_with_perception=self.data['predictions_with_perception'],
            pose=self.data['pose'], actual_traj_actor_view=self.actual_traj_actor_view, ego_id=self.ego_id, 
            meta_data=self.meta_data, cfg=self.cfg)
        self.controller_oracle = ControllerOracle(
            planning_data=self.data['waypoint'], pose=self.data['pose'],
            meta_data=self.meta_data, cfg=self.cfg)
        self.oracles = {
            'perception': self.perception_oracle,
            'prediction': self.prediction_oracle,
            'planning': self.planning_oracle,
            'controller': self.controller_oracle
        }

    def __get_bbox_data(self):
        bbox_data = {}
        for bbox_file in glob.glob(self.base_dir.joinpath('bboxes', '*.json').as_posix()):
            timestamp = int(bbox_file.split('-')[-1].split('.')[0])
            bbox_data[timestamp] = load_json(bbox_file)
        return bbox_data

    def collect_root_cause(self):
        stats = {oracle_md:{'collision': 0, 'safe': 0} for oracle_md, oracle in self.oracles.items()}
        for ts in self.timestamps:
            for oracle_md, oracle in self.oracles.items():
                md_failure, md_score = oracle.calc_root_cause_at_timestamp(ts)
                if md_failure:
                    if self.meta_data['collision_frame'] == -1:
                        stats[oracle_md]['safe'] += 1
                    elif ts > (self.meta_data['collision_frame'] - self.cfg.effect_time_window)*self.meta_data['timesteps_per_frame']:
                        stats[oracle_md]['collision'] += 1
                    else:
                        stats[oracle_md]['safe'] += 1
        if self.cfg.display_results:
            self.display_results(stats)
        return stats

    def display_results(self, stats):
        root = []
        for oracle_md, oracle_stats in stats.items():
            print(f"{oracle_md} error - Cause Collisions: {oracle_stats['collision']}, Safe: {oracle_stats['safe']}")
            if oracle_stats['collision']:
                root.append(oracle_md)
        if root:
            print(f"Root cause(s) of collision: {', '.join(root)}")
        print("Analysis complete.")
                        


