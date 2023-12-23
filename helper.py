# HEAT PUMP RUNNING COSTS AND EMISSIONS ESTIMATOR
# A calculator for estimating the impact of upgrading from a gas boiler 
# to a heat pump on running costs, CO2 emissions and energy used.
#
# Copyright (C) 2022  Chris Warwick, Green Heat Coop Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# For enquiries about using this source code, please contact:
# hello@greenheatcoop.co.uk

import pandas as pd
import numpy as np
import altair as alt


def generate_df(data_list, data_list_new, value_names):
    """
    data_list, data_list_new : old and new list of lists of data,
            columns: old/new label, category, data values
            data_list_new can be list of such list of lists of data
    value_names: column names of data values    
    """
    cols = ["Case", "Breakdown"]
    cols.extend(value_names)
    
    df1 = pd.DataFrame(data_list, columns=cols)
    concat_list = [df1]
    if type(data_list_new) is list:
        for data in data_list_new:
            concat_list.append(pd.DataFrame(data, columns=cols))
    else:
        concat_list.append(pd.DataFrame(data_list_new, columns=cols))

    df = pd.concat(concat_list)
    df.round(0)
    df[df == 0] = np.NaN
    
    return df

    
def make_stacked_bar_narrow(source, value_name, col_scheme=2):
    """
    source - dataframe
    value_name - what to plot
    col_scheme - 1 if costs, otherwise 2
    """
    source = source.astype({value_name: 'float'})

    if col_scheme == 1:
        col_scheme = 'paired'
    else:
        col_scheme = 'category10'

    x_str = value_name #'Total Annual ' + 
    bars = alt.Chart(source).mark_bar().encode(
    y=alt.Y('sum(' + value_name + '):Q', stack='zero', title=x_str),
    x=alt.X('Case:N'),
    color=alt.Color('Breakdown:N', legend=alt.Legend(
        orient='bottom', #legendX=0, legendY=400,        
        direction='vertical'),    
        scale=alt.Scale(scheme=col_scheme))
    ).properties(width='container', height=500 #title=titleStr,
    ).configure_axis(titleFontSize=16, labelFontSize=14
    ).configure_legend(titleFontSize=16, labelFontSize=14)#.configure_title(fontSize=18
    #)
    #order=alt.Order(value_name, sort='descending')

    # text = alt.Chart(source).mark_text(dx=-15, dy=3, color='white').encode(
    #     x=alt.X('sum(' + value_name + '):Q', stack='zero'),
    #     y=alt.Y('Case:N'),
    #     detail='Breakdown:N',
    #     text=alt.Text('sum(' + value_name + '):Q', format='d')
    # )
    # chart = bars + text
    return bars

def make_stacked_bar_horiz(source, value_name, col_scheme=2):
    """
    source - dataframe
    value_name - what to plot
    col_scheme - 1 if costs, otherwise 2
    """
    source = source.astype({value_name: 'float'})

    if col_scheme == 1:
        col_scheme = 'paired'
    else:
        col_scheme = 'category10'

    x_str = value_name #'Total Annual ' + 
    bars = alt.Chart(source).mark_bar().encode(
    x=alt.X('sum(' + value_name + '):Q', stack='zero', title=x_str),
    y=alt.Y('Case:N', sort=['Current', 'Typical HP Install', 'Hi-performance HP Install']),
    color=alt.Color('Breakdown:N', legend=alt.Legend(
        orient='top', #legendX=0, legendY=400,        
        direction='horizontal'),    
        scale=alt.Scale(scheme=col_scheme))
    ).properties(width='container', height=300 #title=titleStr,
    ).configure_axis(titleFontSize=16, labelFontSize=14
    ).configure_legend(titleFontSize=16, labelFontSize=14)#.configure_title(fontSize=18
    #)
    #order=alt.Order(value_name, sort='descending')

    # text = alt.Chart(source).mark_text(dx=-15, dy=3, color='white').encode(
    #     x=alt.X('sum(' + value_name + '):Q', stack='zero'),
    #     y=alt.Y('Case:N'),
    #     detail='Breakdown:N',
    #     text=alt.Text('sum(' + value_name + '):Q', format='d')
    # )
    # chart = bars + text
    return bars