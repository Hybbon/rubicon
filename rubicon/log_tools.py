import os
import sys
import pprint
import pickle

from collections import namedtuple
from functools import partial

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

import rubikscube as rc

def print_run_stats(stats, file=sys.stdout):
    record_fmt = "{min} to {max} (mean {mean}, std {std})"
    row_fmt = "{gen}\tFit: {fit}/Size: {size}/Same: {same}, Improved: {improved}"

    stat_lists = (stats['fitness'], stats['size'], stats['same'], stats['improved'])
    for i, (fit_record, size_record, same, improved) in enumerate(zip(*stat_lists)):
        fit_str = record_fmt.format(**fit_record._asdict())
        size_str = record_fmt.format(**size_record._asdict())
        row = row_fmt.format(gen=i, fit=fit_str, size=size_str, same=same,
                             improved=improved)
        print(row, file=file)


def plot_records(path, records, multi=False):
    if multi:
        columns = ["min", "max", "mean", "std"]
        f = pd.DataFrame.from_records(records, columns=columns)
        f.plot()
    else:
        plt.plot(range(len(records)), records)
    plt.savefig(path)
    plt.clf()



def log_stats(stats, run_dir, file=sys.stdout):
    print_run_stats(stats, file=file)
    multi_stats = {'fitness', 'size'}

    for stat_name, records in stats.items():
        filename = "{}.pdf".format(stat_name)
        path = os.path.join(run_dir, filename)
        plot_records(path, records, multi=stat_name in multi_stats)



def log_run(run_dir, config, stats, duration):
    log_file_path = os.path.join(run_dir, "run.log")
    with open(log_file_path, "a") as f:
        pp = pprint.PrettyPrinter(stream=f, indent=4)
        log = partial(print, file=f)

        header_fmt = """RUBIK'S CUBE GA RUN LOG

        This run took {duration}s to finish\n"""
        log(header_fmt.format(duration=duration))
        log("Configuration:")
        pp.pprint(config)
        log("\nRun stats:")
        log_stats(stats, run_dir, file=f)


def log_multi_run(all_runs_dir, config, summary, duration):
    log_file_path = os.path.join(all_runs_dir, "all_runs.log")
    with open(log_file_path, "a") as f:
        pp = pprint.PrettyPrinter(stream=f, indent=4)
        log = partial(print, file=f)

        header_fmt = """RUBIK'S CUBE GA MULTI RUN LOG

        All {runs} runs combined took {duration}s to finish\n"""
        log(header_fmt.format(runs=config['Runs'], duration=duration))
        log("Configuration:")
        pp.pprint(config)
        log("\nRun stat summary:")
        log_stats(summary, all_runs_dir, file=f)


Individuals = namedtuple("Individuals", ["best", "pop"])


def log_individuals(run_dir, best, pop, best_cube):
    pickle_path = os.path.join(run_dir, "individuals.pickle")
    with open(pickle_path, "wb") as f:
        pickle.dump(Individuals(best=best, pop=pop), f)

    log_path = os.path.join(run_dir, "individuals.log")
    with open(log_path, "w") as f:
        log = partial(print, file=f)
        log("INDIVIDUALS LOG")
        log("Best individual:", best)
        log("Cube generated by the best individual:")
        rc.print_3d_cube(best_cube, file=f)

        log("\nAll individuals:")
        for i, ind in enumerate(pop):
            log(i, ind)

