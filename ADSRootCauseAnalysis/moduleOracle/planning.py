from .moduleOracle import MoudleOracle
import numpy as np
import math

class PlanningOracle(MoudleOracle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.planning_data = kwargs.get('planning_data', {})
        self.predictions = kwargs.get('predictions', {})
        self.predictions_with_perception = kwargs.get('predictions_with_perception', {})
        self.pose = kwargs.get('pose', {})
        self.actual_traj_actor_view = kwargs.get('actual_traj_actor_view', {})
        self.ego_id = kwargs.get('ego_id', None)
        self.meta_data = kwargs.get('meta_data', {})
        self.cfg = kwargs.get('cfg', None)
        

    def _handle_at_timestamp(self, timestamp):
        planning_data = self.planning_data.get(timestamp, {})
        predictions = self.predictions.get(timestamp, {})
        self.failure, self.danger_score = self.__calc_planning_status(
            planning_data, predictions, timestamp)

    def __calc_planning_status(self, planning_data, prediction_data, timestamp):
        yaw = float(self.pose[timestamp]['yaw'])
        theta = math.radians(yaw)
        ego_x, ego_y = planning_data['0']['x'], planning_data['0']['y']
        if not prediction_data or not planning_data:
            return False, 0
        pred_id_in_gt = {}

        for pred_id, pred_data in prediction_data.items():
            x = float(pred_data['0']['x'])
            y = float(pred_data['0']['y'])
            min_dis = 100
            for pred_gt_id, pred_gt_data in self.predictions_with_perception[timestamp].items():
                if pred_gt_id == self.ego_id:
                    continue
                gx = float(pred_gt_data['0']['x'])
                gy = float(pred_gt_data['0']['y'])
                dis = np.sqrt((gx - x)**2 + (gy - y)**2)
                if dis < min_dis:
                    min_dis = dis
                    pred_id_in_gt[pred_id] = pred_gt_id

        min_score = 1
        for future_ts, plan_loc in planning_data.items():
            if future_ts == '0':
                continue
            future_timestamp = timestamp + \
                int(future_ts)*self.meta_data['timesteps_per_frame']
            if future_timestamp > self.meta_data['total_frames'] * self.meta_data['timesteps_per_frame']:
                continue

            for pred_id, pred_data in prediction_data.items():
                pred_loc = prediction_data[pred_id].get(future_ts, 'None')
                if pred_loc == 'None' or pred_id not in pred_id_in_gt:
                    continue
                else:
                    x = ego_x + pred_data[future_ts]['x'] * \
                        math.cos(theta) - \
                        pred_data[future_ts]['y'] * math.sin(theta)
                    y = ego_y + pred_data[future_ts]['x'] * \
                        math.sin(theta) + \
                        pred_data[future_ts]['y'] * math.cos(theta)
                stats, score = self.check_collision(
                    plan_loc, self.ego_id,
                    (x, y), pred_id_in_gt[pred_id], future_ts=future_ts)
                if stats:
                    return True, 1
                if score < min_score:
                    min_score = score
        return False, 1 - min(1, min_score)
    
    def check_collision(self, ego_location, ego_id, actor_location, actor_id, future_ts):
        actor_extent = self.actual_traj_actor_view[actor_id]['extent']
        ego_extent = self.actual_traj_actor_view[ego_id]['extent']

        toleration = 0 if int(future_ts) < self.cfg.module_setting.planning.planning_toleration_future_step \
            else -self.cfg.module_setting.planning.planning_toleration

        diff_x = abs(ego_location['x'] - actor_location[0]) - \
            (actor_extent['x'] + ego_extent['x'] -
             self.meta_data['ego_config']['camera']['camera_loc'][0])
        diff_y = abs(ego_location['y'] - actor_location[1]) - \
            (actor_extent['y'] + ego_extent['y'] -
             self.meta_data['ego_config']['camera']['camera_loc'][1])
        if diff_x < toleration and diff_y < toleration:
            return True, 0
        return False, math.sqrt(diff_x**2 + diff_y**2)
