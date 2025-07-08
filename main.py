import hydra
from omegaconf import DictConfig, OmegaConf
import os
from ADSRootCauseAnalysis.RCHandler import RCHandler

@hydra.main(version_base=None, config_path=os.path.join('ADSRootCauseAnalysis','config'), config_name="RCanaylsis")
def main(cfg: DictConfig):
    handler = RCHandler(cfg)
    stats = handler.collect_root_cause()
    print(stats)

if __name__ == "__main__":
    main()