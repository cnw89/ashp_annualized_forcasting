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

import streamlit as st
import pandas as pd
from helper import generate_df, make_stacked_bar_horiz
from PIL import Image

#new comment
#__________ set default values______________
#efficiencies and performance coefficients - default values
boiler_heat_eff = 0.88
boiler_hw_eff = 0.88
immersion_hw_eff = 1
#typical heat pump performance:
hp_heat_scop_typ = 3.4
hp_hw_cop_typ = 2.8
#hi heat pump performance
hp_heat_scop_hi = 4.0
hp_hw_cop_hi = 2.8

#Raise in temp (degC) from mains water to hot water AS USED
hw_temp_raise_default = 25

#carbon intensity values taken from SAP 10.2 (dec 2021)
GAS_kgCO2perkWh = 0.21
ELEC_RENEW_kgCO2perkWh = 0
ELEC_AVE_kgCO2perkWh = 0.136

# price cap October 2025 gas and electricity domestic standing and unit charges
gas_stand = 34.03
gas_unit = 6.29
elec_stand = 53.68
elec_unit = 26.35
#cosy octopus details
elec_unit_cosy_standard=elec_unit
elec_unit_cosy_offpeak = 0.6*elec_unit
elec_unit_cosy_peak = 1.6*elec_unit
pc_other_elec_cosy_offpeak = 0.2
pc_other_elec_cosy_peak = 0.2
cosy_second_tariff_hours = 6
cosy_third_tariff_hours = 3
cosy_offpeak_heat_demand_reduction = 1 #for cosy octopus - less heat demand in the night period due to switch to hot water, compensated by possible boost in day time.
offpeak_heat_demand_reduction = 2/3 # for economy 7 and octopus go - less heat needed in the night

# efficincy measures to choose from
efficiency_opts = [('Draft proofing and/or door insulation (3%)', 0.03),
                    ('Increased loft insulation (5%)', 0.05),
                    ('Improved window glazing (5%)', 0.05),
                    ('Cavity wall insulation (10%)', 0.1),
                    ('Underfloor insulation (10%)', 0.1),
                    ('Internal or external solid wall insulation (15%)', 0.15),
                    ('Enter a custom heating demand saving', -1.0)]
#____________ Page info________________________________________

about_markdown = 'This app has been developed by Chris Warwick, August-October 2022, for Green Heat Coop Ltd. ' + \
'(www.greenheatcoop.co.uk). For enquiries about this tool you can email hello@greenheatcoop.co.uk, or message' + \
    ' @greenheatcoop on Twitter, Facebook, or Nextdoor. This program is free software: you can redistribute it and/or modify' + \
' it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3 of the License.'

st.set_page_config(layout="centered", menu_items={'Get Help': None, 'Report a Bug': None, 'About': about_markdown})

#__________write some reference info to the sidebar____________

df_tot = pd.DataFrame([['1', 2100, 7000], ['2', 2750, 9500], 
                        ['3', 3000, 12000], ['4', 3500, 15000],
                        ['5', 4300, 17000]],
                        columns=['House size', 'Electricity (kWh)', 'Gas (kWh)'])
df_tot.set_index('House size', inplace=True)                        

df_hw = pd.DataFrame([['Washing up', 15], ['5 min water-saving shower', 30], ['10 min power shower', 150], ['Bath', 100]],
columns=['Use', 'Hot water used (L)'])
df_hw.set_index('Use', inplace=True)

df_cook = pd.DataFrame([['Gas hob', 0.8], ['Gas grill', 1], ['Gas oven', 1.5]],
columns=['Use', 'Gas consumption per use (kWh)'])
df_cook.set_index('Use', inplace=True)

st.sidebar.header('Reference information')
st.sidebar.subheader('Typical total annual household energy consumption by number of bedrooms (with no EV)')
st.sidebar.table(df_tot.style.format("{:,d}"))
st.sidebar.subheader('Typical amounts of water for different uses')
st.sidebar.table(df_hw)
st.sidebar.subheader('Typical amounts of energy used for cooking with gas appliances')
st.sidebar.table(df_cook.style.format(precision=1))

#___________Main page__________________________________________

st.title('Heat Pump Running Costs and Emissions Estimator')    

img = Image.open('heat pump close up edit.JPG')
st.image(img)

st.write('Use this tool to compare how a heat pump could change your annual energy bills and CO$_2$ emissions.  '
+ 'Enter some information below, and once you are ready, press the *Update Results* button at the bottom to see the comparison.  ' +
'This tool is currently only suited to those who use a gas boiler as the main source of heat for their house.')
st.markdown('To calculate an estimate of the cost of installing a heat pump, see the Nesta demo tool ' +
'<a href="http://asf-hp-cost-demo-l-b-1046547218.eu-west-1.elb.amazonaws.com/">here</a>.', unsafe_allow_html=True)
#st.header('Inputs')
st.markdown("<div id='linkto_top'></div>", unsafe_allow_html=True)

#Now go to main tabs
tab1, tab2, tab3 = st.tabs(["Basic Settings", "Advanced Settings", "Further Information"])

with tab1:
    #_______________basic settings_________________________________________
    st.subheader('1.  Annual energy consumption')

    st.write('Your projected annual energy consumption should be available on your energy bill. If you do not know ' +
    'your annual energy consumption, you can use the typical values for your house size shown in the sidebar to the left.')
    # is_know_annual = st.radio('Do you know your annual energy consumption for electricity and gas?', ['Yes', 'No'])
     
    # if is_know_annual is 'Yes':

    c1, c2 = st.columns(2)        
    with c1:
        elec_total_kWh = st.number_input('Annual electricity consumption (kWh):', min_value=0, max_value=100000, value=3000, step=100)
    with c2:
        gas_total_kWh = st.number_input('Annual gas consumption (kWh):', min_value=0, max_value=100000, value=12000, step=100)        

    is_elec_renewable = st.checkbox('I have a 100% renewable energy tariff', value=False)    
    
    with st.expander('More about renewable energy tariffs'):
        st.markdown('Please note that not all "100% renewable" energy tariffs are equivalent. For example some suppliers invest in ' +
        'renewable energy production, while others only buy unwanted renewable energy certificates. You can learn more about this ' +
        "<a href='https://www.cse.org.uk/advice/advice-and-support/green-electricity-tariffs'>here</a>. In this tool we take a 100% renewable" +
        ' tariff to have zero carbon emissions, otherwise we use the emissions of the general energy mix of the grid. We leave it to you to decide' +
        ' which is more appropriate for your tariff. This also means that the embedded carbon emissions of the grid and energy generators is not accounted for here.',
        unsafe_allow_html=True)

    st.write(' To customize the energy tariff used, see the *Advanced Settings* tab.')

    st.subheader('2.  Hot water usage')
    st.write('How is your hot water heated?  If you have solar thermal panels to heat your hot water, select the source which tops-up the temperature when needed.')
    hw_source = st.radio('Hot water heat source:', ['gas', 'electricity (immersion heater or electric boiler)'])
    is_hw_gas = (hw_source=='gas')

    st.write('How much hot water does your household use in a typical day?  *You can find some reference values in the sidebar to the left to help here.*')
    hw_lday = st.number_input('The UK average is 140 litres per person per day.  Enter the total litres/day here:', 
    min_value=0, max_value=1000, value=350, step=1)

    st.subheader('3.  Cooking')
    st.write('If you cook with gas, we would like to know how much to help calculate the energy used for heating.')
    is_cook_gas = st.checkbox('I cook with mains gas', value=False)

    if is_cook_gas:
        st.write('How much energy do you use cooking with gas *each week*? *You can find some reference values in the sidebar to the left to help here.*')
        gas_cook_kWhweek = st.number_input('A typical household uses between 5 and 12 kWh per week.  Enter total kWh/week here:', 
        min_value=0, max_value=100, value=8, step=1)

    st.subheader('4.  More complex homes')       
    
    with st.expander('I have an Electric Vehicle (EV) that I charge at home'):
        
        st.write('I charge my EV:')
        c1, c2 = st.columns(2)        
        with c1:
            helpstring='Don\'t include energy generated by your own solar panels used to charge your EV'
            elec_ev_kWh = st.number_input('Typical imported energy per charge (kWh):', min_value=0, max_value=100, value=30, step=1, help=helpstring)
        with c2:
            charges_per_week = st.number_input('Number of charges per week', min_value=0, max_value=10, value=0, step=1)
        
        elec_ev_kWh = elec_ev_kWh * charges_per_week * 52

        st.write('If you have an electricity tariff that allows you to charge your EV at a lower rate, you can input your tariff in '
                 + 'the Advanced Settings tab, by selecting "Use custom unit and standing charges".')


    with st.expander('I have a secondary heating source in addition to gas central heating'):
        is_second_heatsource = st.checkbox('I have a secondary heating source in addition to gas central heating', value=False)
        
        if is_second_heatsource:
            opts = ['gas', 'electric', 'other (not included in energy consumption calculations below)']
            second_heatsource_type = st.radio('My secondary heat source is:', opts)
            opts = ['Keep using my secondary heat source', 'Remove the secondary heat source and have the heat pump supply this heat']
            second_heatsource_remains = st.radio('In the heat pump scenario, I would...', opts)
            is_second_heatsource_remains = (second_heatsource_remains == opts[0])
            second_heatsource_kWh = st.number_input('Annual estimated energy usage of the secondary heatsource (kWh).  5% of your gas usage is used as an intial estimate.', min_value=0, max_value=100000, value=int(0.05*gas_total_kWh), step=10)

    # some complex set-ups don't need extra inputs, just explain how to use the existing ones.
    with st.expander('I generate some of my own electricity'):
        st.write('When entering the annual electricity consumption above, only input the annual *imported* electricity. ' +
        'The results below will then only relate to the imported energy and emissions.' +
        ' Heating your home with a heat pump may not use much of your solar-generated electricity due to the energy demand ' +
        'being primarily in the winter when your existing electricity consumption may already use all your generation capacity. '
        'However, your surplus generation capacity in the summer months can be used to heat your hot water with the heat pump.')
        is_free_summer_hw = st.checkbox('Set 4 months of summer hot water use to be provided at no cost in the heat pump scenarios', value=False)

    with st.expander('I use solar thermal panels to heat my hot water'):
        st.write('Typically solar thermal energy does not provide all of your hot water heating needs.  In this case you should reduce the '
        +'hot water usage above to the fraction that will be heated by other sources on an average day (across the whole year).')

    st.subheader('5.  Switching to a heat pump')

    st.write('Some efficiency measures are often implemented prior to or as part of a heat pump installation.' +
    ' Optionally, you can take these into account here.')    
    
    efficiency_boost = 0
    with st.expander('Energy efficiency measures'):         
        st.write('Select the energy efficiency measures to be implemented.' +
        ' Approximate heating demand reduction for each measure is shown in brackets. These are conservative estimates based on average *measured*' +
         ' reductions in heat demand rather than quoted reductions, which includes for example the effect of households choosing more comfortable heating settings' +
         ' once their energy bill reduces. Alternatively you can enter a custom heating demand reduction by selecting the last checkbox.')
        
        #make a checkbox for each efficiency boost we have:
        for (lab, boost) in efficiency_opts:

            is_op = st.checkbox(lab, value=False)
            if is_op:
                if boost < 0: #custom option selected
                    custom_val = st.number_input('Enter percentage saving:', 0.0, 100.0, 20.0, 1.0)
                    efficiency_boost += custom_val/100
                else:
                    efficiency_boost += boost     

    st.write('Save more money by switching your electricity tariff after the heat pump is installed. If you already have an EV tariff with a low ' 
             + ' unit rate, you may be better of keeping your current electricity tariff.')
    op1 = 'Keep my current electricity tariff'
    op2 = 'Lower my bills with a heat pump electricity tariff'
    op3 = 'Lower my bills further with a heat pump electricity tariff, and switching my heating off from 4-7pm each day'
    helpstring = 'The heat pump electricity tariff used here is based on the Cosy Octopus tariff, which has three different rates for ' \
    + 'different times of day. See the further information tab for more detail.'
    tariff_switch_option = st.radio('Tariff choice:',[op1, op2, op3], 2,help=helpstring) #TODO

    switch_tariff_for_hp = False
    if tariff_switch_option != op1:
        switch_tariff_for_hp = True

    turn_off_hp_in_peak_hours = False
    if tariff_switch_option == op3:
        turn_off_hp_in_peak_hours = True

    st.write('If you can disconnect from gas completely, you may save money by not paying the gas standing charge.  Any gas fireplace, '
    + 'gas hobs, or gas oven would need to be removed and replaced with electric appliances or simply disconnected.')
    is_disconnect_gas = st.checkbox('Disconnect from mains gas in heat pump scenario', value=True)

n_tariff_states = 1
#____________advanced settings______________________
with tab2:

    st.subheader('1.  Energy prices')

    op1 = 'Use the UK-average domestic energy price cap for direct debit paying customers for the period beginning October 2025'
    op2 = 'Use custom unit and standing charges'

    charge_option = st.radio('Prices to use:',[op1, op2])

    #if user selects to input their own energy tariff
    if charge_option == op2:

        op1 = 'Use a standard fixed electricity tariff'
        op2 = 'Use an electricity tariff with an off-peak rate'
        op3 = 'Use an electricity tariff with an off-peak, peak, and standard rate'
        tariff_option = st.radio('Type of tariff:',[op1, op2, op3])
        
        if tariff_option == op2:
            n_tariff_states = 2
        elif tariff_option == op3:
            n_tariff_states = 3

        c1, c2 = st.columns(2)
        
        with c1:    
            gas_stand = st.number_input('Gas standing charge (p/day):', min_value=0.0, max_value=100.0, value=gas_stand, step=0.01)
            gas_unit = st.number_input('Gas unit cost (p/kWh):', min_value=0.0, max_value=100.0, value=gas_unit, step=0.01)

        with c2:    
            elec_stand = st.number_input('Electricity standing charge (p/day):', min_value=0.0, max_value=100.0, value=elec_stand, step=0.01)        
            elec_unit = st.number_input('Electricity standard unit cost (p/kWh):', min_value=0.0, max_value=100.0, value=elec_unit, step=0.01)  

        helpstring = 'If you have an EV, we assume that it is only charged with off-peak energy.'   
        if n_tariff_states == 2:
                    
            elec_unit2 = st.number_input('Off-peak electricity unit cost (p/kWh):', min_value=0.0, max_value=100.0, value=0.6*elec_unit, step=0.01)  
            second_tariff_hours = st.slider('Number of hours of off-peak tariff per day:', 1, 12, 6, 1)
            pc_elec_second_tariff = st.slider('Percentage of current electricity consumption (excluding EV) in off-peak hours:', 0, 100, 30, 1, help=helpstring)
            pc_elec_second_tariff /= 100

            st.write('If you keep this tariff in the heat pump scenarios we assume that the average energy consumed per off-peak hour by heating is two-thirds that used in the' +
            ' average standard hour. We also assume all of the hot water heating is performed in off-peak hours (unless using solar power) and none of the cooking.')

        if n_tariff_states == 3:
            
            c1, c2 = st.columns(2)
        
            with c1:  
                elec_unit2 = st.number_input('Off-peak electricity unit cost (p/kWh):', min_value=0.0, max_value=100.0, value=elec_unit_cosy_offpeak, step=0.01)  
                second_tariff_hours = st.slider('Number of hours of off-peak rate per day:', 1, 12, cosy_second_tariff_hours, 1)
                pc_elec_second_tariff = st.slider('Percentage of current electricity consumption (excluding EV) in off-peak hours:', 0, 100, int(100*pc_other_elec_cosy_offpeak), 1, help=helpstring)
                pc_elec_second_tariff /= 100

            with c2:  
                elec_unit3 = st.number_input('Peak electricity unit cost (p/kWh):', min_value=0.0, max_value=100.0, value=1.6*elec_unit, step=0.01)  
                third_tariff_hours = st.slider('Number of hours of peak rate per day:', 1, 12, cosy_third_tariff_hours, 1)
                pc_elec_third_tariff = st.slider('Percentage of current electricity consumption (excluding EV) in peak hours:', 0, 100, int(100*pc_other_elec_cosy_peak), 1, help=helpstring)
                pc_elec_third_tariff /= 100
                pc_elec_third_tariff = max(pc_elec_third_tariff, 1-pc_elec_second_tariff)

            st.write('If you keep this tariff in the heat pump scenarios we assume that the average energy consumed per off-peak hour by heating is two-thirds that used in the' +
            ' average standard hour. The heat pump is assumed to be off during peak hours. We also assume all of the hot water heating is performed in' +
             ' off-peak hours (unless using solar power). All of the cooking is assumed to fall in peak hours.')

          
    st.subheader('2.  Device performance')
    st.write('Results are calculated for both a typical and a high-performance heat pump installation.  '
    + ' The heat pump system performance is described by the seasonal coefficient of performance (SCOP).')
    c1, c2, c3 = st.columns([3, 3, 4])
    
    #TODO: could potentially include immersion heating efficiency here
    with c1:
        st.write('_Average boiler efficiency_')
        boiler_heat_eff = st.number_input('When space heating:', min_value=0.0, max_value=1.00, value=boiler_heat_eff, step=0.01, key='boiler1')
        boiler_hw_eff = st.number_input('When hot water heating:', min_value=0.0, max_value=1.00, value=boiler_hw_eff, step=0.01, key='boiler2')
    with c2:
        st.write('*Typical heat pump SCOP*')
        hp_heat_scop_typ = st.number_input('When space heating:', min_value=0.1, max_value=10.0, value=hp_heat_scop_typ, step=0.1, key='typ1')
        hp_hw_cop_typ = st.number_input('When hot water heating:', min_value=0.1, max_value=10.0, value=hp_hw_cop_typ, step=0.1, key='typ2')
    with c3:
        st.write('*High-performance heat pump SCOP*')
        hp_heat_scop_hi = st.number_input('When space heating:', min_value=0.1, max_value=10.0, value=hp_heat_scop_hi, step=0.1, key='hi1')
        hp_hw_cop_hi = st.number_input('When hot water heating:', min_value=0.1, max_value=10.0, value=hp_hw_cop_hi, step=0.1, key='hi2')

    st.subheader('3.  Hot Water Temperature')
    st.write('Typical mains cold water may be at 15$^{\circ}$C, while a comfortable shower temperature is 37-41$^{\circ}$C.  The gas boiler '
    + 'will supply hot water hotter than this, which is then mixed with cold water, but the total energy used per litre is similar to providing '
    +'water at this temperature.')
    hw_temp_raise = st.number_input('Cold and hot water temperature difference (degrees C):', min_value=1, max_value=100, step=1, 
    help='The typical difference in temperature between mains water and hot water as used.', value=hw_temp_raise_default)

with tab3:
    #____________ Further Information____________________________
    st.subheader('1.  Carbon intensity')
    st.write("We use standard values for carbon intensity of different energy sources as set in the Standard Assessment Procedure (SAP) 10.2, "
    +"released December 2021.  These values only consider the CO$_2$ equivalent emissions associated per unit of energy, not the embedded emissions of the "
    + "energy generation and transmission infrastructure.  These values are: ")
    costs_table = pd.DataFrame([['Mains Gas', GAS_kgCO2perkWh], ['Electricity (grid average)', ELEC_AVE_kgCO2perkWh],
    ['Electricity (renewable only)', ELEC_RENEW_kgCO2perkWh]], columns=['Energy Source', 'CO2 Equivalent Emissions (kgCO2/kWh)'])
    costs_table.set_index('Energy Source', inplace=True)
    st.table(costs_table)

    st.subheader('3.  Heat pump tariff')
    st.markdown(
    """
    The heat pump tariff used here is based on the <a href='https://octopus.energy/smart/cosy-octopus/'>Cosy Octopus tariff</a>.
    The Cosy Octopus tariff has a off-peak, standard and peak electricity rate, depending on the time of day.
    The following table describes our assumptions of when energy is used in the day:
    """, unsafe_allow_html=True
    )
    pc_2_without = cosy_offpeak_heat_demand_reduction*cosy_second_tariff_hours/(24 - cosy_third_tariff_hours - (1-cosy_offpeak_heat_demand_reduction)*cosy_second_tariff_hours)
    pc_2_with = cosy_offpeak_heat_demand_reduction*cosy_second_tariff_hours/(24 - (1-cosy_offpeak_heat_demand_reduction)*cosy_second_tariff_hours)
    pc_3_with = cosy_third_tariff_hours/(24 - (1-cosy_offpeak_heat_demand_reduction)*cosy_second_tariff_hours)
             
    energysplit_table = pd.DataFrame([['Room heating (with peak-time heating)', int(100*pc_2_with), int(100*(1-pc_2_with-pc_3_with)), int(100*pc_3_with)], 
                                      ['Room heating (without peak-time heating)', int(100*pc_2_without), int(100*(1-pc_2_without)), 0],
                                      ['Hot water heating', 100, 0, 0],
                                      ['Cooking', 0, 0, 100],
                                      ['EV', 100, 0, 0], 
                                      ['All other electricity', 100*pc_other_elec_cosy_offpeak, 100*(1-pc_other_elec_cosy_offpeak-pc_other_elec_cosy_peak), 100*pc_other_elec_cosy_peak]], 
                                      columns=['Energy Source', 'Demand in off-peak hours - 6 hours/day (%)', 'Demand in standard day rate hours - 15 hours/day (%)', 
                                               'Demand in peak hours - 3 hours/day (%)'])
    energysplit_table.set_index('Energy Source', inplace=True)
    st.table(energysplit_table.style.format(precision=0))

    st.subheader('3.  Other approximations and considerations')
    st.markdown(
    """
    It would not be possible to put together a perfectly accurate, but simple calculator comparing energy usage with and without a heat pump.
    This calculator necessarily gives only an indicative comparison, but in the majority of cases it should be representative when used correctly.
    Some examples as to why this calculator may be slightly inaccurate include:
    1. Switching from a boiler to a heat pump may change your heat demand independently of any energy saving measures you implement, for example you may save energy by overshooting the set temperature less, or you may have a different set temperature at night.
    2. Atypical annual variation in heating demand will result in different heat pump performance, as will weather conditions different from the UK average.
    3. Switching from a combi boiler to a heat pump will require you to install a hot water storage tank, which will impact the efficiency of heating hot water - some heat will be lost while storing the water, but less will be lost while waiting for the water to heat up on demand.
    4. Switching from gas to electric cooking (if you select gas cooking and disconnect from mains gas options) will change the energy demand of your cooking - electric is typically more efficient.       
    """
    )

is_submit1 = st.button(label='Update results')
st.divider()
result_container = st.container()

#leave some whitespace before adding the footer...
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')

st.markdown("This tool is a project of <a href='https://www.greenheatcoop.co.uk'>Green Heat Coop Ltd</a>.", unsafe_allow_html=True)
img = Image.open('web_banner.png')
st.image(img)

st.markdown("<a href='#linkto_top'>^ Back to top ^</a>", unsafe_allow_html=True)


#don't proceed until Update results has been pressed
if not is_submit1:
    st.stop()

#_______________Results calculation______________________
#prepare some variables

#calculate hot water kWh/L
GAS_HW_kWhperL = 4200 * hw_temp_raise/(3600 * 1000 * boiler_hw_eff)
IMMERSION_HW_kWhperL = 4200 * hw_temp_raise/(3600 * 1000 * immersion_hw_eff)

#_____________first do the current case____________________
if n_tariff_states == 3:
    elec_unit_eff = (pc_elec_third_tariff*elec_unit3) + (pc_elec_second_tariff*elec_unit2) + (1 - pc_elec_second_tariff - pc_elec_third_tariff)*elec_unit
    elec_unit_ev = elec_unit2
if n_tariff_states == 2:
    elec_unit_eff = (pc_elec_second_tariff*elec_unit2) + (1 - pc_elec_second_tariff)*elec_unit
    elec_unit_ev = elec_unit2
else:
    elec_unit_eff = elec_unit
    elec_unit_ev = elec_unit

elec_other_kWh = max(elec_total_kWh - elec_ev_kWh, 0)
elec_ev_kWh = elec_total_kWh - elec_other_kWh

costs_by_type = [['Current', 'Gas standing', gas_stand*3.65],
                ['Current', 'Gas unit',  gas_total_kWh * gas_unit/100],
                ['Current', 'Elec.  standing', elec_stand*3.65],
                ['Current', 'Elec.  unit', (elec_other_kWh * elec_unit_eff + elec_ev_kWh * elec_unit_ev)/100]] 
            
costs_total = (gas_stand + elec_stand)*3.65 + gas_total_kWh * gas_unit/100 + elec_other_kWh * elec_unit_eff/100 + elec_ev_kWh * elec_unit_ev/100

# hot water energy demand
if is_hw_gas:
    gas_hw_kWh = hw_lday * 365 * GAS_HW_kWhperL
    elec_hw_kWh = 0
else:
    gas_hw_kWh = 0
    elec_hw_kWh = hw_lday * 365 * IMMERSION_HW_kWhperL

#cooking demand - only done if gas
if is_cook_gas:
    gas_cook_kWh = gas_cook_kWhweek * 52
else:
    gas_cook_kWh = 0

#gas heating is remainder after hot water and cooking removed
gas_heat_kWh = gas_total_kWh - gas_hw_kWh - gas_cook_kWh

#see if there's any electric heating in addition:
if is_second_heatsource:
    if second_heatsource_type=='electric':
        elec_heat_kWh = second_heatsource_kWh
    else:
        elec_heat_kWh = 0    
    # elif second_heatsource_type=='other':
    #     other_total_kWh = second_heatsource_kWh
else:
    elec_heat_kWh = 0

#electric other is remainder after heating and hw removed
elec_other_kWh = elec_other_kWh-elec_heat_kWh-elec_hw_kWh

#if other electricity is now negative, assume user has overestimated either 
# their electric hw usage or electric heating - whichever the greater.
#reduce to bring other electricity to zero.
if elec_other_kWh < 0:
    if elec_hw_kWh > elec_heat_kWh:
        elec_hw_kWh += elec_other_kWh
    else: 
        elec_heat_kWh += elec_other_kWh

    elec_other_kWh = 0

#select carbon intensity of electricity
if is_elec_renewable:
    elec_kgCO2perkWh = ELEC_RENEW_kgCO2perkWh
else:
    elec_kgCO2perkWh = ELEC_AVE_kgCO2perkWh

#current energy usage table
energy_usage = [['Current', 'Heating', gas_heat_kWh+elec_heat_kWh, gas_heat_kWh*GAS_kgCO2perkWh+elec_heat_kWh*elec_kgCO2perkWh],
            ['Current', 'Hot water', gas_hw_kWh+elec_hw_kWh, gas_hw_kWh*GAS_kgCO2perkWh + elec_hw_kWh*elec_kgCO2perkWh],
            ['Current', 'Cooking', gas_cook_kWh, gas_cook_kWh*GAS_kgCO2perkWh],
            ['Current', 'EV', elec_ev_kWh, elec_ev_kWh*elec_kgCO2perkWh],
            ['Current', 'Other Elec.', elec_other_kWh, elec_other_kWh*elec_kgCO2perkWh]]                

energy_total = gas_total_kWh + elec_total_kWh
emissions_total = sum([gas_heat_kWh*GAS_kgCO2perkWh, gas_hw_kWh*GAS_kgCO2perkWh, gas_cook_kWh*GAS_kgCO2perkWh, elec_total_kWh*elec_kgCO2perkWh])

#___________now do the future/heat pump case_____________


def do_heat_pump_case(install_type, gas_heat_kWh, elec_heat_kWh, gas_hw_kWh, elec_hw_kWh, gas_cook_kWh):
    """
    install type either 'Typical' or 'Hi-performance'
    """

    #set heat pump performance coefficients to hi or typical:
    if install_type == 'Hi-performance':
        hp_heat_scop = hp_heat_scop_hi
        hp_hw_cop = hp_hw_cop_hi
    else:
        hp_heat_scop = hp_heat_scop_typ
        hp_hw_cop = hp_hw_cop_typ

    #calculate future heating energy - dependent upon second heat source (if any)
    if not is_second_heatsource:
        elec_heat_kWh = (1 - efficiency_boost) * gas_heat_kWh * boiler_heat_eff/hp_heat_scop
        gas_heat_kWh = 0
    else:
        if is_second_heatsource_remains:
            if second_heatsource_type=='gas':
                elec_heat_kWh = (1 - efficiency_boost) * (gas_heat_kWh - second_heatsource_kWh) * boiler_heat_eff/hp_heat_scop
                gas_heat_kWh = second_heatsource_kWh
            elif second_heatsource_type=='electric':
                elec_heat_kWh = second_heatsource_kWh + (1 - efficiency_boost) * gas_heat_kWh * boiler_heat_eff/hp_heat_scop
                gas_heat_kWh = 0
        else:
            if second_heatsource_type=='electric':
                elec_heat_kWh = (1 - efficiency_boost) * (gas_heat_kWh * boiler_heat_eff + second_heatsource_kWh)/hp_heat_scop
                gas_heat_kWh = 0
            elif second_heatsource_type=='gas': #same as the no second heatsource case, as we assume same efficiency as boiler
                elec_heat_kWh = (1 - efficiency_boost) * gas_heat_kWh * boiler_heat_eff/hp_heat_scop
                gas_heat_kWh = 0
            else:#other second heatsource, assume gas boiler efficiency, but not included in gas_heat_kWh
                elec_heat_kWh = (1 - efficiency_boost) * (gas_heat_kWh + second_heatsource_kWh) * boiler_heat_eff/hp_heat_scop
                gas_heat_kWh = 0

    #hot water
    if is_hw_gas:
        elec_hw_kWh = gas_hw_kWh * boiler_heat_eff/hp_hw_cop
    else:
        elec_hw_kWh = elec_hw_kWh * immersion_hw_eff/hp_hw_cop

    #gas cooking energy
    if is_cook_gas:
        if is_disconnect_gas:
            emissions_cook = gas_cook_kWh * elec_kgCO2perkWh
            elec_cook_kWh = gas_cook_kWh
            gas_cook_kWh = 0   
        else:
            emissions_cook = gas_cook_kWh * GAS_kgCO2perkWh
            elec_cook_kWh = 0
    else:
        emissions_cook = 0   
        gas_cook_kWh = 0 #redundant, for clarity
        elec_cook_kWh = 0 

    #totals
    elec_total_kWh = elec_other_kWh + elec_heat_kWh + elec_hw_kWh + elec_cook_kWh + elec_ev_kWh
    gas_total_kWh = gas_heat_kWh + gas_cook_kWh

    #new energy consumption and emissions table
    case_name = install_type + ' HP Install'
    energy_usage = [[case_name, 'Heating', gas_heat_kWh+elec_heat_kWh, gas_heat_kWh*GAS_kgCO2perkWh+elec_heat_kWh*elec_kgCO2perkWh],
                [case_name, 'Hot water', elec_hw_kWh, elec_hw_kWh*elec_kgCO2perkWh],
                [case_name, 'Cooking', gas_cook_kWh+elec_cook_kWh, emissions_cook],
                [case_name, 'EV', elec_ev_kWh, elec_ev_kWh*elec_kgCO2perkWh],
                [case_name, 'Other Elec.', elec_other_kWh, elec_other_kWh*elec_kgCO2perkWh]]   

    energy_total = elec_heat_kWh + elec_hw_kWh + elec_cook_kWh + elec_ev_kWh + elec_other_kWh + gas_heat_kWh + gas_cook_kWh
    emissions_total = sum([elec_heat_kWh*elec_kgCO2perkWh, gas_heat_kWh*GAS_kgCO2perkWh, elec_hw_kWh*elec_kgCO2perkWh, emissions_cook, elec_ev_kWh*elec_kgCO2perkWh, elec_other_kWh*elec_kgCO2perkWh])

    #update costs

    #don't include gas standing charge if disconnecting from gas
    if is_disconnect_gas:
        gas_stand_total = 0
    else:
        gas_stand_total = gas_stand*3.65

    if n_tariff_states == 2:
        #this pc of heating in second tariff 
        pc_heat_second_tariff = offpeak_heat_demand_reduction*second_tariff_hours/(24 - (1-offpeak_heat_demand_reduction)*second_tariff_hours)
        #all of hot water in second tariff (or free in summer solar)
        #none of cooking in second tariff
        #same pc of other elec in second tariff as original scenario

        if is_free_summer_hw: #those with solar panels can get free hot water for 4 months
            elec_unit_total_cost = elec_heat_kWh * (pc_heat_second_tariff*elec_unit2 + (1-pc_heat_second_tariff)*elec_unit) + \
                elec_hw_kWh*(2/3)*elec_unit2 + elec_cook_kWh*elec_unit + elec_ev_kWh*elec_unit_ev + elec_other_kWh*elec_unit_eff
        else:
            elec_unit_total_cost = elec_heat_kWh * (pc_heat_second_tariff*elec_unit2 + (1-pc_heat_second_tariff)*elec_unit) + \
                elec_hw_kWh*elec_unit2 + elec_cook_kWh*elec_unit + elec_ev_kWh*elec_unit_ev + elec_other_kWh*elec_unit_eff
        elec_unit_total_cost /= 100

    elif n_tariff_states == 3:
        #this pc of heating in second tariff 
        if turn_off_hp_in_peak_hours:
            pc_heat_second_tariff = offpeak_heat_demand_reduction*second_tariff_hours/(24 - third_tariff_hours - (1-offpeak_heat_demand_reduction)*second_tariff_hours)
            pc_heat_third_tariff = 0
        else:
            pc_heat_second_tariff = offpeak_heat_demand_reduction*second_tariff_hours/(24 - (1-offpeak_heat_demand_reduction)*second_tariff_hours)
            pc_heat_third_tariff = third_tariff_hours/(24 - (1-offpeak_heat_demand_reduction)*second_tariff_hours)

        #all of hot water in second tariff (or free in summer solar)
        #all of cooking in third tariff
        #same pc of other elec in second tariff as original scenario

        if is_free_summer_hw: #those with solar panels can get free hot water for 4 months
            elec_unit_total_cost = elec_heat_kWh * (pc_heat_second_tariff*elec_unit2 + pc_heat_third_tariff*elec_unit3 + (1-pc_heat_second_tariff-pc_heat_third_tariff)*elec_unit) + \
                elec_hw_kWh*(2/3)*elec_unit2 + elec_cook_kWh*elec_unit3 + elec_ev_kWh*elec_unit_ev + elec_other_kWh*elec_unit_eff
        else:
            elec_unit_total_cost = elec_heat_kWh * (pc_heat_second_tariff*elec_unit2 + pc_heat_third_tariff*elec_unit3 + (1-pc_heat_second_tariff-pc_heat_third_tariff)*elec_unit) + \
                elec_hw_kWh*elec_unit2 + elec_cook_kWh*elec_unit3 + elec_ev_kWh*elec_unit_ev + elec_other_kWh*elec_unit_eff
        elec_unit_total_cost /= 100

    else:
        if is_free_summer_hw: #those with solar panels can get free hot water for 4 months
            elec_unit_total_cost = (elec_total_kWh - elec_hw_kWh/3)*elec_unit/100
        else:
            elec_unit_total_cost = elec_total_kWh*elec_unit/100


    costs_by_type = [[case_name, 'Gas standing', gas_stand_total],
                    [case_name, 'Gas unit',  gas_total_kWh*gas_unit/100],
                    [case_name, 'Elec.  standing', elec_stand*3.65],
                    [case_name, 'Elec.  unit', elec_unit_total_cost]] 
    
    costs_total = sum([gas_stand_total, gas_total_kWh*gas_unit/100, elec_stand*3.65, elec_unit_total_cost])

    return energy_usage, costs_by_type, energy_total, emissions_total, costs_total

if switch_tariff_for_hp:
    n_tariff_states = 3
    elec_unit = elec_unit_cosy_standard
    elec_unit2 = elec_unit_cosy_offpeak
    elec_unit3 = elec_unit_cosy_peak
    pc_elec_second_tariff = pc_other_elec_cosy_offpeak
    pc_elec_third_tariff = pc_other_elec_cosy_peak
    second_tariff_hours = cosy_second_tariff_hours
    third_tariff_hours = cosy_third_tariff_hours
    elec_unit_eff = (pc_elec_third_tariff*elec_unit3) + (pc_elec_second_tariff*elec_unit2) + (1 - pc_elec_second_tariff - pc_elec_third_tariff)*elec_unit
    elec_unit_ev = elec_unit2
    offpeak_heat_demand_reduction = cosy_offpeak_heat_demand_reduction

energy_usage_typ, costs_by_type_typ, energy_total_typ, emissions_total_typ, costs_total_typ = \
do_heat_pump_case('Typical', gas_heat_kWh, elec_heat_kWh, gas_hw_kWh, elec_hw_kWh, gas_cook_kWh)

energy_usage_hi, costs_by_type_hi, energy_total_hi, emissions_total_hi, costs_total_hi = \
do_heat_pump_case('Hi-performance', gas_heat_kWh, elec_heat_kWh, gas_hw_kWh, elec_hw_kWh, gas_cook_kWh)

#if no EV, just delete EV data entries (index 3):
if elec_ev_kWh == 0:
    energy_usage.pop(3)
    energy_usage_hi.pop(3)
    energy_usage_typ.pop(3)

#if no gas heating, just delete cooking data entries (index 2):
if not is_cook_gas:
    energy_usage.pop(2)
    energy_usage_hi.pop(2)
    energy_usage_typ.pop(2)

#_______________Present results_________________________

with result_container:
    st.header('Results')
    st.write('The impact of installing a heat pump (and any other changes entered above) on your annual energy **costs**, '
    +'**CO$_2$ emissions** and **energy usage** are summarized below, for both a typical installation and a high-performing one.' +
    '  Please remember that these are only estimates and no estimate can be perfect.  '
    + 'You can find '
    + 'more information on the assumptions that have gone into generating these estimates on the *Further Information* tab.')

    with st.expander('Tell me more about high-performance installations'):
        st.write(
            """
            High-performance installations typically include design features such as:
            - A low operating flow temperature (e.g. 35$^\circ$C), utilising larger radiators if necessary
            - Flow controls designed to minimising cycling of the heat pump (regular switching on and off)
            - Weather compensation control 
            - Many other aspects of the system designed and installed to best practice 
            """
            )

    #calculate key values to show...
    df_costs = generate_df(costs_by_type, [costs_by_type_typ, costs_by_type_hi], ['Costs (£)'])
    df_energy = generate_df(energy_usage, [energy_usage_typ, energy_usage_hi], ['Energy (kWh)', 'Emissions (kg of CO2)'])

    #present costs, energy consumed and emissions side-by-side
    change_str2 = lambda v : '+' if v > 0 else '-'

    st.subheader('1. Annual Energy Costs')

    st.write('The costs of energy are changing rapidly at the moment in the UK, so the cost of energy may be significantly'
    + ' different by the time you have a heat pump installed.  To give the simplest, like-for-like comparison, '
    + 'we use a constant price of energy for the whole year based on the October 2025 domestic energy price cap (this is set to change in January 2026).'
    + '  These costs should only be used comparatively between the two cases and may be quite different from your energy bill in previous years.  '
    + '  You can edit the price of energy used in the *Advanced Settings* tab at the top of the page.')

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric('Current', f"£{costs_total:,.0f}")
    with c2:
        dcost = -100*(costs_total - costs_total_typ)/max(costs_total,1)
        st.metric('Typical HP Install', f"£{costs_total_typ:,.0f}", 
        delta=f"{change_str2(dcost)}£{abs(costs_total - costs_total_typ):,.0f} ({change_str2(dcost)} {abs(dcost):.0f}%)", delta_color='inverse')
    with c3:
        dcost = -100*(costs_total - costs_total_hi)/max(costs_total,1)
        st.metric('Hi-performance HP Install', f"£{costs_total_hi:,.0f}", 
        delta=f"{change_str2(dcost)} £{abs(costs_total - costs_total_hi):,.0f} ({change_str2(dcost)} {abs(dcost):.0f}%)", delta_color='inverse')

    bars = make_stacked_bar_horiz(df_costs, 'Costs (£)', 1)
    st.altair_chart(bars, use_container_width=True)

    st.subheader('2. Annual Emissions')
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric('Current', f"{emissions_total:,.0f} kg CO2")
    with c2:
        dcost = 100*(emissions_total_typ - emissions_total)/max(emissions_total, 0.0001)
        st.metric('Typical HP Install', f"{emissions_total_typ:,.0f} kg CO2", 
        delta=f"{change_str2(dcost)} {abs(emissions_total_typ - emissions_total):,.0f} kg CO2 ({change_str2(dcost)} {abs(dcost):.0f}%)", delta_color='inverse')
    with c3:
        dcost = 100*(emissions_total_hi - emissions_total)/max(emissions_total, 0.0001)
        st.metric('Hi-performance HP Install', f"{emissions_total_hi:,.0f} kg CO2", 
        delta=f"{change_str2(dcost)} {abs(emissions_total_hi - emissions_total):,.0f} kg CO2 ({change_str2(dcost)} {abs(dcost):.0f}%)", delta_color='inverse')

    bars = make_stacked_bar_horiz(df_energy, 'Emissions (kg of CO2)')
    st.altair_chart(bars, use_container_width=True)

    st.subheader('3. Annual Energy Usage')
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric('Current', f"{energy_total:,.0f} kWh")
    with c2:
        dcost = 100*(energy_total_typ - energy_total)/max(energy_total,1)
        st.metric('Typical HP Install', f"{energy_total_typ:,.0f} kWh", 
        delta=f"{change_str2(dcost)} {abs(energy_total_typ - energy_total):,.0f} kWh ({change_str2(dcost)} {abs(dcost):.0f}%)", delta_color='inverse')
    with c3:
        dcost = 100*(energy_total_hi - energy_total)/max(energy_total,1)
        st.metric('Hi-performance HP Install', f"{energy_total_hi:,.0f} kWh", 
        delta=f"{change_str2(dcost)} {abs(energy_total_hi - energy_total):,.0f} kWh ({change_str2(dcost)} {abs(dcost):.0f}%)", delta_color='inverse')

    bars = make_stacked_bar_horiz(df_energy, 'Energy (kWh)')
    st.altair_chart(bars, use_container_width=True)

    st.write('If you found this tool helpful - please share!')
