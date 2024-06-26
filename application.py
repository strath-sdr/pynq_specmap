__author1__ = 'David Northcote'
__author2__ = 'Graeme Fitzpatrick'
__organisation__ = 'The University of Strathclyde'
__date__ = '10th September 2021'
__version_name__ = '<a href="https://www.google.com/search?q=Brig+O%27+Doon" target="_blank" rel="noopener noreferrer">Brig O` Doon</a>'
__version_number__ = '0.1.0'
__release__ = 'Release'
__info__ = 'Spectrum Mapping Tool'
__support__ = '<a href="https://github.com/strath-sdr/pynq_spectrum_map" target="_blank" rel="noopener noreferrer">https://github.com/strath-sdr/pynq_spectrum_map</a>'

about = ''.join(['<br><b>', __info__, '</b><br>',
                ' ', __release__, '<br>', 'Version ', __version_number__,
                ': ', __version_name__, '<br>Date: ', __date__, '<br><br>',
                '<b>Organisation:</b> <br>', __organisation__,
                '<br><br>', '<b>Support</b>:<br>', __support__])

import ipywidgets as ipw
import os
import plotly.graph_objs as go

from pynq_specmap import filters
from pynq_specmap import plots


select_dict = {}


def spectrum_map_tool(bands, merge=True, threshold=0, unique=False, template='plotly'):
    """Returns the spectrum mapping tool
    application.
    
    """
    
    def on_value_change_sector(change):
        """Callback for the spectrum sector
        dropdown widget.
        
        """
        
        sector = change['new']
        old_sector = change['old']
        traces_reference = []
        for trace in plot.data:
            if old_sector not in trace.ids:
                traces_reference.append(trace)
        plot.data = traces_reference
        filtered_bands_merged = filters.filter_bands(bands_merged, s=[sector])
        plot.layout.xaxis.range = (0, 4096e6)
        band_select.unobserve(on_click_band, names='index')
        u_range, u_name = [], []
        for index in range(len(select_dict[sector]['u'])):
            u = select_dict[sector]['u'][index]
            u_strings = u.split(' — ')
            u_range.append(u_strings[0])
            u_name.append(u_strings[1])
        band_select.options = u_name
        band_select_alt.options = u_range
        band_select.value = None
        band_select.rows = len(select_dict[sector]['u'])
        band_select_alt.rows = len(select_dict[sector]['u'])
        band_select.observe(on_click_band, names='index')
        traces = filtered_bands_merged.trace.tolist()
        plots.batch_add_traces(plot, traces)
        plots.add_overlay_trace(plot)
        
    def on_click_band(change):
        """Callback for the band selector
        widget.
        
        """
        
        sector = sector_dropdown.value
        index = change['owner'].index
        if index is not None:
            u = select_dict[sector]['u'][index]
            u_range, u_name = u.split(' — ')
            band_to_display = bands_merged[
                bands_merged['u'].str.contains(u, na=False, regex=False)]
            if len(band_to_display) != 1:
                raise RuntimeError(''.join(['Could not display band ', u]))
            if not merge:
                lf = select_dict[sector]['lf'][index]
                uf = select_dict[sector]['uf'][index]
                bw = select_dict[sector]['bw'][index]
            else:
                lf = band_to_display['lf'].tolist()[0]
                uf = band_to_display['uf'].tolist()[0]
                bw = band_to_display['bandwidth'].tolist()[0]
            plots.update_overlay_trace(plot=plot, s=sector, u=select_dict[sector]['u'][index],
                                       lf=select_dict[sector]['lf'][index],
                                       uf=select_dict[sector]['uf'][index])
            plot.layout.xaxis.range = (lf-bw*2, uf+bw*2)
            
    def on_button_click(change):
        """Callback for the reset button
        widget.
        
        """
        band_select.unobserve(on_click_band, names='index')
        band_select.value = None
        plot.layout.xaxis.range = (0, 4096e6)
        plots.reset_overlay_trace(plot)
        band_select.observe(on_click_band, names='index')
        
    global select_dict
    plot = plots.initialise_plot(template=template)
    sectors = filters.get_bands_unique_values(bands, key='s')['s']
    for sector in sectors:
        sector_bands = filters.filter_bands(bands, s=[sector])
        select_dict[sector] = {
            'u' : sector_bands.u.tolist(),
            'lf' : sector_bands.lf.tolist(),
            'uf' : sector_bands.uf.tolist(),
            'bw' : sector_bands.bandwidth.tolist()
        }
    bands_merged = filters.merge_bands_threshold(bands, threshold, unique)
    filtered_bands_merged = filters.filter_bands(bands_merged, s=[sectors[0]])
    traces = filtered_bands_merged.trace.tolist()
    plots.batch_add_traces(plot, traces)
    plots.add_overlay_trace(plot)
    plots.update_overlay_trace(plot=plot, s=sectors[0], u=select_dict[sectors[0]]['u'][0],
                               lf=select_dict[sectors[0]]['lf'][0],
                               uf=select_dict[sectors[0]]['uf'][0])
    sector_dropdown = ipw.Dropdown(options=sectors,
                                   index=0,
                                   layout={'width' : 'auto'})
    u_range, u_name = [], []
    for index in range(len(select_dict[sectors[0]]['u'])):
        u = select_dict[sectors[0]]['u'][index]
        u_strings = u.split(' — ')
        u_range.append(u_strings[0])
        u_name.append(u_strings[1])
    band_select = ipw.Select(options=u_name,
                             value=None,
                             rows=len(select_dict[sectors[0]]['u']),
                             layout={'width' : 'auto'})
    band_select_alt = ipw.Select(options=u_range,
                             value=None,
                             rows=len(select_dict[sectors[0]]['u']),
                             layout={'width' : 'auto'})
    ipw.link((band_select, 'index'), (band_select_alt, 'index'))
    reset_button = ipw.Button(description='Reset Band Selection')
    sector_accordion = ipw.Accordion(children=[sector_dropdown],
                                     layout={'width' : 'auto'})
    band_accordion = ipw.Accordion(children=[ipw.VBox([reset_button,
                                                       ipw.HBox([band_select_alt, band_select],
                                                                layout={'height' : '300px'})])],
                                   layout={'width' : 'auto'})
    sector_accordion.set_title(0, 'Spectrum Sector')
    band_accordion.set_title(0, 'Spectrum Bands')
    sector_dropdown.observe(on_value_change_sector, names='value')
    band_select.observe(on_click_band, names='index')
    reset_button.on_click(on_button_click)
    this_dir = os.path.dirname(__file__)
    if template == 'plotly_dark':
        logo_address = os.path.join(this_dir, 'assets', 'strathsdr_dark.png')
    else:
        logo_address = os.path.join(this_dir, 'assets', 'strathsdr_white.png')
    logo_file = open(logo_address, 'rb')
    logo_image = logo_file.read()
    logo_widget = ipw.Image(value=logo_image,
                            format='png',
                            width=200,
                            height=35)
    about_html = ipw.HTML(value=about)
    side_box = ipw.VBox([logo_widget, about_html])
    app_box = ipw.Tab(children=[ipw.HBox([plot, ipw.VBox([sector_accordion, 
                                                          band_accordion])])])
    app_box.set_title(0, 'Spectrum Map')
    application = ipw.HBox([side_box, app_box])
    
    return application     
