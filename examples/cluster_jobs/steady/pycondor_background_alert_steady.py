import pycondor, argparse, sys, os
from glob import glob
import numpy as np
import pandas as pd
import francis.utils as utils
f_path = utils.get_francis_path()

error = '/scratch/apizzuto/fast_response/condor/error'
output = '/scratch/apizzuto/fast_response/condor/output'
log = '/scratch/apizzuto/fast_response/condor/log'
submit = '/scratch/apizzuto/fast_response/condor/submit'

job = pycondor.Job('background_fastresponse_alerts_steady',
    f_path + 'time_integrated_scripts/steady_background_trials.py',
    error=error,
    output=output,
    log=log,
    submit=submit,
    getenv=True,
    universe='vanilla',
    verbose=2, 
    request_memory=8000,
    #request_cpus=5,
    extra_lines= ['should_transfer_files = YES', 'when_to_transfer_output = ON_EXIT', 'Requirements =  (Machine != "node128.icecube.wisc.edu")']
    )

sky_files = glob('/data/ana/realtime/alert_catalog_v2/fits_files/Run1*.fits.gz')

for rng in range(5):
    for index in range(len(sky_files)):
        for smear in [' --smear']:
            job.add_arg('--rng={} --i={} --ntrials=200{}'.format(rng, index, smear))

dagman = pycondor.Dagman('alert_event_fra_background_steady', submit=submit, verbose=2)
dagman.add_job(job)
dagman.build_submit()
