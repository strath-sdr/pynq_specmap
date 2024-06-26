__author__ = "David Northcote, Graeme Fitzpatrick"
__organisation__ = "The Univeristy of Strathclyde"
__support__ = "https://github.com/strath-sdr/pynq_spectrum_map"

import pandas as pd

from pynq_specmap import plots
from pynq_specmap import utilities


def filter_bands(bands, lf=[], s=[], u=[], uf=[], \
                 v=[], include=True):
    """Returns a filtered dataframe based on the
    input filtering requirements.
    
    lf, s, u, uf, and v are all lists containing
    filtering terms. The include argument should
    be used to return the filtering terms in the
    filtered dataframe, or remove the filtering
    terms from the input dataframe and return.
    
    """
    series = (bands.lf.isin(lf)) | \
             (bands.s.isin(s)) | \
             (bands.u.isin(u)) | \
             (bands.uf.isin(uf)) | \
             (bands.v.isin(v))
    if not include:
        series = ~series
        
    return bands[series]


def filter_bands_range(bands, lf=None, uf=None):
    """Returns a filtered dataframe of the input
    dataframe by only selecting bands in the
    given lower and upper frequency range.
    
    lf and uf are used to indicate the minimum
    and maximum frequencies to be selected. If
    these arguments are not entered, the minimum
    and maximum frequencies of the given bands
    are used instead.
    
    """
    if lf is None:
        lf = bands.lf.min()
    if uf is None:
        uf = bands.uf.max()
    bands = bands[(bands.lf >= lf) & \
                  (bands.uf <= uf)]
    
    return bands


def filter_bands_bandwidth(bands, lbw=None, ubw=None):
    """Returns a filtered dataframe of the input
    dataframe by only selecting bands in the
    given lower and upper frequency range.
    
    lbw and ubw are used to indicate the minimum
    and maximum frequencies to be selected. If
    these arguments are note entered, the minimum
    and maximum bandwidths of the given bands are
    used instead
    
    """
    if lbw is None:
        lbw = bands.bandwidth.min()
    if ubw is None:
        ubw = bands.bandwidth.max()
    bands = bands[(bands.bandwidth >= lbw) & \
                  (bands.bandwidth <= ubw)]
    
    return bands


def get_bands_unique_values(bands, key=None):
    """Returns a dictionary of unique values within
    the given pandas dataframe. The dictionary keys
    are the column names of the pandas dataframe
    and the values are lists of unique values.
    
    The key argument allows only a specific
    column to be searched for unique values to
    improve processing time.
    
    """
    unique_values = {}
    if key is None:
        for column in bands:
            if column == 'trace':
                pass
            else:
                unique_values[column] = \
                list(getattr(bands, column).unique())
    else:
        if key == 'trace':
            raise ValueError('Key cannot be trace.')
        unique_values[key] = \
        list(getattr(bands, key).unique())
            
    return unique_values


def set_bands_values(bands, key=None, oldvalue=None, \
                     newvalue=None):
    """Returns the given dataframe
    with values set using a key, and old value
    to search for, and a new value to replace
    the old value.
    
    key should be used to select the dataframe
    column. oldvalue indicates the search term
    to be changed. newvalue is the value to
    replace the oldvalue in the dataframe.
    
    """
    if key is None or \
        oldvalue is None or \
        newvalue is None:
        raise ValueError( \
        'Please initialise all arguments with a value.')
    bands.loc[bands[key] == oldvalue, key] \
    = newvalue
    
    return bands    


def merge_bands_threshold(bands, threshold=0, unique=False):
    """Returns a copy of the input dataframe where
    bands have been merged based on their proximity to
    one another.
    
    Use the threshold argument to modify the distance
    required to merge two bands. Use the unique argument
    to only merge bands with the same unique name that
    are in proximity to one another.
    
    """
    sectors = get_bands_unique_values(bands, key='s')
    temp_bands = []
    bands_copy = utilities.deep_copy_bands(bands)
    if threshold < 0:
        raise ValueError('Threshold must be more than or equal to 0.')
    for sector in sectors['s']:
        uf, lf = 0, 0
        u, s = '', ''
        series = bands_copy['s'].values == sector
        sector_bands = bands_copy[series]
        for index, band in sector_bands.iterrows():
            if band['lf'] < lf:
                raise RuntimeError(''.join(['Band merge error! Band index', str(index)]))
            else:
                if (uf + threshold) >= band['lf'] and \
                (not unique or (u == band['u'])):
                    if temp_bands:
                        old_band = temp_bands.pop()
                        if band['uf'] >= old_band['uf']:
                            old_band['uf'] = band['uf']
                        if (not unique):
                            old_band['u'] = ''.join([old_band['u'], '<br>', band['u']])
                        temp_bands.append(old_band)
                        uf, lf = old_band['uf'], old_band['lf']
                    else:
                        temp_bands.append(band)
                        uf, lf = band['uf'], band['lf']
                else:
                    temp_bands.append(band)
                    uf, lf = band['uf'], band['lf']
            u, s = band['u'], band['s']
        new_bands = pd.DataFrame(temp_bands)
        new_bands['bandwidth'] = new_bands.uf - new_bands.lf
    return plots.update_traces(new_bands)                 


def delete_bands_duplicate(bands): #GF
    """Returns the input dataframe with duplicates
    removed from the lf, uf, s, u, and v columns.
    This function ignores the trace column as it
    is not required to recognise duplicate bands.
    
    """
    series = ~bands.duplicated(['lf','uf','s','u','v'])
    return bands[series]
