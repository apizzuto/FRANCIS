#!/usr/bin/env python

import os, sys, time, pickle
import numpy as np
from francis.universe.universe_analysis import UniverseAnalysis
import argparse

parser = argparse.ArgumentParser(description='Calculate TS distributions')
parser.add_argument('--n', type=int, default=1000,
                        help = 'Number of trials')
parser.add_argument('--density', type=float, default=1e-9,
                        help = 'Local source density')
parser.add_argument('--LF', type=str, default='SC', help ='luminosity function')
parser.add_argument('--evol', type=str, default='MD2014SFR', help='Evolution')
parser.add_argument('--manual_lumi', type=float, default=0.0, help='Manually enter luminosity')
args = parser.parse_args()

TS = []
TS_gold = []
ps = []
ps_gold = []

density = args.density
evol = args.evol
lumi = args.LF
data_years = 9.6
print("STARTING INITIALIZATION")

uni = UniverseAnalysis(lumi, evol, density, 1.5e-8, 2.50, 
        data_years=data_years, manual_lumi=args.manual_lumi)
uni.print_analysis_info()
uni.make_alerts_dataframe()
print('Running trials . . . ')
TS.append(uni.calculate_ts())
TS_gold.append(uni.calculate_ts(only_gold = True))
ps.append(uni.calculate_binomial_pvalue(only_gold=False))
ps_gold.append(uni.calculate_binomial_pvalue(only_gold=True))
print("  Trials completed: ")

for jj in range(args.n - 1):
    print('    {}'.format(jj+1))
    uni.reinitialize_universe()
    uni.make_alerts_dataframe()
    TS.append(uni.calculate_ts(only_gold = False))
    TS_gold.append(uni.calculate_ts(only_gold = True))
    ps.append(uni.calculate_binomial_pvalue(only_gold=False))
    ps_gold.append(uni.calculate_binomial_pvalue(only_gold=True))

TS = np.array([TS, TS_gold, ps, ps_gold])
lumi_str = '_manual_lumi_{:.1e}'.format(args.manual_lumi) if args.manual_lumi != 0.0 else ''
np.save('/data/user/apizzuto/fast_response_skylab/alert_event_followup/ts_distributions/ts_dists_{}year_density_{:.2e}_evol_{}_lumi_{}{}_steady.npy'.format(data_years, density, evol, lumi, lumi_str), TS)
