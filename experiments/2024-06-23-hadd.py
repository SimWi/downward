#! /usr/bin/env python

import os
import shutil

import custom_parser
import project

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
SCP_LOGIN = ""
REMOTE_REPOS_DIR = "/infai/wittne0000/projects"
# If REVISION_CACHE is None, the default "./data/revision-cache/" is used.
REVISION_CACHE = None
if project.REMOTE:
    SUITE = project.SUITE_SATISFICING_STRIPS
    ENV = project.BaselSlurmEnvironment(partition="infai_2")
else:
    SUITE = ["depot:p01.pddl", "grid:prob01.pddl", "gripper:prob01.pddl"]
    ENV = project.LocalEnvironment(processes=2)

CONFIGS = [
    ("add", ["--search", "eager_greedy([add()])"])
]
BUILD_OPTIONS = []
DRIVER_OPTIONS = []
REV_NICKS = [
    ("730f313", "new"),
    ("61646d7", "original"),
]
ATTRIBUTES = [
    "error",
    "run_dir",
    "search_start_time",
    "search_start_memory",
    "search_time",
    "total_time",
    "planner_time",
    "initial_h_value",
    "h_values",
    "coverage",
    "cost",
    "expansions",
    "evaluations",
    "memory",
    "unary_operators"
]

exp = project.FastDownwardExperiment(environment=ENV, revision_cache=REVISION_CACHE)
for config_nick, config in CONFIGS:
    for rev, rev_nick in REV_NICKS:
        algo_name = f"{rev_nick}:{config_nick}" if rev_nick else config_nick
        exp.add_algorithm(
            algo_name,
            REPO,
            rev,
            config,
            build_options=BUILD_OPTIONS,
            driver_options=DRIVER_OPTIONS,
        )
exp.add_suite(BENCHMARKS_DIR, SUITE)

exp.add_parser(exp.EXITCODE_PARSER)
exp.add_parser(exp.TRANSLATOR_PARSER)
exp.add_parser(exp.SINGLE_SEARCH_PARSER)
exp.add_parser(custom_parser.get_parser())
exp.add_parser(exp.PLANNER_PARSER)

exp.add_step("build", exp.build)
exp.add_step("start", exp.start_runs)
exp.add_step("parse", exp.parse)
exp.add_fetcher(name="fetch")

project.add_absolute_report(exp, attributes=ATTRIBUTES, outfile="evaluation_satisficing_strips_all_benchmarks.html")

exp.run_steps()
