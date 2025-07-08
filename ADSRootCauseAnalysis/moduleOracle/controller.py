from .moduleOracle import MoudleOracle

class ControllerOracle(MoudleOracle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.planning_data = kwargs.get('planning_data', {})
        self.pose = kwargs.get('pose', {})
        self.meta_data = kwargs.get('meta_data', {})
        self.cfg = kwargs.get('cfg', None)

    def _handle_at_timestamp(self, timestamp):
        planning_data = self.planning_data[timestamp]
        # pose_data = self.pose[timestamp]
        self.failure, self.danger_score = self.__calc_controller_stats(planning_data, timestamp)

    def __calc_controller_stats(self, planning_data, timestamp):
        if not planning_data:
            return False, 0
        next_timestamp = timestamp + self.meta_data['timesteps_per_frame']
        if next_timestamp > self.meta_data['total_frames'] * self.meta_data['timesteps_per_frame']:
            return False, 0
        next_plan_loc = planning_data['1']
        next_actual_loc = self.pose[next_timestamp]
        ego_x, ego_y = float(self.pose[timestamp]['x']), float(self.pose[timestamp]['y'])
        plan_dis_x, plan_dis_y = float(next_plan_loc['x']) - ego_x, float(next_plan_loc['y'])-ego_y
        actual_dis_x, actual_dis_y = float(next_actual_loc['x']) - ego_x, float(next_actual_loc['y']) - ego_y
        if abs(actual_dis_x) <0.6 and abs(actual_dis_y) <0.6:
            return False,0
        x_score = judge_val(actual_dis_x, plan_dis_x)
        y_score = judge_val(actual_dis_y, plan_dis_y)
        if x_score < 0.1 and y_score<0.1:
            res = False
        else:
            res = True
        score = 1 - max(x_score, y_score)
        return res, score

def judge_val(a,b):
    if abs(b) < 0.5:
        return 1
    diff = abs(a-b)
    if diff < 0.5:
        return 1
    return abs(a-b)/abs(b)