import os
import boto3
import io
from PIL import Image
import base64
from openai import OpenAI
import time
import psycopg2 #postgres
import environ

from config.settings.base import BASE_DIR

env = environ.Env(DEBUG=(bool, True))

environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)

# 이미지 데이터를 base64로 인코딩
def encode_image(image_data):
    image = Image.open(io.BytesIO(image_data))
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")  # 이미지 형식에 따라 변경 가능
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

# S3에서 이미지 스트리밍 (파일 다운로드 없이)
def get_image_from_s3(s3, bucket_name, object_key):
    s3_object = s3.get_object(Bucket=bucket_name, Key=object_key)
    image_data = s3_object['Body'].read()
    return image_data

def genarate_ai_diary(images, moods, hashtags):
    s3 = boto3.client('s3')
    bucket_name = 'test-kilolog'
    #request에서 값 가져오기
    tmp_object_key = images #예시: https://test-kilolog.s3.ap-northeast-2.amazonaws.com/youngkyu/2024-12-15/test_image.jpg
    object_key = tmp_object_key[0].split('.com')[1] #tmp_object_key.split('.com')은 이런 값으로 변경됨. 이 중 키 부분인 인덱스 1의 값을 키로 사용['https://test-kilolog.s3.ap-northeast-2.amazonaws', '/youngkyu/2024-12-15/test_image.jpg']
    emotion = moods
    tmp_keywords = hashtags #'키워드1, 키워드2, 키워드3'와 같은 꼴
    keywords = [keyword.strip() for keyword in keywords.split(',')] #[['키워드1', '키워드2', '키워드3']와 같은 꼴로 변환 #[['키워드1', '키워드2', '키워드3']와 같은 꼴로 변환 #[['키워드1', '키워드2', '키워드3']와 같은 꼴로 변환 #[['키워드1', '키워드2', '키워드3']와 같은 꼴로 변환
    #s3에서 이미지 가져오기
    image_data = get_image_from_s3(bucket_name, object_key)
    encoded_image = encode_image(image_data)
    # 이제 인코딩된 이미지 데이터를 OpenAI API로 전송할 수 있습니다
    client = OpenAI(
        api_key=env('OPENAI_API_KEY'))
    query = "" #감정 쿼리문, 날짜랑 함께 조회해야 함
    user_text = f"""
    이 사진은 내가 일기에 올린 사진이야.
    오늘을 나타내는 키워드: {keywords[0]}, {keywords[1]}, {keywords[2]}
    오늘의 감정: {emotion}
    사진, 키워드 감정을 토대로 일기를 작성해 줘.
    일기의 제목이나 날짜 같은 정보는 쓰지 마. 일기의 내용만 작성해 줘.
    그리고 오늘의 키워드들을 각각 2번 이상 3번 이하로 일기에 언급해야 해.
    이미지에 대한 분석도 꼭 일기에 포함해야 해.
    띄어 쓰기에 주의하고, 개행 문자 '\n'는 넣지 마.
    """
    completion = client.chat.completions.create(
        #model="gpt-3.5-turbo",
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": user_text,
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url":  f"data:image/jpeg;base64,{encoded_image}"
                    },
                },
                ],
            }
        ]
    )
    #print(completion.choices[0].message)
    #print(completion['choices'][0]['message']['content'])
    return completion.choices[0].message.content