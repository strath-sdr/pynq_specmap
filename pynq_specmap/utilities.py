__author__ = "David Northcote"
__organisation__ = "The Univeristy of Strathclyde"
__support__ = "https://github.com/strath-sdr/pynq_spectrum_map"

import copy


def generate_band_cutoff_string(band):
    """Returns a string containing frequency
    cutoff information for traces.
    
    """    
    if band['lf'] >= 1e9:
        l_units = 'GHz'
        l_div_factor = 1e9
    elif (band['lf'] >= 1e6) and (band['lf'] < 1e9):
        l_units = 'MHz'
        l_div_factor = 1e6
    elif (band['lf'] >= 1e3) and (band['lf'] < 1e6):
        l_units = 'kHz'
        l_div_factor = 1e3
    else:
        l_units = 'Hz'
        l_div_factor = 1
    if band['uf'] >= 1e9:
        u_units = 'GHz'
        u_div_factor = 1e9
    elif (band['uf'] >= 1e6) and (band['uf'] < 1e9):
        u_units = 'MHz'
        u_div_factor = 1e6
    elif (band['uf'] >= 1e3) and (band['uf'] < 1e6):
        u_units = 'kHz'
        u_div_factor = 1e3
    else:
        u_units = 'Hz'
        u_div_factor = 1
    fcutoff_string = ''.join([str(band['lf']/l_div_factor),
                              ' ', l_units,
                              ' to ',
                              str(band['uf']/u_div_factor),
                              ' ', u_units])
    
    return fcutoff_string


def deep_copy_bands(bands):
    """Perform a deep copy of the bands
    dataframe.
    
    """

    bands_copy = bands.copy(deep=True)
    trace_list = []
    for trace in bands['trace']:
        trace_list.append(trace)
    bands_copy['trace'] = copy.deepcopy(trace_list)
    
    return bands_copy
