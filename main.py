import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

#TODO: set example usages properly
FILENAME_HW = 'hw_usage_examples.csv'
df_hw = pd.read_csv(FILENAME_HW)

FILENAME_COOK = 'cook_usage_examples.csv'
df_cook = pd.read_csv(FILENAME_COOK)

#TODO: advanced tab setting these
BOILER_EFF = 0.88
GAS_HW_kWhperL = 4200 * 35/(3600 * 1000 * BOILER_EFF)
HP_HEAT_SCOP = 3.2
HP_HW_COP = 2.7

GAS_kgCO2perkWh = 0.21
ELEC_RENEW_kgCO2perkWh = 0
ELEC_AVE_kgCO2perkWh = 0.136

#TODO: some proper intro text here
st.sidebar.header('Reference info...')
st.sidebar.write('Some typical hot water volumes...')
st.sidebar.table(df_hw)
st.sidebar.write('Some typical cooking energy...')
st.sidebar.table(df_cook)

st.header('Annualized Cost and Emissions Estimator')
#TODO: some proper intro text here
st.write('Use this to compare how getting a heat pump could change your annual energy bills and CO2 emissions.')

with st.form('user_input'):

    c1, c2 = st.columns(2)
    #TODO: different input of numbers here - monthly bill not broked down by gas/electricity?
    with c1:
        st.subheader('Gas')
        gas_stand = st.number_input('Gas standing charge (p/day)', min_value=0.0, max_value=100.0, value=26.0, step=0.01)
        gas_unit = st.number_input('Gas unit cost (p/kWh)', min_value=0.0, max_value=100.0, value=7.0, step=0.01)
        gas_bill = st.number_input('Monthly gas bill (£)', min_value=0, max_value=1000, value=65, step=1)
    with c2:
        st.subheader('Electricity')
        elec_stand = st.number_input('Electricity standing charge (p/day)', min_value=0.0, max_value=100.0, value=36.0, step=0.01)        
        elec_unit = st.number_input('Electricity unit cost (p/kWh)', min_value=0.0, max_value=100.0, value=28.0, step=0.01)
        elec_bill = st.number_input('Monthly electricity bill (£)', min_value=0, max_value=1000, value=78, step=1)

    #TODO: do something with contract or take out
    is_fixed_contract = st.checkbox('I have a fixed energy contract', value=True)
    if is_fixed_contract:
        fixed_until = st.date_input('Date contract is fixed until')

    c1, c2 = st.columns(2)
    with c1:
        st.subheader('Hot water')
        is_hw_gas = st.checkbox('My hot water is heated with mains gas', value=True)

        if is_hw_gas:        
            gas_hw_lday = st.number_input('Hot water usage (litres per day)', min_value=0, max_value=1000, value=100, step=1)
    with c2:
        st.subheader('Cooking')

        is_cook_gas = st.checkbox('I cook with mains gas', value=True)

        if is_cook_gas:
            gas_cook_kWhweek = st.number_input('Cooking usage (kWh/week)', min_value=0, max_value=100, value=10, step=1)
            is_convert_cook = st.checkbox('Convert any gas cooking to electricity in heat pump scenario', value=True)

    efficiency_boost = st.number_input('Heating demand reduction as a result of energy efficiency measures implemented Heat Pump installation', 
    min_value=0, max_value=99, help='For example as a result of any change in your radiators or insulation.')
    is_disconnect_gas = st.checkbox('Disconnect from mains gas in heat pump scenario', value=True, help='Any cooking gas is then switched to electric.')
    is_elec_renewable = st.checkbox('Use only non-fossil fuel electricity', value=True, help='Otherwise the annual average CO2 emissions for UK mains electricity in 2021 is used.')    

    is_submit = st.form_submit_button()

def generate_df(data_list, data_list_new, value_names):

    cols = ["Case", "Breakdown"]
    cols.extend(value_names)
    
    df1 = pd.DataFrame(data_list, columns=cols)
    df2 = pd.DataFrame(data_list_new, columns=cols)
    df = pd.concat([df1, df2])
    
    #TODO: set zeros to NaN
    #TODO: round to correct sig fig
    return df

def make_stacked_bar(source, value_name):
    #TODO: change size of bar charts
    source = source.astype({value_name: 'float'})

    bars = alt.Chart(source).mark_bar().encode(
    x=alt.X('sum(' + value_name + '):Q', stack='zero'),
    y=alt.Y('Case:N'),
    color=alt.Color('Breakdown:N')
    )

    text = alt.Chart(source).mark_text(dx=-15, dy=3, color='white').encode(
        x=alt.X('sum(' + value_name + '):Q', stack='zero'),
        y=alt.Y('Case:N'),
        detail='Breakdown:N',
        text=alt.Text('sum(' + value_name + '):Q', format='.1f')
    )

    st.altair_chart(bars + text, use_container_width=True)

def show_results():

    #TODO some introductory text
    c1, c2 = st.columns(2)

    with c1:
        st.subheader('Current System')
        st.metric('Total Annual Cost', '£' + str(costs_total))
        st.metric('Total Annual Emissions', str(emissions_total) + ' kgCO2e')

    with c2:
        st.subheader('Heat Pump System')
        st.metric('Total Annual Cost', '£' + str(costs_total_new))
        st.metric('Total Annual Emissions', str(emissions_total_new) + ' kgCO2e')
    
    df_costs = generate_df(costs_by_type, costs_by_type_new, ['Costs (£)'])
    df_energy = generate_df(energy_usage, energy_usage_new, ['Energy (kWh)', 'Emissions (kgCO2e)'])

    make_stacked_bar(df_costs, 'Costs (£)')
    make_stacked_bar(df_energy, 'Energy (kWh)')
    make_stacked_bar(df_energy, 'Emissions (kgCO2e)')

if is_submit:

        #first do the current case
    #don't worry about fixed/non-fixed contract for now, or future energy costs
    costs_by_type = [['Current', 'Gas standing charge', gas_stand*3.65],
                    ['Current', 'Gas unit costs',  gas_bill*12 - gas_stand*3.65],
                    ['Current', 'Electricity standing charge', elec_stand*3.65],
                    ['Current', 'Electricity unit costs', elec_bill*12 - elec_stand*3.65]] 
                    
    costs_total = (gas_bill + elec_bill) * 12

    gas_total_kWh = (gas_bill*12 - gas_stand*3.65)/(gas_unit/100)
    elec_total_kWh = (elec_bill*12 - elec_stand*3.65)/(elec_unit/100)

    if is_hw_gas:
        gas_hw_kWh = gas_hw_lday * 365 * GAS_HW_kWhperL
    else:
        gas_hw_kWh = 0

    if is_cook_gas:
        gas_cook_kWh = gas_cook_kWhweek * 52
    else:
        gas_cook_kWh = 0

    gas_heat_kWh = gas_total_kWh - gas_hw_kWh - gas_cook_kWh

    if is_elec_renewable:
        elec_kgCO2perkWh = ELEC_RENEW_kgCO2perkWh
    else:
        elec_kgCO2perkWh = ELEC_AVE_kgCO2perkWh

    energy_usage = [['Current', 'Heating', gas_heat_kWh, gas_heat_kWh*GAS_kgCO2perkWh],
                ['Current', 'Hot water', gas_hw_kWh, gas_hw_kWh*GAS_kgCO2perkWh],
                ['Current', 'Cooking', gas_cook_kWh, gas_cook_kWh*GAS_kgCO2perkWh],
                ['Current', 'Other Electricity', elec_total_kWh, elec_total_kWh*elec_kgCO2perkWh]]                

    emissions_total = sum([gas_heat_kWh*GAS_kgCO2perkWh, gas_hw_kWh*GAS_kgCO2perkWh, gas_cook_kWh*GAS_kgCO2perkWh, elec_total_kWh*elec_kgCO2perkWh])
    #now do the future/heat pump case
    elec_heat_kWh = gas_heat_kWh * BOILER_EFF/HP_HEAT_SCOP
    elec_hw_kWh = gas_hw_kWh * BOILER_EFF/HP_HW_COP

    elec_total_kWh_new = elec_total_kWh + elec_heat_kWh + elec_hw_kWh

    if is_disconnect_gas:
        is_convert_cook = True

    if is_cook_gas:
        if is_convert_cook:
            emissions_cook = gas_cook_kWh * elec_kgCO2perkWh
            elec_total_kWh_new += gas_cook_kWh
            gas_total_kWh_new = 0
        else:
            emissions_cook = gas_cook_kWh * GAS_kgCO2perkWh
            gas_total_kWh_new = gas_cook_kWh
    else:
        emissions_cook = 0
        gas_total_kWh_new = 0

    energy_usage_new = [['Heat Pump', 'Heating', elec_heat_kWh, elec_heat_kWh*elec_kgCO2perkWh],
                ['Heat Pump', 'Hot water', elec_hw_kWh, elec_hw_kWh*elec_kgCO2perkWh],
                ['Heat Pump', 'Cooking', gas_cook_kWh, emissions_cook],
                ['Heat Pump', 'Other Electricity', elec_total_kWh, elec_total_kWh*elec_kgCO2perkWh]]   

    emissions_total_new = sum([elec_heat_kWh*elec_kgCO2perkWh, elec_hw_kWh*elec_kgCO2perkWh, emissions_cook, elec_total_kWh*elec_kgCO2perkWh])

    if is_disconnect_gas:
        gas_stand_total_new = 0
    else:
        gas_stand_total_new = gas_stand*3.65

    costs_by_type_new = [['Heat Pump', 'Gas standing charge', gas_stand_total_new],
                    ['Heat Pump', 'Gas unit costs',  gas_total_kWh_new*gas_unit/100],
                    ['Heat Pump', 'Electricity standing charge', elec_stand*3.65],
                    ['Heat Pump', 'Electricity unit costs', elec_total_kWh_new*elec_unit/100]] 

    costs_total_new = sum([gas_stand_total_new, gas_total_kWh_new*gas_unit/100, elec_stand*3.65, elec_total_kWh_new*elec_unit/100])

    show_results()