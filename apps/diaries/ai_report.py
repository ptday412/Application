from datetime import datetime
import ast
import os
import psycopg2 #postgres
import io
import environ
from openai import OpenAI
from config.settings.base import BASE_DIR
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from django.contrib.auth import get_user_model
from rest_framework.response import Response

User = get_user_model()

env = environ.Env(DEBUG=(bool, True))

environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)

#jwt에서 사용자 id를 추출하는 함수
def get_user_from_token(token):
    try:
        decoded_token = jwt.decode(token, 'django-insecure-%fzs+393q*e53vg4mry$ehj4n1ebzmzq1(kcj3_(*ov-2vq5h$', algorithms=['HS256'])
        user_id = decoded_token['user_id']  # jwt에서 사용자 ID 추출
        return user_id
    except ExpiredSignatureError:
        raise ValueError("token expired")
    except InvalidTokenError:
        raise ValueError("invalid token")

#postgre 쿼리하기
def emotion_query_postgre(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    #datetime을 string으로 변환
    results_converted_to_string = [
        (dt.strftime('%Y-%m-%d'), col1, col2)
        for (dt, col1, col2) in results
    ]
    #tuple 꼴의 각 요소를 list로 변환
    results_converted_to_list = [list(item) for item in results_converted_to_string]
    cursor.close()
    return results_converted_to_list

# 가입일 이전이면서 일주일치 일기 내용이 없다면, AI 피드백 받기에 가치가 없다고 판단
def is_worth_it(user_id, base_date, diary_contents):
    user = User.objects.filter(pk=user_id).values('date_joined')
    print(dict(user))
    date_obj = datetime.strptime(base_date, "%Y-%m-%d").date()
    if dict(user) < date_obj and not diary_contents:
        return False
    return True

#일기 요약과 활동 추천
def query_postgre(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

def ai_report(user_id, base_date):
    print('>>>>>>>>>>>>>>>>>>basedate: ', base_date)
    #DB 연결
    try:
        connection = psycopg2.connect(
                    host=env("DEV_DB_HOST"),
                    # 데이터베이스 호스트 #database="your_database",  # 데이터베이스 이름
                    user=env("DEV_DB_USER"),      # 데이터베이스 사용자 이름
                    password=env("DEV_DB_PASSWORD"),  # 데이터베이스 비밀번 호
                    port=env("DEV_DB_PORT")                # 기본 PostgreSQL 포트
                    )
    except (Exception, psycopg2.Error) as error:
        print("db 연결 실패::", error)
    # 일기: 기준일로부터 7일 동안, 테스트 성공
    query = f"SELECT content FROM diaries_diary WHERE user_id = {user_id} AND ymd BETWEEN '{base_date}' AND '{base_date}'::date + INTERVAL '6 days';" #일기 쿼리 : 일주일치
    diary = query_postgre(connection, query) #결과: [('내용1',), ('내용2',)] 튜플 만들어야 해서 쉼표가 있나봄
    diary_contents = [entry[0] for entry in diary]
    print(f'diary: {diary_contents}') #결과: ['내용1', '내용2']
    # AI 피드백 받기에 가치가 없다면 막기
    if not is_worth_it(user_id, base_date, diary_contents):
        print(diary_contents)
        return ('해당 날짜는 가입일 이전이면서, 분석할 일주일치 내용이 없어 AI피드백을 드릴 수 없습니다.')
    #키워드인데 일단 애매해서 뺌
    #query = "SELECT h.name FROM Hashtag h JOIN DiaryHashtag dh ON h.hashtag_id = dh.hashtag_id WHERE dh.diary_id IN (SELECT diary_id FROM Diary WHERE user_id = {user_id});" #키워드 쿼리
    #keywords = [query_postgre(connection, query)]
    # 관심사
    query = f"SELECT i.name FROM accounts_interest i JOIN accounts_user_interests ui ON i.id = ui.interest_id WHERE ui.user_id = {user_id};" #관심사 쿼리
    interest = [query_postgre(connection, query)]
    interest_contents = [i[0] for i in interest[0]] #얘는 리스트형태로 나와서 interest[0]에서 첫 인덱스
    print(f'interest: {interest_contents}')
    #성격
    query = f"SELECT p.name FROM accounts_personality p JOIN accounts_user_personalities up ON p.id = up.id WHERE up.user_id = {user_id};" # 성격 쿼리
    personality = [query_postgre(connection, query)]
    personality_contents = [i[0] for i in personality[0]] #얘는 리스트형태로 나와서 interest[0]에서 첫 인덱스
    print(f'personality: {personality_contents}')
    client = OpenAI(
        api_key = env('OPENAI_API_KEY'))
    system_instructions = """
    사용자는 너에게 사용자의 관심사, 성격, 일주일 간의 일기를 전송할 거야.
    먼저 일기를 토대로 일주일 간 있었던 일을 요약해 줘.
    그리고 요약을 토대로 관심사와 성격, 일기를 토대로 활동을 추천해.
    '활동 추천'과 같은 제목은 답변에 넣지 마.
    일주일을 요약한 내용도 답변에 넣지마.
    답변은 이 양식을 따라 줘. : ['추천 활동','추천한 이유']
    추천 활동은 하나만 추천해줘.
    추천한 이유는 '~입니다.'와 같은 어투를 사용해 줘
    """
    user_instructions = f"""
    나의 관심사: {interest_contents}
    나의 성격: {personality_contents}
    나의 일기: {diary_contents}
        """
    completion = client.chat.completions.create(
        #model="gpt-3.5-turbo",
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_instructions
            },
            {
                "role": "user",
                "content": user_instructions
            },
        ],
    )
    data = completion.choices[0].message.content
    try:
        data_list = ast.literal_eval(data)
        print(f'type of data_list is {type(data_list)}') # output: list
    except ValueError as e:
        print(f"error occured: {e}")
    result = [data_list[0], data_list[1]] #최종 반환될 리스트
    return result

def report_emotion(user_id, base_date):
    #DB 연결
    try:
        connection = psycopg2.connect(
                    host=env("DEV_DB_HOST"), 
                    # 데이터베이스 호스트 #database="your_database",  # 데이터베이스 이름
                    user=env("DEV_DB_USER"),      # 데이터베이스 사용자 이름
                    password=env("DEV_DB_PASSWORD"),  # 데이터베이스 비밀번 호
                    port=env("DEV_DB_PORT")                # 기본 PostgreSQL 포트
                    )
        print('complete to connect to db')
    except (Exception, psycopg2.Error) as error:
        print("db 연결 실패::", error)
    # 일기: 기준일로부터 7일 동안, 여기선 기준일을 2024-12-15로 한다.
    #mood랑 diary 조인해서 6일 간의 ymd, name, category 쿼리
    query = f"""
    SELECT d.ymd, m.name, m.category
    FROM diaries_diary d
    JOIN diaries_mood m
    ON d.moods_id = m.id
    WHERE user_id={user_id}
    AND ymd BETWEEN '{base_date}' AND '{base_date}'::date + INTERVAL '6 days';
    """
    result = emotion_query_postgre(connection, query) ##쿼리 결과
    emotion = {
    '희' : """긍정의 한주를 보낸 당신, 대단해요
    크고 작은 기쁨들이 있으셨군요!
    앞으로도 좋은 일들이 가득하길 바랍니다.""",
    '노' : """부정의 한주를 보낸 당신, 괜찮아요 혹시 화나는 일이 있으셨나요?
    분노를 느낄 때마다 깊게 숨을 들이마시고 내쉬며 마음을 가라앉혀 보세요.
    한결 나아질 거예요.""",
    '애' : """슬픔의 한주를 보낸 당신, 토닥토닥
    혹시 속상한 일이 있으셨나요?
    하지만 그만큼 성장하고 있다는 증거이기도 합니다.
    내일은 더 나은 날이 기다리고 있을 거예요.""",
    '락' : """즐거운 한주를 보낸 당신, 부러워요
    이번 주에는 즐거움이 많으셨군요!
    앞으로도 짜릿한 순간들이 계속되길 바랍니다.""",
    '섞' : """다양한 감정을 느낀 당신, 수고했어요
    즐거움은 힘이 되고, 어려움은 성장이 되니
    앞으로도 당신만의 속도로 걸어가길 바라요."""
    }
    emotion_aggregator = {
    '희': 0,
    '노': 0,
    '애': 0,
    '락': 0
    }
    for i in result: #감정에 따라 add dict value
        emotion_aggregator[i[2]] += 1 #i는 ['date', 'emotion', 'category']꼴
    # 최대 value 찾기
    max_value = max(emotion_aggregator.values())
    # 최대 value를 가지는 모든 key 찾기
    max_keys = [key for key, value in emotion_aggregator.items() if value == max_value]
    if len(max_keys) > 1:
        max_emotion = "섞"
    else:
        max_emotion = max_keys[0]

    weekly_emotions = [[i[0],i[1]] for i in result] #result에서 date, emotion 추출
    # 날짜를 datetime 객체로 변환하여 오름차순 정렬하고 요일도 추가
    sorted_weekly_emotions = sorted(weekly_emotions, key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'))
    # 요일을 추가한 새로운 리스트 만들기
    weekly_emotions_yoyeel = [[date, emotion, datetime.strptime(date, '%Y-%m-%d').strftime('%A')] for date, emotion in sorted_weekly_emotions]
    emotion_by_day = {
        'Sunday': '',
        'Monday': '',
        'Tuesday': '',
        'Wednesday': '',
        'Thursday': '',
        'Friday': '',
        'Saturday': ''
    }
    # 리스트에서 요일별로 감정을 딕셔너리에 저장
    for date, emotion2, day in weekly_emotions_yoyeel:
        #emotion_by_day[day].append(emotion)
        emotion_by_day[day] = emotion2
    #딕셔너리가 비어있다면 null 삽입
    for key in emotion_by_day:
        if not emotion_by_day[key]:
            #emotion_by_day[key].append('null')
            emotion_by_day[key] = 'null'
    #인덱스0부터 순서대로 일, 월, 화, ... 요일의 감정. null이면 일기 작성하지 않은 날
    final_weekly_emotion = [emotion_by_day['Sunday'], emotion_by_day['Monday'], emotion_by_day['Tuesday'], emotion_by_day['Wednesday'], emotion_by_day['Thursday'], emotion_by_day['Friday'], emotion_by_day['Saturday']]
    return [max_emotion, emotion[max_emotion], final_weekly_emotion]