import streamlit as st
import pandas as pd
from helper import generate_df, make_stacked_bar, make_stacked_bar_narrow

about_markdown = 'This app has been developed by Chris Warwick, August 2022.'
st.set_page_config(layout="centered", menu_items={'Get Help': None, 'Report a Bug': None, 'About': about_markdown})

#COMMENTS on:
#TODO: inductive hob cooking more efficient than gas hob cooking 
#also for gas/electric oven
#TODO: hot water tank efficiency

#set default values
boiler_heat_eff = 0.88
boiler_hw_eff = 0.88
hw_temp_raise = 35
hp_heat_scop = 3.2
hp_hw_cop = 2.7

GAS_kgCO2perkWh = 0.21
ELEC_RENEW_kgCO2perkWh = 0
ELEC_AVE_kgCO2perkWh = 0.136

#write some reference infor to the sidebar
FILENAME_HW = 'hw_usage_examples.csv'
df_hw = pd.read_csv(FILENAME_HW, index_col=0)

FILENAME_COOK = 'cook_usage_examples.csv'
df_cook = pd.read_csv(FILENAME_COOK, index_col=0)

st.sidebar.header('Reference information')
st.sidebar.write('**Some typical amounts of water for different uses.**')
st.sidebar.table(df_hw)
st.sidebar.write('**Some typical amounts of energy used for cooking with gas appliances.**')
st.sidebar.table(df_cook)

st.title('Heat Pump Running Costs and Emissions Estimator')    
st.write('Use this tool to compare how a heat pump could change your annual energy bills and CO2 emissions.')
st.header('Inputs')
#Now go to main tabs
tab1, tab2, tab3 = st.tabs(["Basic Settings", "Advanced Settings", "Further Information"])

#basic settings
with tab1:
    
    st.subheader('1.  Annual energy consumption')
    st.write('Your projected annual energy consumption should be available on your energy bill.' +
    ' To customize the energy tariff used, see the Advanced Settings tab.')

    c1, c2 = st.columns(2)        
    with c1:
        elec_total_kWh = st.number_input('Annual projected electricity consumption (kWh).  Between 2500 - 3700 kWh is typical.', min_value=0, max_value=100000, value=2900, step=100)
    with c2:
        gas_total_kWh = st.number_input('Annual projected gas consumption (kWh).  Between 8000 - 16000 kWh is typical.', min_value=0, max_value=100000, value=12000, step=100)        

    is_elec_renewable = st.checkbox('I have a 100% renewable energy tariff', value=True)    

    st.subheader('2.  Gas usage')
    st.write('We need to understand a little a bit about how you use gas to estimate the heating requirements for your home.'
    + ' *You can find some reference values in the sidebar to the left to help here.*')
    c1, c2 = st.columns(2)
    with c1:
        is_hw_gas = st.checkbox('My hot water is heated with mains gas', value=False)

        if is_hw_gas:        
            st.write('How much hot water does your household use in a typical day?')
            #+' Typical hot water usage is between X and Y per person per day.')
            gas_hw_lday = st.number_input('The UK average is 140 litres per person per day.  Enter the total litres/day here.', 
            min_value=0, max_value=1000, value=350, step=1)
    with c2:
        
        is_cook_gas = st.checkbox('I cook with mains gas', value=False)

        if is_cook_gas:
            st.write('How much energy do you use cooking each week with gas?')
            gas_cook_kWhweek = st.number_input('A typical household uses between 5 and 12 kWh per week.  Enter total kWh/week here.', 
            min_value=0, max_value=100, value=8, step=1)

    st.subheader('3.  More complex set-ups')       
    
    is_second_heatsource = st.checkbox('I have a secondary heating source in addition to gas central heating', value=False)
    
    if is_second_heatsource:
        opts = ['gas', 'electric', 'other (not included in energy consumption calculations below)']
        second_heatsource_type = st.radio('My secondary heat source is:', opts)
        opts = ['Keep using my secondary heat source', 'Remove the secondary heat source and have the heat pump supply this heat']
        second_heatsource_remains = st.radio('In the heat pump scenario, I would...', opts)
        is_second_heatsource_remains = (second_heatsource_remains == opts[0])
        second_heatsource_kWh = st.number_input('Annual estimated energy usage of the secondary heatsource (kWh).  5% of your gas usage is used as an intial estimate.', min_value=0, max_value=100000, value=int(0.05*gas_total_kWh), step=10)

    ex = st.expander('I use solar thermal pannels to heat my hot water')
    with ex:
        st.write('Typically solar thermal energy does not provide all of your hot water heating needs.  In this case you should reduce the '
        +'hot water usage above to the fraction that will be heated by gas or the heat pump on an average day (across the whole year).')

    ex = st.expander('I generate some of my own electricity')
    with ex:
        st.write('1.  If you generate your electricity from solar energy, then bear in mind that the majority of the heating needed is '
        + 'during the winter when solar energy generation is at its lowest.  Therefore solar power will only reduce the cost of heating'
        + ' a small amount.  However it can provide energy for hot water heating outside the winter months, reducing costs there provided that '
        + 'the additional energy demand fits within your supply.'
        + '2.  If you generate your electricity from wind then...  ')

    st.subheader('4.  Switching to a heat pump')
    st.write('The efficiency of a heat pump can vary considerably between different installations, depending on the quality of the installation.  ' 
    + 'The difference between a typical versus quality installation could be as much as 30% in your heating bills.') 
    
    op1 = 'Assume a typical heat pump installation.'
    op2 = 'Assume a high-performance heat pump installation.'
    hp_quality = st.radio('Heat pump installation quality',[op1, op2])
    is_hi_quality_hp = (hp_quality == op2)

    st.write('Some efficiency measures are often implemented prior to or as part of a heat pump installation.' +
    ' Optionally, you can take these into account here.')
    is_hp_eff = st.checkbox('Include heating efficiency measures for the heat pump scenario', value=False)
    
    if is_hp_eff:
        op1 = 'Minor efficiency measures e.g.  draft proofing, (3% heating demand reduction)'
        op2 = 'Significant efficiency measures e.g.  cavity wall insulation and additional loft insulation (10% heating demand reduction)'
        op3 = 'Major house retrofit (40% heating demand reduction)'
        efficiency_boost = st.radio('Heating energy saving measures',[op1, op2, op3])

        if efficiency_boost == op1:
            efficiency_boost = 0.03
        elif efficiency_boost == op2:
            efficiency_boost = 0.1
        else: 
            efficiency_boost = 0.4
    else:
        efficiency_boost = 0
        
    st.write('If you can disconnect from gas completely, you may save money by not paying the gas standing charge.  Any gas fireplace, '
    + 'gas hobs, or gas oven would need to be removed and replaced with electric appliances or simply disconnected.')
    is_disconnect_gas = st.checkbox('Disconnect from mains gas in heat pump scenario', value=False)
    
    is_submit1 = st.button(label='Update results', key='b1')

#advanced settings
with tab2:

    st.subheader('1.  Energy prices')
    gas_stand = 28.0
    gas_unit = 10.3
    elec_stand = 46.0
    elec_unit = 34.0

    # st.write('If you have a fixed tariff')
    # ex = st.expander('I want to know more about the energy price caps')
    # with ex:
    #     st.write('From October 2022 ')

    op1 = 'Use the UK average domestic energy price cap for October 2022'
    op2 = 'Use custom unit and standing charges'

    charge_option = st.radio('Prices to use',[op1, op2])


    if charge_option == op2:
        c1, c2 = st.columns(2)
        
        with c1:    
            gas_stand = st.number_input('Gas standing charge (p/day)', min_value=0.0, max_value=100.0, value=gas_stand, step=0.01)
            gas_unit = st.number_input('Gas unit cost (p/kWh)', min_value=0.0, max_value=100.0, value=gas_unit, step=0.01)

        with c2:    
            elec_stand = st.number_input('Electricity standing charge (p/day)', min_value=0.0, max_value=100.0, value=elec_stand, step=0.01)        
            elec_unit = st.number_input('Electricity unit cost (p/kWh)', min_value=0.0, max_value=100.0, value=elec_unit, step=0.01)  
    
        
    st.subheader('2.  Device performance')
    st.write('Either a typical or high-performance heat pump installation can be selected in the basic settings tab.  '
    + ' The heat pump system performance is described by the seasonal coefficient of performance (SCOP).')
    c1, c2, c3 = st.columns([3, 3, 4])
    
    with c1:
        st.write('_Average boiler efficiency_')
        boiler_heat_eff = st.number_input('When space heating', min_value=0.0, max_value=1.00, value=0.88, step=0.01)
        boiler_hw_eff = st.number_input('When hot water heating', min_value=0.0, max_value=1.00, value=0.88, step=0.01)
    with c2:
        st.write('*Typical heat pump SCOP*')
        hp_heat_scop_typ = st.number_input('When space heating', min_value=0.1, max_value=10.0, value=3.2, step=0.1, key='typ')
        hp_hw_cop_typ = st.number_input('When hot water heating', min_value=0.1, max_value=10.0, value=2.7, step=0.1, key='typ')
    with c3:
        st.write('*High-performance heat pump SCOP*')
        hp_heat_scop_hi = st.number_input('When space heating', min_value=0.1, max_value=10.0, value=3.8, step=0.1, key='hi')
        hp_hw_cop_hi = st.number_input('When hot water heating', min_value=0.1, max_value=10.0, value=2.7, step=0.1, key='hi')

    st.subheader('3.  Hot Water Temperature')
    st.write('Typical mains cold water may be at 15$^{\circ}$C, while a comfortable shower temperature is 37-38$^{\circ}$C.  The gas boiler '
    + 'will supply hot water hotter than this, which is then mixed with cold water, but the total energy used is similar to providing '
    +'water at this temperature.')
    hw_temp_raise = st.number_input('Cold and hot water temperature difference (degrees C)', min_value=1, max_value=100, step=1, 
    help='The typical difference in temperature between mains water and hot water as used.', value=22)

with tab3:
    st.subheader('1.  Carbon intensity')
    st.write("We use standard values for carbon intensity of different energy sources as set in the Standard Assessment Procedure (SAP) 10.2, "
    +"released December 2021.  These values only consider the CO_2 equivalent emissions associated per unit of energy, not the embedded emissions of the "
    + "energy generation and transmission infrastructure.  These values are: ")
    st.table(pd.DataFrame([['Mains Gas', GAS_kgCO2perkWh], ['Electricity (grid average)', ELEC_AVE_kgCO2perkWh],
    ['Electricity (renewable only)', ELEC_RENEW_kgCO2perkWh]], columns=['Energy Source', 'CO_2 Equivalent Emissions (kgCO_2/kWh)']))

    st.subheader('2.  Other approximations and considerations')
    st.markdown(
    """
    It would not be possible to put together a perfectly accurate, but simple calculator comparing energy usage with and without a heat pump.
    This calculator necessarily gives only an indicative comparison, but in the majority of cases it should be representative when used correctly.
    Some examples as to why this calculator may be slightly inaccurate include:
    1. Switching from a boiler to a heat pump may change your heat demand independently of any energy saving measures you implement, for example you may save energy by overshooting the set temperature less, or you may have a different set temperature at night.
    2. Atypical annual variation in heating demand will result in different heat pump performance, as will weather conditions different from the UK average.
    3. Switching from a combi boiler to a heat pump will require you to install a hot water storage tank, which will impact the efficiency of heating hot water - some heat will be lost while storing the water, but less will be lost while waiting for the water to heat up on demand.
    4. Switching from gas to electric cooking (if you select Gas cooking and disconnect from mains gas options) will change the energy demand of your cooking - electric is typically more efficient.       
    """
    )

    is_submit2 = st.button(label='Update results', key='b2')

if not (is_submit1 or is_submit2):
    st.stop()

#calculate some derived values
GAS_HW_kWhperL = 4200 * hw_temp_raise/(3600 * 1000 * boiler_hw_eff)

if is_hi_quality_hp:
    hp_heat_scop = hp_heat_scop_hi
    hp_hw_cop = hp_hw_cop_hi
else:
    hp_heat_scop = hp_heat_scop_typ
    hp_hw_cop = hp_hw_cop_typ

#first do the current case
#don't worry about fixed/non-fixed contract for now, or future energy costs
costs_by_type = [['Current', 'Gas standing', gas_stand*3.65],
                ['Current', 'Gas unit',  gas_total_kWh * gas_unit/100],
                ['Current', 'Elec.  standing', elec_stand*3.65],
                ['Current', 'Elec.  unit', elec_total_kWh * elec_unit/100]] 
            
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

if is_second_heatsource:
    if second_heatsource_type=='electric':
        elec_heat_kWh = second_heatsource_kWh
    else:
        elec_heat_kWh = 0    
    # elif second_heatsource_type=='other':
    #     other_total_kWh = second_heatsource_kWh
else:
    elec_heat_kWh = 0

elec_other_kWh = elec_total_kWh-elec_heat_kWh

if is_elec_renewable:
    elec_kgCO2perkWh = ELEC_RENEW_kgCO2perkWh
else:
    elec_kgCO2perkWh = ELEC_AVE_kgCO2perkWh

energy_usage = [['Current', 'Heating', gas_heat_kWh+elec_heat_kWh, gas_heat_kWh*GAS_kgCO2perkWh+elec_heat_kWh*elec_kgCO2perkWh],
            ['Current', 'Hot water', gas_hw_kWh, gas_hw_kWh*GAS_kgCO2perkWh],
            ['Current', 'Cooking', gas_cook_kWh, gas_cook_kWh*GAS_kgCO2perkWh],
            ['Current', 'Other Elec.', elec_other_kWh, elec_other_kWh*elec_kgCO2perkWh]]                

energy_total = gas_total_kWh + elec_total_kWh
emissions_total = sum([gas_heat_kWh*GAS_kgCO2perkWh, gas_hw_kWh*GAS_kgCO2perkWh, gas_cook_kWh*GAS_kgCO2perkWh, elec_total_kWh*elec_kgCO2perkWh])

#now do the future/heat pump case
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

elec_hw_kWh = gas_hw_kWh * boiler_heat_eff/hp_hw_cop

elec_total_kWh_new = elec_other_kWh + elec_heat_kWh + elec_hw_kWh
gas_total_kWh_new = gas_heat_kWh

if is_cook_gas:
    if is_disconnect_gas:
        emissions_cook = gas_cook_kWh * elec_kgCO2perkWh
        elec_total_kWh_new += gas_cook_kWh        
    else:
        emissions_cook = gas_cook_kWh * GAS_kgCO2perkWh
        gas_total_kWh_new += gas_cook_kWh
else:
    emissions_cook = 0    

energy_usage_new = [['Heat Pump', 'Heating', gas_heat_kWh+elec_heat_kWh, gas_heat_kWh*GAS_kgCO2perkWh+elec_heat_kWh*elec_kgCO2perkWh],
            ['Heat Pump', 'Hot water', elec_hw_kWh, elec_hw_kWh*elec_kgCO2perkWh],
            ['Heat Pump', 'Cooking', gas_cook_kWh, emissions_cook],
            ['Heat Pump', 'Other Elec.', elec_total_kWh, elec_total_kWh*elec_kgCO2perkWh]]   

energy_total_new = elec_heat_kWh + elec_hw_kWh + gas_cook_kWh + elec_other_kWh
emissions_total_new = sum([elec_heat_kWh*elec_kgCO2perkWh, elec_hw_kWh*elec_kgCO2perkWh, emissions_cook, elec_other_kWh*elec_kgCO2perkWh])

if is_disconnect_gas:
    gas_stand_total_new = 0
else:
    gas_stand_total_new = gas_stand*3.65

costs_by_type_new = [['Heat Pump', 'Gas standing', gas_stand_total_new],
                ['Heat Pump', 'Gas unit',  gas_total_kWh_new*gas_unit/100],
                ['Heat Pump', 'Elec.  standing', elec_stand*3.65],
                ['Heat Pump', 'Elec.  unit', elec_total_kWh_new*elec_unit/100]] 

costs_total_new = sum([gas_stand_total_new, gas_total_kWh_new*gas_unit/100, elec_stand*3.65, elec_total_kWh_new*elec_unit/100])

st.header('Results')
st.write('The impact of installing a heat pump (and any other changes entered above) on your annual bill, '
+'annual energy consumption and annual household emissions are summarized below.' +
' Please remember that these are only estimates and no estimate can be perfect.  '
+ 'The costs of energy are changing rapidly at the moment in the UK, so the cost of energy may be significantly'
+ ' different by the time you have a heat pump installed.  To give the simplest, like-for-like comparison, '
+ 'we use a constant price of energy for the whole year based on the most recent domestic energy price cap.'
+ ' These costs should only be used comparatively between the two cases and may be quite different from your energy bill in previous years.  '
+ ' You can edit the price of energy used in the Advanced Settings tab at the top of the page, where you will also find '
+ 'more information on the assumptions that have gone into generating these estimates.')
# st.write("Installing a heat pump is expected to reduce your household annual CO2 emissions by "
#         + f"**{(emissions_total-emissions_total_new)/1000:.2f} tonnes**, from "
#         + f"**{emissions_total/1000:.2f} tonnes** to **{emissions_total_new/1000:.2f} tonnes**.")

# if costs_total_new < costs_total:
#     change_str = 'decrease'    
# else:
#     change_str = 'increase'
    
# st.write(f"Your annual energy costs are expected to {change_str} by "
#         f"**£{abs(costs_total_new-costs_total):.0f}** from "
#         + f"**£{costs_total:.0f}** to **£{costs_total_new:.0f}**.")


df_costs = generate_df(costs_by_type, costs_by_type_new, ['Costs (£)'])
df_energy = generate_df(energy_usage, energy_usage_new, ['Energy (kWh)', 'Emissions (kgCO2e)'])

cost_change = (costs_total_new - costs_total)
energy_change = (energy_total_new - energy_total)
emissions_change = (emissions_total_new - emissions_total)
cost_change_pc = 100 * (costs_total_new - costs_total) / costs_total
energy_change_pc = 100 * (energy_total_new - energy_total) / energy_total
emissions_change_pc = 100 * (emissions_total_new - emissions_total) / emissions_total
change_str2 = lambda v : '+' if v > 0 else '-'

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