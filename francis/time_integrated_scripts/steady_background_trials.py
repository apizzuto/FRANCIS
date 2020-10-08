#!/usr/bin/env python

'''
Script to generate ntrials number of background only test statistics and save 
information about each trial to outfile

@options: 
    --i index: alert event index
    --ntrials: number of trials to perform
'''
import os, time, sys, pickle, argparse
import numpy as np
import healpy as hp

from glob                       import glob
from skylab.ps_llh              import PointSourceLLH, MultiPointSourceLLH
from skylab.ps_injector         import PriorInjector
from skylab.llh_models          import EnergyLLH
from skylab.datasets            import Datasets
from skylab.utils               import dist
from skylab.priors              import SpatialPrior
import numpy.ma as ma
from skylab.sensitivity_utils   import estimate_sensitivity
from skylab.sensitivity_utils   import DeltaChiSquare
from astropy.io                 import fits

sys.path.append('/data/user/apizzuto/fast_response_skylab/alert_event_followup/FRANCIS/francis/time_integrated_scripts/')
from config_steady              import config

##################################### CONFIGURE ARGUMENTS #############################
parser = argparse.ArgumentParser(description = 'Alert event followup steady background')
parser.add_argument("--ntrials", default=1000, type=int,
                help="Number of trials (default=1000")
parser.add_argument('--i', type=int, required=True, help='Alert event index')
parser.add_argument('--rng', type=int, default=1, help="Random number seed")
parser.add_argument('--verbose', action='store_true', default=False,
                    help="Assorted print statements flag")
parser.add_argument('--smear', default=False, action='store_true',
                    help='Include systematics by smearing norm. prob.')
args = parser.parse_args()
#######################################################################################


index = args.i
ntrials = args.ntrials
seed = args.rng
verbose = args.verbose

smear_str = 'smeared/' if args.smear else 'norm_prob/'
outfile = '/data/user/apizzuto/fast_response_skylab/alert_event_followup/analysis_trials/bg/{}index_{}_steady_seed_{}.pkl'.format(smear_str, index, seed)

t0 = time.time()

nside = 2**7
multillh, spatial_prior = config(index, gamma = 2.0, seed = seed, scramble = True, nside=nside, 
                        ncpu = 1, injector = False, verbose=verbose, smear=args.smear)

t1 = time.time()
if verbose:
    print('{:.2f} seconds to Initialize Likelihoods'.format(t1 - t0))
    print ("\nRunning background only trials ...")

allspots = None
ii = 1
for results, hotspots in multillh.do_allsky_trials(n_iter= ntrials, 
                              injector=None,
                              #mean_signal=0, 
                              nside=nside, rng_seed = 123*seed + ii,
                              spatial_prior=spatial_prior,
                              follow_up_factor = 1):
    if verbose:
        print('Trial Number: {}'.format(ii))
    ii += 1
    if allspots is None:
        allspots = {}
        for k, v in hotspots['spatial_prior_0']['best'].items():
            allspots[k] = [v]
        if 'pix' not in allspots.keys():
            allspots['pix'] = [0]
        if 'nside' not in allspots.keys():
            allspots['nside'] = [0]
    else:
        for k, v in hotspots['spatial_prior_0']['best'].items():
            allspots[k].append(v)
        if 'pix' not in hotspots['spatial_prior_0']['best'].keys():
            allspots['pix'].append(0)
        if 'nside' not in hotspots['spatial_prior_0']['best'].keys():
            allspots['nside'].append(0)
    #allspots.append(hotspots)

dt1 = t1 - t0
dt     = time.time() - t0
if verbose:
    print("Finished script in {} seconds".format(dt))
    print("Initialization: {} seconds\ntrials: {} seconds".format(dt1, (dt-dt1)))

with open(outfile, 'w') as f:
    pickle.dump(allspots, f, protocol=pickle.HIGHEST_PROTOCOL)
