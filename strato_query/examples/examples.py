"""
StratoDem Analytics : examples
Principal Author(s) : Eric Linden
Secondary Author(s) :
Description :

Notes :

January 09, 2019
"""

import pandas

from strato_query.base_API_query import *
from strato_query.standard_filters import *


class ExampleQueries(BaseAPIQuery):
    @classmethod
    def example_count_query(cls):
        # Number of households ages 25-39 with net worth of at least $50,000
        # within 20-minute drive of a location South of Boston in the year 2017

        df = cls.query_api_df(
            query_params=APIQueryParams(
                query_type='COUNT',
                table='networth_tract_annual_net_worth_age',
                data_fields=('year', 'age_g_bottom_coded', 'net_worth_g', 'households'),
                data_filters=(
                    BetweenFilter(var='age_g_bottom_coded', val=[6, 8]).to_dict(),
                    GtrThanOrEqFilter(var='net_worth_g', val=3).to_dict(),
                    EqFilter(var='year', val=2017).to_dict(),
                    dict(
                        filter_type='drivetime',
                        filter_value=dict(
                            latitude=42.256922,
                            longitude=-71.040571,
                            minutes=20),
                        filter_variable='')
                ),
                groupby=(),
                order=(),
                aggregations=(),
            )
        )

        print('Number of households 25-39 with $50k+ net worth in 2017 in a 20 min drive of coord:')
        print(df.head())
        print('Results truncated')

    @classmethod
    def example_query_with_area_join_and_aggregation(cls):
        # Population density in the Boston MSA by year prior to 2015

        df = cls.query_api_df(
            query_params=APIQueryParams(
                query_type='COUNT',
                table='populationforecast_metro_annual_population_age_edu',
                data_fields=('year', 'cbsa', {'population': 'population'}),
                data_filters=(
                    LessThanFilter(var='year', val=2015).to_dict(),
                    EqFilter(var='cbsa', val=14454).to_dict(),
                ),
                aggregations=(dict(aggregation_func='sum', variable_name='population'),),
                groupby=('cbsa', 'year'),
                order=('year',),
                join=APIQueryParams(
                    query_type='AREA',
                    table='geocookbook_metro_na_shapes_full',
                    data_fields=('cbsa', 'area', 'name'),
                    data_filters=(),
                    groupby=('cbsa', 'name'),
                    aggregations=(),
                    on=dict(left=('cbsa',), right=('cbsa',)),
                )
            )
        )

        df['POP_PER_SQ_MI'] = df['POPULATION'].div(df['AREA'])
        df_final = df[['YEAR', 'NAME', 'POP_PER_SQ_MI']]

        print('Population density in the Boston MSA up to 2015:')
        print(df_final.head())
        print('Results truncated')

    @classmethod
    def example_median_query(cls):
        # Finds median household income in the US for those 80+ from 2010 to 2013

        df = cls.query_api_df(
            query_params=APIMedianQueryParams(
                query_type='MEDIAN',
                table='incomeforecast_us_annual_income_group_age',
                data_fields=('year', {'median_value': 'median_income'}),
                median_variable_name='income_g',
                data_filters=(
                    GtrThanOrEqFilter(var='age_g', val=17).to_dict(),
                    BetweenFilter(var='year', val=[2010, 2013]).to_dict(),
                ),
                groupby=('year',),
                order=('year',),
                aggregations=(),
            )
        )

        print('Median US household income 80+:')
        print(df.head())

    @classmethod
    def example_mean_query(cls):
        # Mean US home value for homeowners ages 60 and up from 2006 to 2010

        df = cls.query_api_df(
            query_params=APIMeanQueryParams(
                table='homevalueforecast_us_annual_age_mean_home_value',
                data_fields=('year', {'mean_value': 'mean_home_value'}),
                data_filters=(
                    BetweenFilter(var='year', val=[2006, 2010]).to_dict(),
                    GtrThanOrEqFilter(var='age_g', val=13).to_dict(),
                ),
                query_type='MEAN',
                mean_variable_name='home_value_g2',
                aggregations=(),
                groupby=('year',),
                order=('year',)
            )
        )

        print('Mean US home value for homeowners ages 60+ from 2006 to 2010:')
        print(df.head())

    @classmethod
    def example_multiple_query(cls):
        # Households ages 30 to 59 earning under $100k in Suffolk County, MA in 2010
        # Multiple-type queries, including this one, can often be handled using join,

        df_dict = cls.query_api_multiple(
            queries=dict(
                income=APIQueryParams(
                    table='incomeforecast_county_annual_income_group_age',
                    data_fields=('geoid5', 'year', 'income_g', 'age_g', 'households'),
                    data_filters=(
                        EqFilter(var='year', val=2010).to_dict(),
                        BetweenFilter(var='age_g', val=[7, 12]).to_dict(),
                        LessThanOrEqFilter(var='income_g', val=12).to_dict(),
                        EqFilter(var='geoid5', val=25025).to_dict(),
                    ),
                    query_type='COUNT',
                    aggregations=(),
                    groupby=(),
                ),
                name=APIQueryParams(
                    table='geocookbook_county_na_county_name',
                    data_fields=('geoid5', 'geoid5_name_with_init'),
                    data_filters=(),
                    query_type='COUNT',
                    aggregations=(),
                    groupby=(),
                ),
            )
        )

        df = pandas.merge(df_dict['income'], df_dict['name'], on='GEOID5')
        df_final = df[['AGE_G', 'INCOME_G', 'HOUSEHOLDS', 'GEOID5_NAME_WITH_INIT']]

        print('Households ages 30-59 earning under $100k in Suffolk County, MA in 2010:')
        print(df_final.head())
        print('Results truncated')


def run_examples():
    ExampleQueries.example_count_query()
    print('\n\n')
    ExampleQueries.example_query_with_area_join_and_aggregation()
    print('\n\n')
    ExampleQueries.example_median_query()
    print('\n\n')
    ExampleQueries.example_mean_query()
    print('\n\n')
    ExampleQueries.example_multiple_query()


if __name__ == '__main__':
    run_examples()
