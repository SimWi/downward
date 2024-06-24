#! /usr/bin/env python

from pathlib import Path

import project

from lab.experiment import Experiment

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
    "unary_operators",
]

exp = Experiment()

project.fetch_algorithm(exp, "2024-06-23-hadd", "new:add")
project.fetch_algorithm(exp, "2024-06-23-hadd", "original:add")

project.add_absolute_report(
    exp, attributes=ATTRIBUTES, outfile="evaluation_satisficing_strips_considering_limitations.tex", format="tex", filter_domain=[
                    "airport", "barman-sat11-strips", "barman-sat14-strips", "blocks",
                    "childsnack-sat14-strips", "depot", "driverlog", "floortile-sat11-strips",
                    "floortile-sat14-strips", "freecell", "ged-sat14-strips", "grid", "gripper",
                    "hiking-sat14-strips", "logistics00", "logistics98", "miconic", "movie",
                    "mprime", "mystery", "nomystery-sat11-strips", "openstacks-sat08-strips", 
                    "openstacks-sat11-strips", "openstacks-sat14-strips", "openstacks-strips", 
                    "parcprinter-08-strips", "parcprinter-sat11-strips", "parking-sat11-strips", 
                    "parking-sat14-strips", "pathways", "pegsol-08-strips", "pegsol-sat11-strips", 
                    "pipesworld-notankage", "pipesworld-tankage", "psr-small", "rovers", "satellite", 
                    "scanalyzer-08-strips", "scanalyzer-sat11-strips", "sokoban-sat08-strips", 
                    "sokoban-sat11-strips", "storage", "thoughtful-sat14-strips", "tpp", 
                    "trucks-strips", "visitall-sat11-strips", "visitall-sat14-strips", "zenotravel"]
)

project.add_absolute_report(
    exp, attributes=ATTRIBUTES, outfile="evaluation_satisficing_strips_considering_limitations.html", filter_domain=[
                    "airport", "barman-sat11-strips", "barman-sat14-strips", "blocks",
                    "childsnack-sat14-strips", "depot", "driverlog", "floortile-sat11-strips",
                    "floortile-sat14-strips", "freecell", "ged-sat14-strips", "grid", "gripper",
                    "hiking-sat14-strips", "logistics00", "logistics98", "miconic", "movie",
                    "mprime", "mystery", "nomystery-sat11-strips", "openstacks-sat08-strips", 
                    "openstacks-sat11-strips", "openstacks-sat14-strips", "openstacks-strips", 
                    "parcprinter-08-strips", "parcprinter-sat11-strips", "parking-sat11-strips", 
                    "parking-sat14-strips", "pathways", "pegsol-08-strips", "pegsol-sat11-strips", 
                    "pipesworld-notankage", "pipesworld-tankage", "psr-small", "rovers", "satellite", 
                    "scanalyzer-08-strips", "scanalyzer-sat11-strips", "sokoban-sat08-strips", 
                    "sokoban-sat11-strips", "storage", "thoughtful-sat14-strips", "tpp", 
                    "trucks-strips", "visitall-sat11-strips", "visitall-sat14-strips", "zenotravel"]
)

project.add_absolute_report(
    exp, attributes=ATTRIBUTES, outfile="evaluation_satisficing_strips_considering_limitations_without_domains_with_different_h_values.tex", format="tex", filter_domain=[
                    "airport", "barman-sat11-strips", "barman-sat14-strips", "blocks",
                    "childsnack-sat14-strips", "depot", "driverlog", "floortile-sat11-strips",
                    "floortile-sat14-strips", "ged-sat14-strips", "grid", "gripper",
                    "hiking-sat14-strips", "logistics00", "logistics98", "miconic", "movie",
                    "mprime", "mystery", "nomystery-sat11-strips", "openstacks-sat08-strips", 
                    "openstacks-sat11-strips", "openstacks-sat14-strips", "openstacks-strips", 
                    "parcprinter-08-strips", "parcprinter-sat11-strips", "parking-sat11-strips", 
                    "parking-sat14-strips", "pathways", "pegsol-08-strips", "pegsol-sat11-strips", 
                    "pipesworld-notankage", "psr-small", "rovers", "satellite", "sokoban-sat08-strips", 
                    "sokoban-sat11-strips", "storage", "thoughtful-sat14-strips", "tpp", 
                    "trucks-strips", "visitall-sat11-strips", "visitall-sat14-strips", "zenotravel"]
)

project.add_absolute_report(
    exp, attributes=ATTRIBUTES, outfile="evaluation_satisficing_strips_considering_limitations_without_domains_with_different_h_values.html", filter_domain=[
                    "airport", "barman-sat11-strips", "barman-sat14-strips", "blocks",
                    "childsnack-sat14-strips", "depot", "driverlog", "floortile-sat11-strips",
                    "floortile-sat14-strips", "ged-sat14-strips", "grid", "gripper",
                    "hiking-sat14-strips", "logistics00", "logistics98", "miconic", "movie",
                    "mprime", "mystery", "nomystery-sat11-strips", "openstacks-sat08-strips", 
                    "openstacks-sat11-strips", "openstacks-sat14-strips", "openstacks-strips", 
                    "parcprinter-08-strips", "parcprinter-sat11-strips", "parking-sat11-strips", 
                    "parking-sat14-strips", "pathways", "pegsol-08-strips", "pegsol-sat11-strips", 
                    "pipesworld-notankage", "psr-small", "rovers", "satellite", "sokoban-sat08-strips", 
                    "sokoban-sat11-strips", "storage", "thoughtful-sat14-strips", "tpp", 
                    "trucks-strips", "visitall-sat11-strips", "visitall-sat14-strips", "zenotravel"]
)


attributes = ["unary_operators", "total_time", "planner_time", "search_time"]
pairs = [
    ("original", "new"),
]
suffix = "-rel" if project.RELATIVE else ""
for algo1, algo2 in pairs:
    for attr in attributes:
        exp.add_report(
            project.ScatterPlotReport(
                relative=project.RELATIVE,
                get_category=None if project.TEX else lambda run1, run2: run1["domain"],
                attributes=[attr],
                filter_domain=[
                    "airport", "barman-sat11-strips", "barman-sat14-strips", "blocks",
                    "childsnack-sat14-strips", "depot", "driverlog", "floortile-sat11-strips",
                    "floortile-sat14-strips", "freecell", "ged-sat14-strips", "grid", "gripper",
                    "hiking-sat14-strips", "logistics00", "logistics98", "miconic", "movie",
                    "mprime", "mystery", "nomystery-sat11-strips", "openstacks-sat08-strips", 
                    "openstacks-sat11-strips", "openstacks-sat14-strips", "openstacks-strips", 
                    "parcprinter-08-strips", "parcprinter-sat11-strips", "parking-sat11-strips", 
                    "parking-sat14-strips", "pathways", "pegsol-08-strips", "pegsol-sat11-strips", 
                    "pipesworld-notankage", "pipesworld-tankage", "psr-small", "rovers", "satellite", 
                    "scanalyzer-08-strips", "scanalyzer-sat11-strips", "sokoban-sat08-strips", 
                    "sokoban-sat11-strips", "storage", "thoughtful-sat14-strips", "tpp", 
                    "trucks-strips", "visitall-sat11-strips", "visitall-sat14-strips", "zenotravel"],
                format="tex" if project.TEX else "png",
            ),
            name=f"{algo1}-vs-{algo2}--{attr}{suffix}",
        )



exp.run_steps()
