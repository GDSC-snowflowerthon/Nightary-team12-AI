
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import requests
import os
from dotenv import load_dotenv




def analyze_by_arima(df):
    model_start_time = ARIMA(df['start_hour'], order=(1, 1, 1))
    model_start_time_fit = model_start_time.fit()
    start_time_forecast = model_start_time_fit.forecast(steps=5).reset_index(drop=True)


    model_duration= ARIMA(df['sleepDuration'], order=(1, 1, 1))
    model_duration_fit = model_duration.fit()
    duration_forecast = model_duration_fit.forecast(steps=5).reset_index(drop=True)
    return start_time_forecast, duration_forecast

#주어진 날짜와 소수 형식의 시간을 datetime 객체로 변환
def convert_to_datetime(date, time_float):
    hours = int(time_float)
    minutes = int((time_float % 1) * 60)
    return datetime(date.year, date.month, date.day, hours, minutes)

def call_chat_gpt_api(prompt):
    """
    ChatGPT API를 호출하여 결과를 받아오는 함수
    """
    load_dotenv()
    api_url = "https://api.openai.com/v1/chat/completions" 
    headers = {
        "Authorization": os.getenv('BEARER_TOKEN'),
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
      {
        "role": "system",
        "content": "You are a analyst who is analyzing sleep patterns of a user. Please analyze user's sleep pattern by using Korean.\n"\
                    "분석은 1. 수면 시간, 2. 수면 일관성, 3. 예측된 수면 시간에 대해서 진행해줬으면 좋겠고, 이후로는 간단한 피드백을 좀 줬으면 좋겠어. 나한테 어떠한 질문도 하지 말아줘."\
                    "Please consider the max_tokens is 999. "
      },
      {
        "role": "user",
        "content": prompt
      }
    ],
        "max_tokens": 999  
    }

    response = requests.post(api_url, headers=headers, json=data)
    response_json = response.json()
    if response_json.get('choices'):
        return response_json['choices'][0]['message']['content'].strip()

def make_graph(df, start_time_forecast, duration_forecast):
    # 그래프 생성
    future_dates = pd.date_range(start=df['startSleepDate'].max(), periods=6, freq='D')[1:]
    plt.figure(figsize=(10, 6))
    plt.plot(df['startSleepDate'][-20:], df['sleepDuration'][-20:], label='Actual Sleep Duration')
    plt.plot(future_dates[:5], duration_forecast, label='Predicted Sleep Duration')
    plt.xlabel('Date')
    plt.ylabel('Sleep Duration (hours)')
    plt.title('Sleep Duration Prediction')
    plt.legend()
    plt.grid(True)

    # 그래프를 BytesIO 버퍼에 저장
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # base64 인코딩을 사용하여 이미지를 문자열로 변환
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return image_base64

def process_sleep_data(data):
        start_dates = data['startSleepDate']
        end_dates = data['endSleepDate']

        df = pd.DataFrame({'startSleepDate': start_dates, 'endSleepDate': end_dates})
        df['startSleepDate'] = pd.to_datetime(df['startSleepDate'])
        df['endSleepDate'] = pd.to_datetime(df['endSleepDate'])

        # 수면 시간 계산(시간 단위)
        df['sleepDuration'] = (df['endSleepDate'] - df['startSleepDate']).dt.total_seconds() / 3600
        df.loc[df['sleepDuration'] < 0, 'sleepDuration'] += 24

        # 수면 시작 시간을 시간의 소수점 형식으로 변환 ex)16:30 -> 16.5
        df['start_hour'] = df['startSleepDate'].dt.hour + df['startSleepDate'].dt.minute / 60 + df['startSleepDate'].dt.second / 3600

        start_time_forecast, duration_forecast = analyze_by_arima(df)

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

        image_base64 = make_graph(df, start_time_forecast, duration_forecast)

        prompt='Here are my recent sleep records: \n'
        for i in range(20):
            prompt += str(df['startSleepDate'].iloc[-20+i])[:19] + ' ~ ' + str(df['endSleepDate'].iloc[-20+i])[:19] + '\n'
        
        prompt+='\nAnd here are my predicted sleep times for the next 5 days: \n'
        for i in range(5):
            prompt += str(final_predictions['Predicted Start Time'].iloc[i])[:19] + ' ~ ' + str(final_predictions['Predicted End Time'].iloc[i])[:19] + '\n'

        prompt+='Please analyse my sleep patterns and give me some advice on how to improve my sleep quality by using Korean.\n'
        prompt+='피드백은 "--피드백" 으로 시작했으면 좋겠어.\n'
        prompt+='Please consider the max_tokens is 999. '


        # ChatGPT API 호출
        chat_gpt_response = call_chat_gpt_api(prompt)

        # 분석과 피드백으로 나누기
        chat_gpt_response = chat_gpt_response.split('--피드백')

        response_content = {
        'graph': image_base64,
        'chat_gpt_analysis': chat_gpt_response[0],
        'chat_gpt_feedback': chat_gpt_response[1] 
        }
        
        return response_content
    
