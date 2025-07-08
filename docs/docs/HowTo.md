# How to Run

To run this project, you need to provide the analysis base configuration and log information at runtime. Their structure is as follows.

## Base Configuration

The base configuration defines the parameters required during the analysis process, including the time window for analysis and the specific settings for each module, as shown below:

### 🔧 Example Configuration (`config/RCanaylsis.yaml`)

    log_dir: /path/to/logs
    effect_time_window: 10
    display_results: true
    module_setting:
    perception:
        perc_score_threshold: 0.5
    prediction:
        prediction_window: 10
        pred_score_threshold: 0.1
    planning:
        planning_toleration_future_step: 5
        planning_toleration: 1


Explanation of Configuration Fields

### 📝 Explanation of Configuration Fields

- **`log_dir`**: Path to the input log directory.
- **`effect_time_window`**: Time window (in frames) to consider for root cause analysis.
- **`display_results`**: Whether display results on screen.

- **`module_setting`**:
    - **`perception.perc_score_threshold`**: Minimum confidence score for the perception module to consider a result valid.
    - **`prediction.prediction_window`**: Time horizon (in frames) used by the prediction module(If it differs from the settings of the running prediction module, the smaller value between the two will be used by default.).
    - **`prediction.pred_score_threshold`**: Confidence threshold for predictions to be considered reliable.
    - **`planning.planning_toleration_future_step`**: The planner allows a small tolerance for errors after a number of future steps.
    - **`planning.planning_toleration`**: Tolerance value for planning errors (in meters).

## Custom Configuration

If you need to set the analysis configurations, there are two ways to do so:

1. Directly modify the project's default configuration file. `{project}/ADSRootCauseAnalysis/config/RCanalysis.yaml`

2. (Recommended) Create a custom configuration file and specify it at runtime.

You can create a new configuration file with same format, and running with

    python main.py --config-path <your/file/path> --config-name <your/file/name>

## Input Data

The input data of ADS Root Cause Anaylsis is the running log of ADS, the details can be found in [Input Format](Input.md).


## Integration Supports

This project can be run as a standalone application or imported as a Python package for integration into other projects.

In summary, `RCHandler` wraps all core functionalities and enables standalone execution by importing and using this class directly. To run this package, you need to create a configuration file as an OmegaConf `DictConfig` and pass it as a parameter to initialize the `RCHandler`.

    from ADSRootCauseAnalysis import RCHandler
    from omegaconf import DictConfig
    from hydra import initialize, compose

    ... your code

    with initialize(config_path="ADSRootCauseAnaylsis/config"):
        cfg = compose(config_name="RCanaylsis")
        handler = RCHandler(cfg)

    ... follow code