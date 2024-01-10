from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.http import JsonResponse
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta

#주어진 날짜와 소수 형식의 시간을 datetime 객체로 변환
def convert_to_datetime(date, time_float):
    hours = int(time_float)
    minutes = int((time_float % 1) * 60)
    return datetime(date.year, date.month, date.day, hours, minutes)

@csrf_exempt
@require_http_methods(["POST"])
def sleep_prediction(request):
    try:
        # Load JSON data from request
        data = json.loads(request.body)
        start_dates = data['startSleepDate']
        end_dates = data['endSleepDate']

        # Convert to DataFrame
        df = pd.DataFrame({'startSleepDate': start_dates, 'endSleepDate': end_dates})
        df['startSleepDate'] = pd.to_datetime(df['startSleepDate'])
        df['endSleepDate'] = pd.to_datetime(df['endSleepDate'])

        # 수면 시간 계산(시간 단위)
        df['sleepDuration'] = (df['endSleepDate'] - df['startSleepDate']).dt.total_seconds() / 3600
        df.loc[df['sleepDuration'] < 0, 'sleepDuration'] += 24

        # 수면 시작 시간을 시간의 소수점 형식으로 변환 ex)16:30 -> 16.5
        df['start_hour'] = df['startSleepDate'].dt.hour + df['startSleepDate'].dt.minute / 60 + df['startSleepDate'].dt.second / 3600


        model_start_time = ARIMA(df['start_hour'], order=(1, 1, 1))
        model_start_time_fit = model_start_time.fit()
        start_time_forecast = model_start_time_fit.forecast(steps=5).reset_index(drop=True)


        model_duration= ARIMA(df['sleepDuration'], order=(1, 1, 1))
        model_duration_fit = model_duration.fit()
        duration_forecast = model_duration_fit.forecast(steps=5).reset_index(drop=True)


        # End Time 계산(예측 수면 시작 시각 + 예측 수면 시간)
        future_dates = pd.date_range(start=df['startSleepDate'].max(), periods=6, freq='D')[1:]
        final_predictions = pd.DataFrame({
            'Predicted Start Time': [convert_to_datetime(future_dates[i], start_time_forecast[i]) for i in range(5)],
            'Predicted End Time': [convert_to_datetime(future_dates[i], start_time_forecast[i]) + timedelta(hours=duration_forecast[i]) for i in range(5)]
        }, index=future_dates)

        # 인덱스 재설정
        final_predictions = final_predictions.reset_index(drop=True)

        # 1부터 시작하는 인덱스로 조정
        final_predictions.index = final_predictions.index + 1

        #End Time에 밀리초 제거
        final_predictions['Predicted End Time'] = final_predictions['Predicted End Time'].dt.strftime('%Y-%m-%d %H:%M:%S')

        response_data = final_predictions.to_json(orient='records', date_format='iso')

        return JsonResponse({'predictions': json.loads(response_data)}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
