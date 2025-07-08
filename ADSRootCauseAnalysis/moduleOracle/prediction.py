from .moduleOracle import MoudleOracle
import math
import numpy as np

class PredictionOracle(MoudleOracle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.predictions_data = kwargs.get('predictions', {})
        self.pose = kwargs.get('pose', {})
        self.actual_traj_actor_view = kwargs.get('actual_traj_actor_view', {})
        self.ego_id = kwargs.get('ego_id', None)
        self.meta_data = kwargs.get('meta_data', {})
        self.cfg = kwargs.get('cfg', None)

    def _handle_at_timestamp(self, timestamp):
        predictions = self.predictions_data[timestamp]
        self.failure, self.danger_score = self.__calc_prediction_status(predictions, timestamp)

    def __calc_prediction_status(self, predictions, timestamp):
        max_error = 0
        for pred_id, pred_data in predictions.items():
            if pred_id == self.ego_id:
                continue
            for future_ts, pred_loc in pred_data.items():
                future_timestamp = timestamp + \
                    int(future_ts)*self.meta_data['timesteps_per_frame']
                if future_timestamp >= self.meta_data['total_frames'] * self.meta_data['timesteps_per_frame']:
                    continue
                ego_x, ego_y = float(self.pose[future_timestamp]['x']), float(
                    self.pose[future_timestamp]['y'])
                yaw = float(self.pose[timestamp]['yaw'])
                theta = math.radians(yaw)
                x = ego_x + pred_loc['x'] * \
                    math.cos(theta) - pred_loc['y'] * math.sin(theta)
                y = ego_y + pred_loc['x'] * \
                    math.sin(theta) + pred_loc['y'] * math.cos(theta)
                actual_x, actual_y = self.actual_traj_actor_view[pred_id]['location'][future_timestamp][
                    'x'], self.actual_traj_actor_view[pred_id]['location'][future_timestamp]['y']
                error = np.sqrt((x - actual_x)**2 + (y - actual_y)**2)
                dis = np.sqrt((ego_x - actual_x)**2 + (ego_y - actual_y)**2)
                score = error/dis
                if score > max_error:
                    max_error = score
                if dis < 4 and error/dis >= self.cfg.module_setting.prediction.pred_score_threshold:
                    return True, max_error
        return False, max_error