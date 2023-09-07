import requests
import pandas as pd
import time
# web_url = 'https://data.census.gov/table?q=B16001+&g=010XX00US,$0400000&tid=ACSDT5Y2020.B16001'

API_KEY = ''
#go to https://api.census.gov/data/key_signup.html to signup for an api key and put it into the API_KEY variable as a string
CENSUS_YEAR = '2015'
STATE = 1
#change state value to whichever state data is desired, use for loop at bottom of file to get all states.
def get_query_url(state_index, value_index):
    if state_index < 10:
        state_index = f'0{state_index}'
    else:
        state_index = f'{state_index}'
    if value_index < 10:
        value_index = f'00{value_index}'
    elif value_index < 100:
        value_index = f'0{value_index}'
    else:
        value_index = f'{value_index}'
    if int(value_index) < 120:
        query_url = f'https://api.census.gov/data/2015/acs/acs5?get=NAME,B16001_{value_index}E,B16001_{value_index}M&for=county&in=state:{state_index}&key={API_KEY}'
    else:
        query_url = f'https://api.census.gov/data/2021/acs/acs1?get=NAME,B16001_{value_index}E,B16001_{value_index}M&for=county&in=state:{state_index}&key={API_KEY}'
    return query_url

def get_variable_table_df():
    print('comeon')
    variable_table_url = 'https://api.census.gov/data/2020/acs/acs5/variables.html'
    print('???')
    v_table = pd.read_html(variable_table_url)
    variable_df = pd.DataFrame(v_table[0])
    print('lll')
    return variable_df

def get_language_spoken_index(variable_table):
    print('hur')
    start_index = variable_table[variable_table['Name'] == 'B16001_001E'].index[0]
    end_index = variable_table[variable_table['Name'] == 'B16001_128E'].index[0]
    return [start_index, end_index + 1]

def get_variable_names(variable_table, indices):
    print('bruh')
    language_spoken_variables = ",".join(variable_table.iloc[indices[0]: indices[1]]['Label'].values).replace(', ', ' ').replace('!!', ' ').replace(':', '').split(',')
    old_variables = language_spoken_variables
    no_repeats = [language_spoken_variables[1]]
    language_spoken_variables.pop(0)
    language_spoken_variables.pop(0)


    for i in language_spoken_variables:
        print(i)
        if i.__contains__("only"):
            no_repeats.append(i.replace('Estimate Total ', ''))
        elif i.__contains__("Speak"):
            continue
        else:
            no_repeats.append(i.replace('Estimate Total ', ''))
    return no_repeats, old_variables

def get_full_variable_names():
    the_list = eval(get_query_text(get_query_url(STATE, 1)))
    other_list = eval(get_query_text(get_query_url(STATE, 120)).replace('null', 'None'))
    the_list.pop(0)
    other_list.pop(0)
    the_list.pop(0)
    other_list.pop(0)
    full_names = []

    for i in var_names:
        if var_names.index(i) < 41:
            list = the_list
        else:
            list = other_list
        for county in list:
            full_names.append(i)
    return full_names

def get_query_text(query_url):
    response = requests.get(query_url)
    return response.text

def get_state_county_fips():
    state_names = []
    county_names = []
    fips = []
    full_list = eval(get_query_text(get_query_url(STATE, 1)))
    other_list = eval(get_query_text(get_query_url(STATE, 120)).replace('null', 'None'))
    full_list.pop(0)
    other_list.pop(0)
    full_list.pop(0)
    other_list.pop(0)
    for var in var_names:
        if var_names.index(var) > 40:
            list = other_list
        else:
            list = full_list
        for county in list:
            try:
                county_names.append(county[0][:county[0].index(',')])
                state_names.append(county[0][county[0].index(',') + 2:])
                fips.append(str(county[3]) + str(county[4]))
            except Exception as bruh:
                print(bruh, var, county)
    return state_names, county_names, fips


def get_census_year():
    census_years = []
    full_list = eval(get_query_text(get_query_url(state_index=STATE, value_index=1)))
    other_list = eval(get_query_text(get_query_url(state_index=STATE, value_index=120)).replace('null', 'None'))
    full_list.pop(0)
    other_list.pop(0)
    full_list.pop(0)
    other_list.pop(0)
    for var in var_names:
        if var_names.index(var) < 41:
            CENSUS_YEAR = '2015'
            list = full_list
        else:
            CENSUS_YEAR = '2021'
            list = other_list
        for county in list:
            census_years.append(CENSUS_YEAR)
    return census_years

def get_county_values():
    county_totals = []
    county_pos_estimates = []
    county_neg_estimates = []
    county_pos_errors = []
    county_neg_errors = []
    county_totals_errors = []
    for variable in old_names:
        print(variable)
        index = old_names.index(variable)
        if index > 118:
            try:
                full_list = eval(get_query_text(get_query_url(STATE, index + 1)).replace('null', 'None'))
                full_list.pop(0)
                full_list.pop(0)
                if variable.__contains__('less'):
                    for county in full_list:
                        try:
                            if int(county[2]) < 0:
                                county_neg_estimates.append(county[1])
                                county_neg_errors.append(None)
                                continue
                        except:
                            pass
                        county_neg_estimates.append(county[1])
                        county_neg_errors.append(county[2])
                elif variable.__contains__('very well'):
                    for county in full_list:
                        try:
                            if int(county[2]) < 0:
                                county_pos_estimates.append(county[1])
                                county_pos_errors.append(None)
                                continue
                        except:
                            pass
                        county_pos_estimates.append(county[1])
                        county_pos_errors.append(county[2])
                else:
                    for county in full_list:
                        try:
                            if int(county[2]) < 0:
                                county_totals.append(county[1])
                                county_totals_errors.append(None)
                                continue
                        except:
                            pass
                        county_totals.append(county[1])
                        county_totals_errors.append(county[2])
            except Exception as e:
                print(e, STATE, variable)
                continue
        else:

            try:
                full_list = eval(get_query_text(get_query_url(STATE, index + 1)))
                full_list.pop(0)
                full_list.pop(0)
                if index == 0:
                    for county in full_list:
                        if int(county[2]) < 0:
                            county_totals.append(county[1])
                            county_totals_errors.append(None)
                            county_pos_estimates.append(county[1])
                            county_pos_errors.append(None)
                            county_neg_estimates.append(0)
                            county_neg_errors.append(None)
                            continue
                        county_totals.append(county[1])
                        county_totals_errors.append(county[2])
                        county_pos_estimates.append(county[1])
                        county_pos_errors.append(county[2])
                        county_neg_estimates.append(0)
                        county_neg_errors.append(None)
                    continue
                elif variable.__contains__('less'):
                    for county in full_list:
                        if int(county[2]) < 0:
                            county_neg_estimates.append(county[1])
                            county_neg_errors.append(None)
                            continue
                        county_neg_estimates.append(county[1])
                        county_neg_errors.append(county[2])
                    continue
                elif variable.__contains__('very well'):
                    for county in full_list:
                        if int(county[2]) < 0:
                            county_pos_estimates.append(county[1])
                            county_pos_errors.append(None)
                            continue
                        county_pos_estimates.append(county[1])
                        county_pos_errors.append(county[2])
                    continue
                else:
                    for county in full_list:
                        if int(county[2]) < 0:
                            county_totals.append(county[1])
                            county_totals_errors.append(None)
                            continue
                        county_totals.append(county[1])
                        county_totals_errors.append(county[2])
                    continue
            except Exception as error:
                print(variable, index, error)
    return county_totals, county_totals_errors, county_pos_estimates, county_pos_errors, county_neg_estimates, county_neg_errors

variables = get_variable_table_df()
var_names, old_names = get_variable_names(variables, get_language_spoken_index(variables))
def runScript():
    try:
        eval(get_query_text(get_query_url(state_index=STATE, value_index=1))).pop(0)
    except Exception as e:
        print(e, 'Invalid state query', STATE)
    state_names, county_names, fips_codes = get_state_county_fips()
    county_totals, county_totals_errors, county_pos_estimates, county_pos_errors, county_neg_estimates, county_neg_errors = get_county_values()
    variable_list = get_full_variable_names()
    years = get_census_year()
    temp_dict = {
        "State": state_names,
        "County": county_names,
        "FIPS CODE": fips_codes,
        "Language spoken": variable_list,
        "Proficient English speakers": county_pos_estimates,
        "Proficient error margin": county_pos_errors,
        "Less than proficient English speakers": county_neg_estimates,
        "Less than proficient error margin": county_neg_errors,
        "Language Total": county_totals,
        "Language Total error margin": county_totals_errors,
        "Census year": years
    }
    print(temp_dict)
    state_df = pd.DataFrame(temp_dict)
    index = pd.Index([i for i in range(len(state_df.index))])
    state_df.set_index(index, inplace=True)
    state_df.to_csv(f'{STATE}_census_data.csv')

runScript()
# Uncomment below loop and comment out above line to get data for every state in different csv files
# for i in range(56):
#     i += 1
#     STATE = i
#     runScript()

