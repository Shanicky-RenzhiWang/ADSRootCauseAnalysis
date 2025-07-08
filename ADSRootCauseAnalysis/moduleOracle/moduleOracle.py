class MoudleOracle:
    def __init__(self, *args, **kwargs):
        self.failure = False
        self.danger_score = 0.0

    def _handle_at_timestamp(self, timestamp):
        pass

    def calc_root_cause_at_timestamp(self, timestamp):
        self._handle_at_timestamp(timestamp)
        return self.failure, self.danger_score