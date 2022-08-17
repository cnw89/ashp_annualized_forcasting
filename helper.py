import pandas as pd
import numpy as np
import altair as alt


def generate_df(data_list, data_list_new, value_names):

    cols = ["Case", "Breakdown"]
    cols.extend(value_names)
    
    df1 = pd.DataFrame(data_list, columns=cols)
    df2 = pd.DataFrame(data_list_new, columns=cols)
    df = pd.concat([df1, df2])
    df.round(0)
    df[df == 0] = np.NaN
    
    return df

def make_stacked_bar(source, value_name, titleStr):
    #TODO: change size of bar charts
    source = source.astype({value_name: 'float'})

    x_str = 'Total Annual ' + value_name
    bars = alt.Chart(source).mark_bar().encode(
    x=alt.X('sum(' + value_name + '):Q', stack='zero', title=x_str),
    y=alt.Y('Case:N'),
    color=alt.Color('Breakdown:N')
    ).properties(title=titleStr, width='container', height=300
    ).configure_axis(titleFontSize=16, labelFontSize=14
    ).configure_title(fontSize=18
    ).configure_legend(titleFontSize=16, labelFontSize=14)

    # text = alt.Chart(source).mark_text(dx=-15, dy=3, color='white').encode(
    #     x=alt.X('sum(' + value_name + '):Q', stack='zero'),
    #     y=alt.Y('Case:N'),
    #     detail='Breakdown:N',
    #     text=alt.Text('sum(' + value_name + '):Q', format='d')
    # )
    # chart = bars + text
    return bars
    
def make_stacked_bar_narrow(source, value_name, col_scheme=2):
    
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
        scale=alt.Scale(scheme=col_scheme)),
    order=alt.Order(value_name, sort='descending')
    ).properties(width='container', height=400 #title=titleStr,
    ).configure_axis(titleFontSize=16, labelFontSize=14
    ).configure_legend(titleFontSize=16, labelFontSize=14)#.configure_title(fontSize=18
    #)

    # text = alt.Chart(source).mark_text(dx=-15, dy=3, color='white').encode(
    #     x=alt.X('sum(' + value_name + '):Q', stack='zero'),
    #     y=alt.Y('Case:N'),
    #     detail='Breakdown:N',
    #     text=alt.Text('sum(' + value_name + '):Q', format='d')
    # )
    # chart = bars + text
    return bars