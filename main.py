import streamlit as st
import pandas as pd
from helper import generate_df, make_stacked_bar_narrow

#__________ set default values______________
#efficiencies and performance coefficients - default values
boiler_heat_eff = 0.88
boiler_hw_eff = 0.88
immersion_hw_eff = 1
#typical heat pump performance:
hp_heat_scop_typ = 3.2
hp_hw_cop_typ = 2.7
#hi heat pump performance
hp_heat_scop_hi = 3.8
hp_hw_cop_hi = 2.7

#Raise in temp (degC) from mains water to hot water AS USED
hw_temp_raise_default = 23

#carbon intensity values taken from SAP 10.2 (dec 2021)
GAS_kgCO2perkWh = 0.21
ELEC_RENEW_kgCO2perkWh = 0
ELEC_AVE_kgCO2perkWh = 0.136

# price cap October 2022 gas and electricity domestic standing and unit charges
gas_stand = 28.0
gas_unit = 10.3
elec_stand = 46.0
elec_unit = 34.0

# efficincy measures to choose from
efficiency_opts = [('Draft proofing and/or door insulation (3%)', 0.03),
                    ('Increased loft insulation (5%)', 0.05),
                    ('Improved window glazing (5%)', 0.05),
                    ('Cavity wall insulation (10%)', 0.1),
                    ('Underfloor insulation (10%)', 0.1),
                    ('Internal or external solid wall insulation (15%)', 0.15)]
#____________ Page info________________________________________

about_markdown = 'This app has been developed by Chris Warwick, August-October 2022.'
st.set_page_config(layout="centered", menu_items={'Get Help': None, 'Report a Bug': None, 'About': about_markdown})

#__________write some reference info to the sidebar____________
df_hw = pd.DataFrame([['Washing up', 15], ['5 min water-saving shower', 30], ['10 min power shower', 150], ['Bath', 100]],
columns=['Use', 'Hot water used (L)'])
df_hw.set_index('Use', inplace=True)

df_cook = pd.DataFrame([['Gas hob', 0.8], ['Gas grill', 1], ['Gas oven', 1.5]],
columns=['Use', 'Gas consumption per use (kWh)'])
df_cook.set_index('Use', inplace=True)

st.sidebar.header('Reference information')
st.sidebar.write('**Some typical amounts of water for different uses.**')
st.sidebar.table(df_hw)
st.sidebar.write('**Some typical amounts of energy used for cooking with gas appliances.**')
st.sidebar.table(df_cook)

#___________Main page__________________________________________
st.title('Heat Pump Running Costs and Emissions Estimator')    
st.write('Use this tool to compare how a heat pump could change your annual energy bills and CO$_2$ emissions.  '
+ 'Enter some information below, and once you are ready, press the Update Results button at the bottom to see the comparison.  ' +
'This tool is currently only suited to those who use a gas boiler as the main source of heat for their house.')
st.write('To calculate an estimate of the cost of installing a heat pump, see the Nesta tool here: http://asf-hp-cost-demo-l-b-1046547218.eu-west-1.elb.amazonaws.com/')
#st.header('Inputs')

#Now go to main tabs
tab1, tab2, tab3 = st.tabs(["Basic Settings", "Advanced Settings", "Further Information"])


with tab1:
    #_______________basic settings_________________________________________
    st.subheader('1.  Annual energy consumption')
    st.write('Enter your projected annual energy consumption, which should be available on your energy bill.' +
    ' To customize the energy tariff used, see the Advanced Settings tab.')

    c1, c2 = st.columns(2)        
    with c1:
        elec_total_kWh = st.number_input('Annual electricity consumption (kWh).  Between 2500 - 3700 kWh is typical.', min_value=0, max_value=100000, value=2900, step=100)
    with c2:
        gas_total_kWh = st.number_input('Annual gas consumption (kWh).  Between 8000 - 16000 kWh is typical, but some have much higher.', min_value=0, max_value=100000, value=12000, step=100)        

    is_elec_renewable = st.checkbox('I have a 100% renewable energy tariff', value=False)    

    st.subheader('2.  Hot water usage')
    st.write('How is your hot water heated?  If you have solar thermal panels to heat your hot water, select the source which tops-up the temperature when needed.')
    hw_source = st.radio('Hot water heat source:', ['gas', 'electricity (immersion heater or electric boiler)'])
    is_hw_gas = (hw_source=='gas')

    st.write('How much hot water does your household use in a typical day?  *You can find some reference values in the sidebar to the left to help here.*')
    hw_lday = st.number_input('The UK average is 140 litres per person per day.  Enter the total litres/day here:', 
    min_value=0, max_value=1000, value=350, step=1)

    st.subheader('3.  Cooking')
    is_cook_gas = st.checkbox('I cook with mains gas', value=False)

    if is_cook_gas:
        st.write('How much energy do you use cooking each week with gas? *You can find some reference values in the sidebar to the left to help here.*')
        gas_cook_kWhweek = st.number_input('A typical household uses between 5 and 12 kWh per week.  Enter total kWh/week here:', 
        min_value=0, max_value=100, value=8, step=1)

    st.subheader('4.  More complex set-ups')       
    
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
        st.write('When entering the annual electricity consumption above, only input the annual *imported* electricity. The results below will then only relate to the imported energy and emissions.')

    with st.expander('I use solar thermal pannels to heat my hot water'):
        st.write('Typically solar thermal energy does not provide all of your hot water heating needs.  In this case you should reduce the '
        +'hot water usage above to the fraction that will be heated by other sources on an average day (across the whole year).')

    st.subheader('5.  Switching to a heat pump')
    st.write('The efficiency of a heat pump can vary considerably between different installations, depending on the quality of the installation.  ' 
    + 'The difference between a typical versus quality installation could be as much as 30% in your heating bills.') 
    
    op1 = 'Assume a typical heat pump installation'
    op2 = 'Assume a high-performance heat pump installation'
    hp_quality = st.radio('Heat pump installation quality:',[op1, op2])
    is_hi_quality_hp = (hp_quality == op2)
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

    st.write('Some efficiency measures are often implemented prior to or as part of a heat pump installation.' +
    ' Optionally, you can take these into account here.')    
    
    efficiency_boost = 0
    with st.expander('Energy efficiency measures'):         
        st.write('Approximate heating demand reduction for each measure is shown in brackets, based on average measured reductions in heat demand rather than quoted reductions.')
        
        #make a checkbox for each efficiency boost we have:
        for (lab, boost) in efficiency_opts:

            is_op = st.checkbox(lab, value=False)
            if is_op:
                efficiency_boost += boost                
        
    st.write('If you can disconnect from gas completely, you may save money by not paying the gas standing charge.  Any gas fireplace, '
    + 'gas hobs, or gas oven would need to be removed and replaced with electric appliances or simply disconnected.')
    is_disconnect_gas = st.checkbox('Disconnect from mains gas in heat pump scenario', value=False)

#____________advanced settings______________________
with tab2:

    st.subheader('1.  Energy prices')

    op1 = 'Use the UK-average domestic energy price cap for direct debit paying customers for the period beginning October 2022'
    op2 = 'Use custom unit and standing charges'

    charge_option = st.radio('Prices to use:',[op1, op2])

    #if user selects to input their own energy tariff
    if charge_option == op2:
        c1, c2 = st.columns(2)
        
        with c1:    
            gas_stand = st.number_input('Gas standing charge (p/day):', min_value=0.0, max_value=100.0, value=gas_stand, step=0.01)
            gas_unit = st.number_input('Gas unit cost (p/kWh):', min_value=0.0, max_value=100.0, value=gas_unit, step=0.01)

        with c2:    
            elec_stand = st.number_input('Electricity standing charge (p/day):', min_value=0.0, max_value=100.0, value=elec_stand, step=0.01)        
            elec_unit = st.number_input('Electricity unit cost (p/kWh):', min_value=0.0, max_value=100.0, value=elec_unit, step=0.01)  
    
        
    st.subheader('2.  Device performance')
    st.write('Either a typical or high-performance heat pump installation can be selected in the basic settings tab.  '
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
    st.write('Typical mains cold water may be at 15$^{\circ}$C, while a comfortable shower temperature is 37-38$^{\circ}$C.  The gas boiler '
    + 'will supply hot water hotter than this, which is then mixed with cold water, but the total energy used per litre is similar to providing '
    +'water at this temperature.')
    hw_temp_raise = st.number_input('Cold and hot water temperature difference (degrees C):', min_value=1, max_value=100, step=1, 
    help='The typical difference in temperature between mains water and hot water as used.', value=hw_temp_raise_default)

with tab3:
    #____________ Further Information____________________________
    st.subheader('1.  Carbon intensity')
    st.write("We use standard values for carbon intensity of different energy sources as set in the Standard Assessment Procedure (SAP) 10.2, "
    +"released December 2021.  These values only consider the $CO_2$ equivalent emissions associated per unit of energy, not the embedded emissions of the "
    + "energy generation and transmission infrastructure.  These values are: ")
    costs_table = pd.DataFrame([['Mains Gas', GAS_kgCO2perkWh], ['Electricity (grid average)', ELEC_AVE_kgCO2perkWh],
    ['Electricity (renewable only)', ELEC_RENEW_kgCO2perkWh]], columns=['Energy Source', 'CO2 Equivalent Emissions (kgCO2/kWh)'])
    costs_table.set_index('Energy Source', inplace=True)
    st.table(costs_table)

    st.subheader('2.  Other approximations and considerations')
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

#don't proceed until Update results has been pressed
if not is_submit1:
    st.stop()

#_______________Results calculation______________________
#prepare some variables

#calculate hot water kWh/L
GAS_HW_kWhperL = 4200 * hw_temp_raise/(3600 * 1000 * boiler_hw_eff)
IMMERSION_HW_kWhperL = 4200 * hw_temp_raise/(3600 * 1000 * immersion_hw_eff)

#set heat pump performance coefficients to hi or typical:
if is_hi_quality_hp:
    hp_heat_scop = hp_heat_scop_hi
    hp_hw_cop = hp_hw_cop_hi
else:
    hp_heat_scop = hp_heat_scop_typ
    hp_hw_cop = hp_hw_cop_typ

#_____________first do the current case____________________
costs_by_type = [['Current', 'Gas standing', gas_stand*3.65],
                ['Current', 'Gas unit',  gas_total_kWh * gas_unit/100],
                ['Current', 'Elec.  standing', elec_stand*3.65],
                ['Current', 'Elec.  unit', elec_total_kWh * elec_unit/100]] 
            
costs_total = (gas_stand + elec_stand)*3.65 + gas_total_kWh * gas_unit/100 + elec_total_kWh * elec_unit/100

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
elec_other_kWh = elec_total_kWh-elec_heat_kWh-elec_hw_kWh

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
            ['Current', 'Other Elec.', elec_other_kWh, elec_other_kWh*elec_kgCO2perkWh]]                

energy_total = gas_total_kWh + elec_total_kWh
emissions_total = sum([gas_heat_kWh*GAS_kgCO2perkWh, gas_hw_kWh*GAS_kgCO2perkWh, gas_cook_kWh*GAS_kgCO2perkWh, elec_total_kWh*elec_kgCO2perkWh])

#___________now do the future/heat pump case_____________

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

#totals - excluding gas cooking if present
elec_total_kWh_new = elec_other_kWh + elec_heat_kWh + elec_hw_kWh
gas_total_kWh_new = gas_heat_kWh

#add gas cooking energy on
if is_cook_gas:
    if is_disconnect_gas:
        emissions_cook = gas_cook_kWh * elec_kgCO2perkWh
        elec_total_kWh_new += gas_cook_kWh        
    else:
        emissions_cook = gas_cook_kWh * GAS_kgCO2perkWh
        gas_total_kWh_new += gas_cook_kWh
else:
    emissions_cook = 0    

#new energy consumption and emissions table
energy_usage_new = [['Heat Pump', 'Heating', gas_heat_kWh+elec_heat_kWh, gas_heat_kWh*GAS_kgCO2perkWh+elec_heat_kWh*elec_kgCO2perkWh],
            ['Heat Pump', 'Hot water', elec_hw_kWh, elec_hw_kWh*elec_kgCO2perkWh],
            ['Heat Pump', 'Cooking', gas_cook_kWh, emissions_cook],
            ['Heat Pump', 'Other Elec.', elec_other_kWh, elec_other_kWh*elec_kgCO2perkWh]]   

energy_total_new = elec_heat_kWh + elec_hw_kWh + gas_cook_kWh + elec_other_kWh
emissions_total_new = sum([elec_heat_kWh*elec_kgCO2perkWh, elec_hw_kWh*elec_kgCO2perkWh, emissions_cook, elec_other_kWh*elec_kgCO2perkWh])

#update costs

#don't include gas standing charge if disconnecting from gas
if is_disconnect_gas:
    gas_stand_total_new = 0
else:
    gas_stand_total_new = gas_stand*3.65

costs_by_type_new = [['Heat Pump', 'Gas standing', gas_stand_total_new],
                ['Heat Pump', 'Gas unit',  gas_total_kWh_new*gas_unit/100],
                ['Heat Pump', 'Elec.  standing', elec_stand*3.65],
                ['Heat Pump', 'Elec.  unit', elec_total_kWh_new*elec_unit/100]] 

costs_total_new = sum([gas_stand_total_new, gas_total_kWh_new*gas_unit/100, elec_stand*3.65, elec_total_kWh_new*elec_unit/100])

#_______________Present results_________________________

st.header('Results')
st.write('The impact of installing a heat pump (and any other changes entered above) on your annual bill, '
+'annual energy consumption and annual household emissions are summarized below.' +
'  Please remember that these are only estimates and no estimate can be perfect.  '
+ 'The costs of energy are changing rapidly at the moment in the UK, so the cost of energy may be significantly'
+ ' different by the time you have a heat pump installed.  To give the simplest, like-for-like comparison, '
+ 'we use a constant price of energy for the whole year based on the most recent domestic energy price cap.'
+ '  These costs should only be used comparatively between the two cases and may be quite different from your energy bill in previous years.  '
+ '  You can edit the price of energy used in the Advanced Settings tab at the top of the page, where you will also find '
+ 'more information on the assumptions that have gone into generating these estimates.')

#calculate key values to show...
df_costs = generate_df(costs_by_type, costs_by_type_new, ['Costs (£)'])
df_energy = generate_df(energy_usage, energy_usage_new, ['Energy (kWh)', 'Emissions (kgCO2e)'])

cost_change = (costs_total_new - costs_total)
energy_change = (energy_total_new - energy_total)
emissions_change = (emissions_total_new - emissions_total)
cost_change_pc = 100 * (costs_total_new - costs_total) / costs_total
energy_change_pc = 100 * (energy_total_new - energy_total) / energy_total
emissions_change_pc = 100 * (emissions_total_new - emissions_total) / emissions_total
change_str2 = lambda v : '+' if v > 0 else '-'

#present costs, energy consumed and emissions side-by-side
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader('Costs')
    st.metric('Annual Change', f"{change_str2(cost_change_pc)} £{abs(cost_change):.0f}", 
    delta=f"{change_str2(cost_change_pc)} {abs(cost_change_pc):.0f}%", delta_color='inverse')
    bars = make_stacked_bar_narrow(df_costs, 'Costs (£)', 1)
    st.altair_chart(bars, use_container_width=True)
with c2:
    st.subheader('Energy Consumed')
    st.metric('Annual Change', f"{change_str2(energy_change_pc)} {abs(energy_change):.0f} kWh", 
    delta=f"{change_str2(energy_change_pc)} {abs(energy_change_pc):.0f}%", delta_color='inverse')
    bars = make_stacked_bar_narrow(df_energy, 'Energy (kWh)')
    st.altair_chart(bars, use_container_width=True)
with c3: 
    st.subheader('Emissions')
    st.metric('Annual Change', f"{change_str2(emissions_change_pc)} {abs(emissions_change):.0f} kgCO2e", 
    delta=f"{change_str2(emissions_change_pc)} {abs(emissions_change_pc):.0f}%", delta_color='inverse')
    bars = make_stacked_bar_narrow(df_energy, 'Emissions (kgCO2e)')
    st.altair_chart(bars, use_container_width=True)

st.write('If you found this tool helpful - please share!')