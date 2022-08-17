import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

#TODO: inductive hob cooking more efficient than gas hob cooking 
#also for gas/electric oven
#TODO: hot water tank efficiency

FILENAME_HW = 'hw_usage_examples.csv'
df_hw = pd.read_csv(FILENAME_HW, index_col=0)

FILENAME_COOK = 'cook_usage_examples.csv'
df_cook = pd.read_csv(FILENAME_COOK, index_col=0)

#default values
boiler_heat_eff = 0.88
boiler_hw_eff = 0.88
hw_temp_raise = 35
hp_heat_scop = 3.2
hp_hw_cop = 2.7

GAS_kgCO2perkWh = 0.21
ELEC_RENEW_kgCO2perkWh = 0
ELEC_AVE_kgCO2perkWh = 0.136

st.sidebar.header('Reference information')
st.sidebar.write('**Some typical amounts of water for different uses.**')
st.sidebar.table(df_hw)
st.sidebar.write('**Some typical amounts of energy used for cooking with gas appliances.**')
st.sidebar.table(df_cook)

tab1, tab2 = st.tabs(["Basic Settings", "Advanced Settings"])

with tab1:
    st.header('Annualized Cost and Emissions Estimator')
    #TODO: some proper intro text here
    st.write('Use this tool to compare how a heat pump could change your annual energy bills and CO2 emissions.')

    st.subheader('1. Forecast annual energy consumption')

    st.write('Your projected annual energy consumption should be available on your energy bill.')

    c1, c2 = st.columns(2)        
    with c1:

        elec_total_kWh = st.number_input('Annual projected electricity consumption (kWh)', min_value=0, max_value=100000, value=12000, step=100)
    with c2:
        gas_total_kWh = st.number_input('Annual projected gas consumption (kWh)', min_value=0, max_value=100000, value=12000, step=100)        

    is_elec_renewable = st.checkbox('Use only non-fossil fuel electricity', value=True, help='Otherwise the annual average CO2 emissions for UK mains electricity in 2021 is used.')    

    st.subheader('2. Gas usage')
    st.write('We need to understand a little a bit about how you use gas to estimate the heating requirements for your home.'
    + ' You can find some reference values in the sidebar to the left to help here.')
    c1, c2 = st.columns(2)
    with c1:
        is_hw_gas = st.checkbox('My hot water is heated with mains gas', value=False)

        if is_hw_gas:        
            st.write('How much hot water does your household use in a typical day?')
            #+' Typical hot water usage is between X and Y per person per day.')
            gas_hw_lday = st.number_input('Typical hot water usage is between X and Y litres per person per day. Enter the total litres/day here.', min_value=0, max_value=1000, value=100, step=1)
    with c2:
        
        is_cook_gas = st.checkbox('I cook with mains gas', value=False)

        if is_cook_gas:
            st.write('How much energy do you use cooking each week with gas?')
            gas_cook_kWhweek = st.number_input('A typical household uses between X and Y kWh per week. Enter total kWh/week here.', min_value=0, max_value=100, value=10, step=1)

    st.subheader('3. Tips for other set-ups')       
    ex = st.expander('I have a gas fireplace')
    with ex:
        st.write('Comment')

    ex = st.expander('I use solar thermal pannels to heat my hot water')
    with ex:
        st.write('Comment')

    ex = st.expander('I generate some of my own electricity')
    with ex:
        st.write('Comment')

    st.subheader('4. Switching to a heat pump')
    st.write('Some efficiency measures are often implemented prior to or as part of a heat pump installation, for example '
    + 'installing cavity wall insulation or larger radiators. If this is likely to be the case for you, you can add the net effect '
    + 'of them here. Typical measures reduce heating demand by 5-10%, minor measures 1-3%, major measures 10-30%.'
    + ' Some references values are also shown in the sidebar.')
    efficiency_boost = st.number_input('Percentage heating demand reduction for heat pump case', 
    min_value=0, max_value=99)
    st.write('If you can disconnect from gas completely, you can save money by not paying the gas standing charge. Any gas fireplace, '
    + 'gas hobs, or gas oven would need to be removed and replaced with electric appliances or simply disconnected.')
    is_disconnect_gas = st.checkbox('Disconnect from mains gas in heat pump scenario', value=False)
    
    is_submit1 = st.button(label='Update', key='b1')

with tab2:


    st.header('Advanced Settings')

    st.subheader('Energy costs')
    op1 = 'Use projected domestic energy price cap for the year October 2022 to September 2023'
    op2 = 'Use the custom unit and standing charges below'

    charge_option = st.radio('Energy charges',[op1, op2])
    if charge_option == op2:
        c1, c2 = st.columns(2)
        #TODO: different input of numbers here - monthly bill not broked down by gas/electricity?
        with c1:
    #            st.subheader('Gas')
            gas_stand = st.number_input('Gas standing charge (p/day)', min_value=0.0, max_value=100.0, value=26.0, step=0.01)
            gas_unit = st.number_input('Gas unit cost (p/kWh)', min_value=0.0, max_value=100.0, value=7.0, step=0.01)

        with c2:
    #           st.subheader('Electricity')
            elec_stand = st.number_input('Electricity standing charge (p/day)', min_value=0.0, max_value=100.0, value=36.0, step=0.01)        
            elec_unit = st.number_input('Electricity unit cost (p/kWh)', min_value=0.0, max_value=100.0, value=28.0, step=0.01)  
    else:
        gas_stand = 26.0
        gas_unit = 7.0
        elec_stand = 36.0
        elec_unit = 28.0

    st.subheader('Device performance')
    c1, c2 = st.columns(2)
    
    with c1:
        st.write('Average boiler efficiency')
        boiler_heat_eff = st.number_input('When space heating', min_value=0.0, max_value=1.00, value=0.88, step=0.01)
        boiler_hw_eff = st.number_input('When hot water heating', min_value=0.0, max_value=1.00, value=0.88, step=0.01)
    with c2:
        st.write('Heat pump seasonal coefficient of performance')
        hp_heat_scop = st.number_input('When space heating', min_value=0.1, max_value=10.0, value=3.2, step=0.1)
        hp_hw_cop = st.number_input('When hot water heating', min_value=0.1, max_value=10.0, value=2.7, step=0.1)

    hw_temp_raise = st.number_input('Cold and hot water temperature difference (degC)', min_value=1, max_value=100, step=1, 
    help='The typical difference in temperature between mains water and hot water as used.', value=35)

    st.subheader('Carbon intensity')
    st.write("some text explaining")

    st.subheader('Other assumptions')
    st.write("some text explaining")

    is_submit2 = st.button(label='Update', key='b2')

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
    st.altair_chart(bars, use_container_width=True)

def show_results():
    
    st.header('Results')
    st.write("Installing a heat pump is expected to reduce your household annual CO2 emissions by "
            + f"**{(emissions_total-emissions_total_new)/1000:.2f} tonnes**, from "
            + f"**{emissions_total/1000:.2f} tonnes** to **{emissions_total_new/1000:.2f} tonnes**.")
    if costs_total_new < costs_total:
        change_str = 'decrease'
    else:
        change_str = 'increase'

    st.write(f"Your annual energy costs are expected to {change_str} by "
            f"**£{abs(costs_total_new-costs_total):.0f}** from "
            + f"**£{costs_total:.0f}** to **£{costs_total_new:.0f}**.")
    # c1, c2 = st.columns(2)

    # with c1:
    #     st.subheader('Current System')
    #     st.metric('Total Annual Cost', f"£ {costs_total:.0f}")
    #     st.metric('Total Annual Emissions', f"{emissions_total:.0f} kgCO2e")

    # with c2:
    #     st.subheader('Heat Pump System')
    #     st.metric('Total Annual Cost', f"£ {costs_total_new:.0f}")
    #     st.metric('Total Annual Emissions', f"{emissions_total_new:.0f} kgCO2e")
    
    df_costs = generate_df(costs_by_type, costs_by_type_new, ['Costs (£)'])
    print(df_costs.head())
    df_energy = generate_df(energy_usage, energy_usage_new, ['Energy (kWh)', 'Emissions (kgCO2e)'])

    make_stacked_bar(df_costs, 'Costs (£)', 'Total Costs Comparison')
    make_stacked_bar(df_energy, 'Energy (kWh)', 'Total Energy Consumption Comparison')
    make_stacked_bar(df_energy, 'Emissions (kgCO2e)', 'Total CO2 Emissions Comparison')

if not (is_submit1 or is_submit2):
    st.stop()

GAS_HW_kWhperL = 4200 * hw_temp_raise/(3600 * 1000 * boiler_hw_eff)
    #first do the current case
#don't worry about fixed/non-fixed contract for now, or future energy costs
costs_by_type = [['Current', 'Gas standing charge', gas_stand*3.65],
                ['Current', 'Gas unit costs',  gas_total_kWh * gas_unit/100],
                ['Current', 'Electricity standing charge', elec_stand*3.65],
                ['Current', 'Electricity unit costs', elec_total_kWh * elec_unit/100]] 
            
costs_total = (gas_stand + elec_stand)*3.65 + gas_total_kWh * gas_unit/100 + elec_total_kWh * elec_unit/100

#gas_total_kWh = (gas_bill*12 - gas_stand*3.65)/(gas_unit/100)
#elec_total_kWh = (elec_bill*12 - elec_stand*3.65)/(elec_unit/100)

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
elec_heat_kWh = (1 - efficiency_boost/100) * gas_heat_kWh * boiler_heat_eff/hp_heat_scop
elec_hw_kWh = gas_hw_kWh * boiler_heat_eff/hp_hw_cop

elec_total_kWh_new = elec_total_kWh + elec_heat_kWh + elec_hw_kWh

if is_cook_gas:
    if is_disconnect_gas:
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