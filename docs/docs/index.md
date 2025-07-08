# ADS Root Cause Analysis

Here is the documents of project ADS Root Cause Analysis. This project is based on [MoDitector: Module-Directed Testing for Autonomous Driving Systems](https://dl.acm.org/doi/10.1145/3728876)

This project aims to build a framework to analyze the ADS running logs, to figure out which module should be responded to the failure of running.

## Installation

Clone the repo from github by

    git clone https://github.com/Shanicky-RenzhiWang/ADSRootCauseAnaylsis.git

Install the requirements

    cd ADSRootCauseAnaylsis
    pip install -r requirements


## Quick Start

Once the installation completed, the project is already usable.

The details for running can be found in the **How to Run** label. 

We provide examples for running, download it by

    bash get_data.sh

Then execute

    python main.py log_dir=examples/example_collision

to run the first example.
