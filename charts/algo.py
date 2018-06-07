import datetime
import sqlite3 as lite

import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.preprocessing import MinMaxScaler


def tsne(self):
    con = lite.connect('test.db', isolation_level='DEFERRED')
    parameters_tech = ['date']
    with con:
        cur = con.cursor()
        list_tech_id = [50, 51, 102, 138, 145, 151, 170, 203, 318]
        questionmarks = '?' * len(list_tech_id)
        query = 'SELECT * FROM PARAMETERS WHERE PARAMETERS.rowid IN ({})'.format(
            ','.join(questionmarks))
        query_args = list_tech_id
        cur.execute(query, query_args)
        rows = cur.fetchall()  # извлечь данные
        for row in rows:
            parameters_tech.append(row[0])
    # print(parameters_tech)

    a = datetime.datetime(2015, 5, 17, 5, 0, 0)
    cur = con.cursor()
    query = ''
    query += 'SELECT date, '
    for row_id in list_tech_id:
        if (list_tech_id[len(list_tech_id) - 1] != row_id):
            query += 'MAX(CASE MEASUREMENTS.parameter_id WHEN ' + str(
                row_id) + ' THEN MEASUREMENTS.value ELSE NULL END), '
        else:
            query += 'MAX(CASE MEASUREMENTS.parameter_id WHEN ' + str(
                row_id) + ' THEN MEASUREMENTS.value ELSE NULL END)'
    query += 'FROM measurements WHERE datetime(date) < datetime(?) group by date'
    # print(query)
    cur.execute(query, (a,))
    df_query = pd.DataFrame.from_records(data=cur.fetchall(),
                                         columns=parameters_tech)  # перевод в матричный вид для pandas
    # для обработки нулевых значений, удаление строк
    df_query.dropna(axis=0, inplace=True)

    sc = MinMaxScaler(feature_range=(0, 1))
    df_data = df_query.drop(['Stippe_-3000', 'date'], axis=1)
    training_set_scaled_x = sc.fit_transform(df_data.values)
    df_classify = df_query['Stippe_-3000'].apply(self.classifyQualityValue)
    # print(df_classify)
    # threshhold = 45
    tsne = TSNE()
    z = tsne.fit_transform(training_set_scaled_x)
    print("hi")
    return z, df_classify


def classifyQualityValue(self, x):
    if (x > 45):
        return 0
    else:
        return 1
