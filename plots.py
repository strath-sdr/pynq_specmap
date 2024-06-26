__author__ = "David Northcote"
__organisation__ = "The Univeristy of Strathclyde"
__support__ = "https://github.com/strath-sdr/pynq_spectrum_map"

import plotly.graph_objs as go
import pandas as pd
import copy

from pynq_specmap import filters

import plotly.io as pio
pio.renderers.default ='jupyterlab'


COLOURS = {'' : 'rgba(51, 102, 255, 0.2)',
           'Aeronautical' : 'rgba(252, 148, 3, 0.2)',
           'Amateur' : 'rgba(252, 0, 160, 0.2)',
           'Broadcasting' : 'rgba(3, 252, 53, 0.2)',
           'Business Radio' : 'rgba(3, 69, 252, 0.2)',
           'Fixed Links' : 'rgba(11, 3, 252, 0.2)',
           'Licence exempt' : 'rgba(240, 200, 80, 0.2)',
           'Maritime' : 'rgba(51, 102, 255, 0.2)',
           'Mobile and Wireless Broadband' : 'rgba(182, 3, 252, 0.2)',
           'Wireless Broadband' : 'rgba(182,3,252,0.2)',
           'Mobile' : 'rgba(182,3,252,0.2)',
           'N/A' : 'rgba(51, 102, 255, 0.2)',
           'PMSE' : 'rgba(107, 3, 252, 0.2)',
           'Public sector' : 'rgba(252, 32, 3, 0.2)',
           'Satellite' : 'rgba(252, 3, 252, 0.2)',
           'Space Science' : 'rgba(3, 252, 227, 0.2)'}

COLOURS_OPAQUE = {'' : 'rgba(51, 102, 255, 1)',
                  'Aeronautical' : 'rgba(252, 148, 3, 1)',
                  'Amateur' : 'rgba(252, 0, 160, 1)',
                  'Broadcasting' : 'rgba(3, 252, 53, 1)',
                  'Business Radio' : 'rgba(3, 69, 252, 1)',
                  'Fixed Links' : 'rgba(11, 3, 252, 1)',
                  'Licence exempt' : 'rgba(240, 200, 80, 1)',
                  'Maritime' : 'rgba(51, 102, 255, 1)',
                  'Mobile and Wireless Broadband' : 'rgba(182, 3, 252, 1)',   
                  'Mobile' : 'rgba(182,3,252,0.2)',
                  'Wireless Broadband' : 'rgba(182,3,252,0.2)',
                  'N/A' : 'rgba(51, 102, 255, 1)',
                  'PMSE' : 'rgba(107, 3, 252, 1)',
                  'Public sector' : 'rgba(252, 32, 3, 1)',
                  'Satellite' : 'rgba(252, 3, 252, 1)',
                  'Space Science' : 'rgba(3, 252, 227, 1)'}


def initialise_plot(layout={}, template='plotly'):
    """Initialise the plotly graph object
    figurewidget with a given layout.
    
    """
    if layout:
        plot = go.FigureWidget(layout=layout)
    else:
        plot = go.FigureWidget(layout={
                                 'template' : template,
                                 'hoverlabel' : {
                                     'font_size' : 12,
                                 },
                                 'xaxis' : {
                                     'title' : 'Frequency (Hz)',
                                     'range' : [0, 4096e6],
                                     'rangemode' : 'tozero',
                                     'autorange' : False
                                 },
                                 'yaxis' : {
                                     'title' : 'Magnitude',
                                     'autorange' : True
                                 },
                                 'margin' : {
                                     't' : 25,
                                     'b' : 25,
                                     'l' : 25,
                                     'r' : 25
                                 },
                                 'showlegend' : False,
                             })
        
    return plot


def initialise_traces_opt(bands=pd.DataFrame()):
    """Initialise each band with plotly
    scatter objects. Adds a trace column
    to the dataframe containing go.Scatter
    json string for adding to a plot.
    
    """
    traces = []
    trace = go.Scatter(
        x=[0, 0, 0, 0],
        y=[-300, 0, 0, -300],
        fill='toself',
        fillcolor='rgb(51, 102, 255)',
        hoveron='points+fills',
        mode='lines',
        line={
            'width' : 2,
            'color' : 'rgb(51, 102, 255)'},
        name='',
        ids=[''],
        hovertemplate="<extra></extra>",
    )
    trace_json = trace.to_plotly_json()
    for index, band in bands.iterrows():
        temp_json = copy.deepcopy(trace_json)
        temp_json.update({'x' : [band['lf'], band['lf'], band['uf'], band['uf']],
                          'name' : ''.join(['<b>',band['s'],'</b><br>',band['u']]),
                          'fillcolor' : COLOURS[band['s']],
                          'line' : {
                              'width' : 2,
                              'color' : COLOURS[band['s']],
                          },
                          'ids' : [band['s']],
                         })
        traces.append(temp_json)
    bands['trace'] = traces
    
    return bands


def update_traces(bands):
    """Returns a dataframe with the trace
    information updated using the given
    band upper and lower frequencies.
    
    Modifies the x position of the trace
    and the name.
    
    """
    sectors = filters.get_bands_unique_values(bands, key='s')
    for index, sector in enumerate(sectors['s']):
        series = bands['s'].values == sector
        sector_bands = bands[series]
        for _, band in sector_bands.iterrows():
            trace = band['trace']
            trace.update({'x' : [band['lf'], band['lf'], band['uf'], band['uf']],
                          'name' : ''.join(['<b>',band['s'],'</b><br>',band['u']]),
                         })
    
    return bands


def batch_add_traces(plot, traces):
    """Updates the given plot with traces.
    Batch update so all changes are performed
    in one transaction between host and client.
    
    """
    with plot.batch_update():
        plot.add_traces(traces)
        
        
def add_overlay_trace(plot):
    """Adds the overlay trace, which indicates
    the active spectrum band.
    
    """
    overlay_trace = go.Scatter(
        x=[0, 0, 0, 0],
        y=[-300, 0, 0, -300],
        fill='toself',
        fillcolor='rgba(0, 0, 0, 0)',
        hoveron='points+fills',
        mode='lines',
        line={
            'width' : 0,
            'color' : 'rgba(0, 0, 0, 0)'},
        name='',
        ids=['Overlay Trace'],
        hovertemplate="<extra></extra>",
    )
            
    plot.add_trace(overlay_trace)
        
        
def update_overlay_trace(plot, s, u, lf, uf):
    """Updates the overlay trace, which indicates
    the active spectrum band.
    
    """
    for trace in plot.data:
        if trace.ids is not None:
            if 'Overlay Trace' in trace.ids:
                with plot.batch_update():
                    trace.x = [lf, lf, uf, uf]
                    trace.line={
                        'width' : 2,
                        'color' : COLOURS_OPAQUE[s]}
                    trace.name=''.join(['<b>',s,'</b><br>',u])
                    trace.ids=[s, 'Overlay Trace']
                
                
def reset_overlay_trace(plot):
    """Resets the overlay trace to be used
    again later.
    
    """
    for trace in plot.data:
        if 'Overlay Trace' in trace.ids:
            trace.x = [0, 0, 0, 0]
            trace.fillcolor = 'rgba(0, 0, 0, 0)'
            trace.line = {'width' : 0,
                          'color' : 'rgba(0, 0, 0, 0)'}
            trace.name=''
            trace.ids=['Overlay Trace']
