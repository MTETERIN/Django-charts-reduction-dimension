import datetime
import pickle
import sqlite3 as lite

import numpy as np
import pandas as pd
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from sklearn.manifold import TSNE
from sklearn.preprocessing import MinMaxScaler

import xgboost as xgb
from rest_framework.response import Response
from rest_framework.views import APIView

from keras.layers import Input, Dense
from keras.models import Model
from keras import backend as K

User = get_user_model()


def get_data(request, *args, **kwargs):
    return render(request, 'parametrs.html')


def manual(request, *args, **kwargs):
    return render(request, 'manual.html')


def main(request, *args, **kwargs):
    return render(request, 'main.html')


class StatCharView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'stat-char.html')

class PlotCharView(View):
    def get(self, request, *args, **kwargs):
        if request.method == "GET":
            web_url = request.GET.get('group')
            defect_url = request.GET.get('defect')
            print(web_url)
            with open('fileplots.pickle', 'wb') as handle:
                pickle.dump(web_url, handle, protocol=pickle.HIGHEST_PROTOCOL)
            with open('defectplots.pickle', 'wb') as defe:
                pickle.dump(defect_url, defe, protocol=pickle.HIGHEST_PROTOCOL)
        return render(request, 'plot-char.html')

class BarChartView(View):
        def get(self, request, *args, **kwargs):
            return render(request, 'chartbar.html')


class HomeView(View):
    def get(self, request, *args, **kwargs):
        if request.method == "GET":
            web_url = request.GET.getlist('groups[]')
            defect_url = request.GET.getlist('defect[]')
            with open('filetechnicalspecifications.pickle', 'wb') as handle:
                pickle.dump(web_url, handle, protocol=pickle.HIGHEST_PROTOCOL)
            with open('filedefect.pickle', 'wb') as defe:
                pickle.dump(defect_url, defe, protocol=pickle.HIGHEST_PROTOCOL)
            print(web_url)
            print(defect_url)
        return render(request, 'charts.html', {"groups": web_url, "defect": defect_url})


class ChartEncoderData(APIView):
    authentication_classes = []
    permission_classes = []

    def autoencoder(self):
        con = lite.connect('test.db', isolation_level='DEFERRED')
        parameters_tech = ['date']
        with con:
            cur = con.cursor()

            with open('filetechnicalspecifications.pickle', 'rb') as handle:
                list_parameters = pickle.load(handle)
            list_tech_id = list(map(int, list_parameters))
            print(list_tech_id)
            print(len(list_parameters))

            with open('filedefect.pickle', 'rb') as defe:
                list_defects = pickle.load(defe)
            for i, item in enumerate(list_defects):
                list_defects[i] = int(item)
            list_tech_id.append(*list_defects)
            print(*list_defects)
            print(list_tech_id)

            #list_tech_id = [50, 51, 102, 138, 145, 151, 170, 203, 318];
            questionmarks = '?' * len(list_tech_id);
            query = 'SELECT * FROM PARAMETERS WHERE PARAMETERS.rowid IN ({})'.format(','.join(questionmarks))
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
        cur.execute(query, (a,));
        df_query = pd.DataFrame.from_records(data=cur.fetchall(),
                                             columns=parameters_tech)  # перевод в матричный вид для pandas

        df_query.dropna(axis=0, inplace=True)  # для обработки нулевых значений, удаление строк


        print(df_query.columns)
        print(list_defects[0])
        with con:
            cur = con.cursor()
            queryName = "SELECT PARAMETERS.parameter_name FROM PARAMETERS WHERE PARAMETERS.rowid = {}".format(
                *list_defects)
            cur.execute(queryName);
            defectParameter = cur.fetchone()[0];


        sc = MinMaxScaler(feature_range=(0, 1))

        df_data = df_query.drop([defectParameter, 'date'], axis=1)
        train_x = sc.fit_transform(df_data.values)

       # training_y = sc.fit_transform(df_query[defectParameter].values)
        df_classify = df_query[defectParameter].apply(self.classifyQualityValue)
        np.random.seed(182)

        encoding_dim = 2
        input_in = Input(shape=(len(list_parameters), ))  # this is our input placeholder #list_parameters
        encoded = Dense(encoding_dim, activation='relu')(
            input_in)  # "encoded" is the encoded representation of the input
        decoded = Dense(len(list_parameters), activation='sigmoid')(encoded)  # "decoded" is the lossy reconstruction of the input

        autoencoder = Model(input_in, decoded)  # this model maps an input to its reconstruction
        encoder = Model(input_in, encoded)

        encoded_input = Input(shape=(encoding_dim, ))  # create a placeholder for an encoded (32-dimensional) input
        decoder_layer = autoencoder.layers[-1]  # retrieve the last layer of the autoencoder model
        decoder = Model(encoded_input, decoder_layer(encoded_input))  # create the decoder model

        autoencoder.compile(optimizer='adam', loss='mean_squared_error')
        autoencoder.fit(train_x, train_x,
                                  epochs=50,
                                  batch_size=32,
                                  shuffle=True
                                  # validation_data=(train_x, train_x)
                                  )

        z = encoder.predict(train_x)
        print("hi")
        return z, df_classify

    def classifyQualityValue(self, x):
        if (x > 45):
            return 0
        else:
            return 1

    def get(self, request, format=None):
        autoencoder_output, classify = self.autoencoder()
        datas = []
        for i in autoencoder_output:
            point = {
                'x': i[0],
                'y': i[1],
                'r': 3,
            }
            datas.append(point)
        colors = []

        for i in classify:
            if i == 0:
                colors.append("#8C7D7E")  # черные
            if i == 1:
                colors.append("#F34F4F")  # красные - дефект

        qs_count = User.objects.all().count()

        data = {
                "default": datas,
                "color": colors
        }
        K.clear_session()
        return Response(data)

class BoostingGradientView(View):
    def get(self, request, *args, **kwargs):
        if request.method == "GET":
            algorithm = request.GET.get('algorithm')
            web_url = request.GET.getlist('groups[]')
            defect_url = request.GET.getlist('defect[]')
            with open('filetechnicalspecifications.pickle', 'wb') as handle:
                pickle.dump(web_url, handle, protocol=pickle.HIGHEST_PROTOCOL)
            with open('filedefect.pickle', 'wb') as defe:
                pickle.dump(defect_url, defe, protocol=pickle.HIGHEST_PROTOCOL)
                if (algorithm == '1'):
                    print('zz')
                    return render(request, 'charts.html', {"groups": web_url, "defect": defect_url})
                elif (algorithm == 2):
                    return render(request, 'boosting.html', {"groups": web_url, "defect": defect_url})
                else:
                    return render(request, 'charts-encoder.html', {"groups": web_url, "defect": defect_url})

class PlotData(APIView):
    def plots(self):
        print('Here:')
        con = lite.connect('test.db', isolation_level='DEFERRED')
        parameters_tech = ['date']
        with con:
            cur = con.cursor()
            with open('fileplots.pickle', 'rb') as handle:
                list_parameters = pickle.load(handle)
            print(list_parameters)

            with open('defectplots.pickle', 'rb') as defe:
                list_defects = pickle.load(defe)
            print(list_defects)
            list = []
            list.append(list_parameters)
            list.append(list_defects)
            #list_tech_id = [50, 51, 102, 138, 145, 151, 170, 203, 318];
            questionmarks = '??'
            query = 'SELECT * FROM PARAMETERS WHERE PARAMETERS.rowid IN ({})'.format(
                ','.join(questionmarks))
            query_args = list_parameters
            print(query)
            cur.execute(query, list);
            rows = cur.fetchall()  # извлечь данные
            for row in rows:
                parameters_tech.append(row[0])

        a = datetime.datetime(2015, 5, 17, 5, 0, 0)
        cur = con.cursor()
        query = ''
        query += 'SELECT date, '
        query += 'MAX(CASE MEASUREMENTS.parameter_id WHEN ' + str(
                    list_parameters) + ' THEN MEASUREMENTS.value ELSE NULL END), '
        query += 'MAX(CASE MEASUREMENTS.parameter_id WHEN ' + str(
                    list_defects) + ' THEN MEASUREMENTS.value ELSE NULL END) '
        query += 'FROM measurements WHERE datetime(date) < datetime(?) group by date'
        print(query)
        cur.execute(query, (a,))
        df_query = pd.DataFrame.from_records(data=cur.fetchall(),
                                             columns=parameters_tech)  # перевод в матричный вид для pandas

        # для обработки нулевых значений, удаление строк
        df_query.dropna(axis=0, inplace=True)
        with con:
            cur = con.cursor()
            queryName = "SELECT PARAMETERS.parameter_name FROM PARAMETERS WHERE PARAMETERS.rowid = {}".format(
                list_parameters)
            cur.execute(queryName)
            techParameter = cur.fetchone()[0]
        with con:
            cur = con.cursor()
            queryName = "SELECT PARAMETERS.parameter_name FROM PARAMETERS WHERE PARAMETERS.rowid = {}".format(
                list_defects)
            cur.execute(queryName)
            defParameter = cur.fetchone()[0]
        return df_query[techParameter].values, df_query[defParameter].values,techParameter,defParameter


    def get(self, request, format=None):
        predict_values, real_values,name1,name2 = self.plots()
        datas = []
        real_data = []
        timeStamp = 0
        for i in predict_values:
            timeStamp += 1
            point = {
                'x': timeStamp,
                'y': i,
                'r': 3,
            }
            datas.append(point)
        colors = []

        for i in predict_values:
            colors.append("#F34F4F")  # красные - дефект

        timeStamp = 0
        for i in real_values:
            timeStamp += 1
            point = {
                'x': timeStamp,
                'y': i,
                'r': 3,
            }
            real_data.append(point)

        qs_count = User.objects.all().count()

        data = {
            "prediction": datas,
            "real": real_data,
            "color": colors,
            "name1":name1,
            "name2":name2,
            "labels":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,89,90,91,92,93,94,95,96,97,98,99,100]
        }
        return Response(data)

class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def tsne(self):
        con = lite.connect('test.db', isolation_level='DEFERRED')
        parameters_tech = ['date']
        with con:
            cur = con.cursor()
            with open('filetechnicalspecifications.pickle', 'rb') as handle:
                list_parameters = pickle.load(handle)
            list_tech_id = list(map(int, list_parameters))
            print(list_tech_id)

            with open('filedefect.pickle', 'rb') as defe:
                list_defects = pickle.load(defe)
            for i, item in enumerate(list_defects):
                list_defects[i] = int(item)
            list_tech_id.append(*list_defects)
            print(*list_defects)
            print(list_tech_id)

            #list_tech_id = [50, 51, 102, 138, 145, 151, 170, 203, 318];
            questionmarks = '?' * len(list_tech_id)
            query = 'SELECT * FROM PARAMETERS WHERE PARAMETERS.rowid IN ({})'.format(
                ','.join(questionmarks))
            query_args = list_tech_id
            cur.execute(query, query_args)
            rows = cur.fetchall()  # извлечь данные
            for row in rows:
                parameters_tech.append(row[0])

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
        print(df_query.columns)
        print(list_defects[0])
        with con:
            cur = con.cursor()
            queryName = "SELECT PARAMETERS.parameter_name FROM PARAMETERS WHERE PARAMETERS.rowid = {}".format(
                *list_defects)
            cur.execute(queryName)
            defectParameter = cur.fetchone()[0]
        sc = MinMaxScaler(feature_range=(0, 1))
        df_data = df_query.drop([defectParameter, 'date'], axis=1)
        training_set_scaled_x = sc.fit_transform(df_data.values)
        df_classify = df_query[defectParameter].apply(
            self.classifyQualityValue)
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

    def get(self, request, format=None):

        tsne_output, classify = self.tsne()
        datas = []
        for i in tsne_output:
            point = {
                'x': i[0],
                'y': i[1],
                'r': 3,
            }
            datas.append(point)
        colors = []

        for i in classify:
            if i == 0:
                colors.append("#8C7D7E")  # черные
            if i == 1:
                colors.append("#F34F4F")  # красные - дефект

        qs_count = User.objects.all().count()

        data = {
            "default": datas,
            "color": colors
        }
        return Response(data)


class Boosting(APIView):
    authentication_classes = []
    permission_classes = []

    def gradient_boosting(self):
        con = lite.connect('test.db', isolation_level='DEFERRED')
        parameters_tech = ['date']
        with con:
            cur = con.cursor()
            with open('filetechnicalspecifications.pickle', 'rb') as handle:
                list_parameters = pickle.load(handle)
            list_tech_id = list(map(int, list_parameters))
            print(list_tech_id)

            with open('filedefect.pickle', 'rb') as defe:
                list_defects = pickle.load(defe)
            for i, item in enumerate(list_defects):
                list_defects[i] = int(item)
            list_tech_id.append(*list_defects)
            print(*list_defects)
            print(list_tech_id)

            #list_tech_id = [50, 51, 102, 138, 145, 151, 170, 203, 318];
            questionmarks = '?' * len(list_tech_id)
            query = 'SELECT * FROM PARAMETERS WHERE PARAMETERS.rowid IN ({})'.format(
                ','.join(questionmarks))
            query_args = list_tech_id
            cur.execute(query, query_args)
            rows = cur.fetchall()  # извлечь данные
            for row in rows:
                parameters_tech.append(row[0])

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
        print(df_query.columns)
        print(list_defects[0])
        with con:
            cur = con.cursor()
            queryName = "SELECT PARAMETERS.parameter_name FROM PARAMETERS WHERE PARAMETERS.rowid = {}".format(
                *list_defects)
            cur.execute(queryName)
            defectParameter = cur.fetchone()[0]
        sc = MinMaxScaler(feature_range=(0, 1))
        df_data = df_query.drop([defectParameter, 'date'], axis=1)
        xgb_model = xgb.XGBRegressor(max_depth=5, n_estimators=60)
        xgb_model.fit(df_data.values, df_query[defectParameter].values)
        print("hi")
        return xgb_model.predict(df_data.values), df_query[defectParameter].values

    def get(self, request, format=None):

        predict_values, real_values = self.gradient_boosting()
        datas = []
        real_data = []
        timeStamp = 0
        for i in predict_values:
            timeStamp += 1
            point = {
                'x': timeStamp,
                'y': i,
                'r': 3,
            }
            datas.append(point)
        colors = []

        for i in predict_values:
            colors.append("#F34F4F")  # красные - дефект

        timeStamp = 0
        for i in real_values:
            timeStamp += 1
            point = {
                'x': timeStamp,
                'y': i,
                'r': 3,
            }
            real_data.append(point)

        qs_count = User.objects.all().count()

        data = {
            "prediction": datas,
            "real": real_data,
            "color": colors,
            "labels":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,89,90,91,92,93,94,95,96,97,98,99,100]
        }
        return Response(data)
