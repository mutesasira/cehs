
from rich import print
from time import time
from datetime import datetime
import pandas as pd
import numpy as np

month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
               'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

index_base_columns = ['id', 'date', 'year',
                      'month', 'facility_id', 'facility_name']


# Filtering methods for data transform functions


def filter_df_by_policy(dfs, key):
    df = dfs.get(key)
    return df


def filter_df_by_indicator(df, indicator, persist_columns=[]):
    columns_to_keep = persist_columns + [indicator]
    df = df[columns_to_keep]

    return df


def filter_df_by_dates(df, target_year, target_month, reference_year, reference_month):
    min_date = None
    max_date = None
    reverse = False

    # TODO See if I can just have this return only the two dates, not everything in between

    df = df.sort_values(['date'])

    if target_year and target_month:
        target_date = datetime(int(target_year), int(
            month_order.index(target_month) + 1), 1)
    if reference_year and reference_month:
        reference_date = datetime(int(reference_year), int(
            month_order.index(reference_month) + 1), 1)
    if reference_date <= target_date:
        max_date = target_date
        min_date = reference_date
    elif target_date < reference_date:
        max_date = reference_date
        min_date = target_date
        reverse = True
    if min_date:
        min_mask = (df.date >= min_date)
        df = df.loc[min_mask].reset_index(drop=True)
    if max_date:
        max_mask = (df.date <= max_date)
        df = df.loc[max_mask].reset_index(drop=True)
    if reverse:
        df = df.reindex(index=df.index[::-1])
    return df


def filter_by_district(df, district):
    mask = (df.id == district)
    df = df.loc[mask].reset_index(drop=True)
    return df


def get_sub_dfs(df, select_index, values, new_index, order=None):
    '''
    Extract and return a dictionary of dictionaries splitting each original dictionary df entry into traces based on values
    '''

    traces = {}
    for value in values:
        sub_df = df[df.index.get_level_values(select_index) == value]
        sub_df = sub_df.groupby(new_index).sum()
        if order:
            sub_df = sub_df.reindex(order)
        traces[value] = sub_df

    return traces


def get_num(df, value='positive_indic'):
    """
    Gets a dataframe of the count of the specified value for each column; expects index formatting including date and id
    """
    df_count_all = []
    for date in list((df.index.get_level_values('date')).unique()):
        count_for_date = (df.loc[date] == value).sum()
        df_count_for_date = (pd.DataFrame(count_for_date)).transpose()
        df_count_for_date.index = [date]
        df_count_all.append(df_count_for_date)
    new_df = pd.concat(df_count_all)
    return new_df


def reporting_count_transform(data):
    """
    Counts occurance of type of reporting label for each date, returning dictionary
    """
    # Set index
    data = check_index(data)
    # Remove unneccesary index values
    data = data.droplevel(['id'])
    # Count number of positive_indic
    df_positive = get_num(data, 'positive_indic')
    # Count number of no_positive_indic
    df_no_positive = get_num(data, 'no_positive_indic')
    # Count number of no_form_report
    df_no_form_report = get_num(data, 'no_form_report')

    data = {
        'Reported a positive number': df_positive,
        'Did not report a positive number': df_no_positive,
        'Did not report on their 105:1 form': df_no_form_report,
    }
    return data


# Data cleaning methods for dataset selction and callbacks


def parse_target_pop(df, indicator):
    new = []
    for x in df.index:
        y = df.loc[x, 'ages']
        z = y.split(' ')
        new.append(z)
    df['age_list'] = new
    df = df[df.indicator == indicator]
    sex = df['sex'][0]
    ages = df['age_list'][0]
    # TODO Modify to accout for more than 1 line in teh file
    return sex, ages


def get_percentage(df, pop, pop_tgt, ind_type, indicator, all_country=False):
    '''
    Transforms the data using percentage of a target population, and group it by district or country
    '''

    # Pick what to grouby and index on : either district level or national level

    merge_pop = ['district', 'year']
    merge_data = ['id', 'year']
    index = ['id', 'year', 'month', 'date']

    if all_country == True:
        merge_pop = merge_pop[1]
        merge_data = merge_data[1]
        index = index[1:4]

    # Return the data as is, with a simple grouby if we are showing absolute numbers

    if ind_type == 'Absolute':
        return df.groupby(index).agg({indicator: 'sum'})

    # Else get target population, merge it and calculate percentage

    sex, ages = parse_target_pop(pop_tgt, indicator)

    val_col = df.columns[-1]
    data_in = df.groupby(index, as_index=False).sum()

    pop_in = pop[pop.age.isin(ages)].groupby(merge_pop, as_index=False).sum()
    data_in = pd.merge(data_in, pop_in, how='left',
                       left_on=merge_data, right_on=merge_pop)

    data_in = data_in.groupby(index, as_index=False).sum()

    data_in[val_col] = (data_in[val_col] / data_in[sex])*12

    data_in.replace(np.inf, np.nan, inplace=True)

    data_in = data_in.set_index(index)[[val_col]]

    return data_in


def check_index(df, index=['id', 'date', 'year', 'month', 'facility_id', 'facility_name']):
    '''
    Check that the dataframe is formatted in the expected way, with expected indexes. Restructure the dataframe (set the indeces) if this is not the case.
    '''
    if df.index.values != index:
        #print('Checking index')
        # Set the indeces
        df = df.reset_index(drop=True).set_index(index)
    return df


def get_national_sum(df, indicator):
    return df.groupby(['date', 'year', 'month'], as_index=False).agg({indicator: 'sum'})


def get_district_sum(df, indicator):
    return df.groupby(['id', 'date', 'year', 'month'], as_index=False).agg({indicator: 'sum'})

# Decorators


def timeit(f):

    def timed(*args, **kw):

        ts = time()
        result = f(*args, **kw)
        te = time()
        run = round(te-ts, 3)

        print(
            f'[cyan]{f.__name__}()[/cyan] took: [bold blue]{run}[/bold blue] seconds to run.')

        return result

    return timed
