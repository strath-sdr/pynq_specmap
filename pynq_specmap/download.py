__author__ = "David Northcote"
__organisation__ = "The Univeristy of Strathclyde"
__support__ = "https://github.com/strath-sdr/pynq_spectrum_map"

import requests
import json
import datetime
import pathlib
import os
import time
import pickle
import pandas as pd

from pynq_specmap import plots
from pynq_specmap import utilities


SPECTRUM_UK_URL = "http://static.ofcom.org.uk/static/spectrum/data/spectrumMapping.json"


def download_bands(url='', region='uk'):
    """Download the spectrum based on URL and
    region arguments. If no URL is given, only
    download OFCOM Spectrum Map for the UK.
    
    """
    if url == '':
        url = SPECTRUM_UK_URL
    req = requests.get(url, allow_redirects=True)
    now = datetime.datetime.now()
    pathlib.Path('spectrum').mkdir(parents=True, exist_ok=True)
    open(''.join(['spectrum/', \
                  'spectrum_', \
                  region, now.strftime('_%Y%m%d_%H%M%S'), \
                  '.json']), 'wb').write(req.content)
    time.sleep(1)
    
    
def get_bands_filename(region='', date=None, time=None):
    """Return the filenames from past spectrum
    downloads. Filenames can be filtered using
    the region, date, and time arguments.
    
    """
    if date is None:
        date = [0, 4294967295]
    if time is None:
        time = [0, 240000]
    spectrum_filenames = []
    filenames = os.listdir('spectrum')
    for filename in filenames:
        filename_text = filename.split('_')
        if 'spectrum' in filename_text:
            r = filename_text[1]
            d = int(filename_text[2])
            t = int(filename_text[3].split('.')[0])
            if (t >= time[0]) and (t <= time[1]) \
            and (d >= date[0]) and (d <= date[1]):
                if region == '':
                    spectrum_filenames.append(filename)
                elif (r == region):
                    spectrum_filenames.append(filename)
                    
    return sorted(spectrum_filenames)


def refresh_bands_object(filename='', region='', filter_callback=None):
    """Refreshes the spectrum map object using
    a previously downloaded spectrum json file.
    The user can specify the exact json file using
    the filename argument.
    
    """
    spectrum_filenames = get_bands_filename(region)
    if filename == '':
        if spectrum_filenames:
            filename = spectrum_filenames[-1]
        else:
            raise RuntimeError('No spectrum map files exist.')
    elif filename not in spectrum_filenames:
        raise ValueError(''.join(['File named ', filename, ' does not exist.']))
    with open(''.join(['spectrum/',filename])) as json_file:
        json_dict = json.load(json_file)
        bands = pd.DataFrame(json_dict['bands'])
    if filter_callback is not None:
        bands = filter_callback(bands)
    bands = add_fcutoff_unique_id(bands)
    bands['bandwidth'] = bands.uf-bands.lf
    bands = plots.initialise_traces_opt(bands)
    bands.to_pickle('spectrum/bands.pkl')
        
    return bands


def add_fcutoff_unique_id(bands):
    """Returns the input dataframe
    with the frequency cutoff values applied
    to the unique name value.
    
    """
    for index, band in bands.iterrows():
        fcutoff_string = utilities.generate_band_cutoff_string(band)
        bands.at[index, 'u'] = ''.join([fcutoff_string, ' — ', band.u])
    
    return bands
    

def retrieve_bands_object():
    """Retrieves the spectrum map object using
    the most recently configured spectrum
    object. Use refresh_spectrum_object to
    update the spectrum map object.
    
    """
    if os.path.isfile('spectrum/bands.pkl'):
        bands = pd.read_pickle('spectrum/bands.pkl')
    else:
        raise RuntimeError('No bands object exists.')
        
    return bands
    