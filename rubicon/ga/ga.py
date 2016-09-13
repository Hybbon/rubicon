from enum import Enum
from collections import namedtuple
import numpy as np
import rubikscube as rc

Record = namedtuple('Record', ('min', 'max', 'mean', 'std'))

def stats_record(entries):
    return Record(min=min(entries), max=max(entries),
                  mean=np.mean(entries), std=np.std(entries))


def count_repeated(pop):
    repeated = [False] * len(pop)
    for i, ind in enumerate(pop):
        if repeated[i]:
            continue
        for j, other_ind in enumerate(pop):
            if i != j and not repeated[j]:
                if ind == other_ind:
                    repeated[j] = True
    return sum(repeated)


def count_improved(prev_fitnesses, fitnesses):
    return sum(fitnesses < prev_fitnesses)


def run_ga(pop, generations, toolkit, verbose=True):
    """Runs a genetic algorithm.

    Parameters:
    - pop: initial population
    - generations: number of generations the GA should run for
    - toolkit: ga.Toolkit which implements select, best, vary operators
               and a fitness function."""
    fitnesses = np.array(list(toolkit.map(toolkit.fitness, pop)))
    stats = {key: list() for key in ("fitness", "size", "improved", "same")}

    for gen in range(generations):
        fit_and_pop = list(zip(fitnesses, pop))
        fit_and_offspring = toolkit.select(fit_and_pop)
        best = toolkit.best(fit_and_pop)

        _, offspring = zip(*fit_and_offspring)

        if best:
            _, best = zip(*best)
        else:
            best = tuple()

        offspring = toolkit.vary(offspring)

        pop = offspring + list(best)

        prev_fitnesses = fitnesses
        fitnesses = np.array(list(toolkit.map(toolkit.fitness, pop)))
        sizes = [len(ind) for ind in pop]


        fit_stats = stats_record(fitnesses)
        size_stats = stats_record(sizes)
        same = count_repeated(pop)
        improved = count_improved(prev_fitnesses, fitnesses)

        log_fmt = "{}\tMin: {}, Avg: {}, Avg size: {}, Same: {}, Improved: {}"
        if verbose:
            print(log_fmt.format(gen, fit_stats.min, fit_stats.mean,
                                 size_stats.mean, same, improved))

        stats['fitness'].append(fit_stats)
        stats['size'].append(size_stats)
        stats['same'].append(same)
        stats['improved'].append(improved)

    fit_and_pop = list(zip(fitnesses, pop))
    return fit_and_pop, stats


def group_by_key(list_of_maps):
    keys = list_of_maps[0].keys()
    return {key: [m[key] for m in list_of_maps]
            for key in keys}


SummaryRecord = namedtuple('SummaryRecord', ['min_mins', 'mean_mins', 'std_mins', 'mean_maxes',
                                             'min_means', 'mean_means', 'std_means', 'mean_stds'])

def summarize_stats(run_stats):
    summary = {key: list() for key in ('fitness', 'size', 'same', 'improved')}
    multi_stats = {'fitness', 'size'}
    for stat_name, stat_by_run in group_by_key(run_stats).items():
        for gen_stats in zip(*stat_by_run):
            if stat_name in multi_stats:
                mins, maxes, means, stds = zip(*gen_stats)
                kwargs = {
                    'min_mins': min(mins),
                    'mean_mins': np.mean(mins),
                    'std_mins': np.std(mins),
                    'mean_maxes': np.mean(maxes),
                    'min_means': min(means),
                    'mean_means': np.mean(means),
                    'std_means': np.std(means),
                    'mean_stds': np.mean(stds)
                }
                summary_record = SummaryRecord(**kwargs)
                summary[stat_name].append(summary_record)
            else:
                record = Record(min=min(gen_stats), max=max(gen_stats),
                                mean=np.mean(gen_stats), std=np.std(gen_stats))
                summary[stat_name].append(record)
    return summary
