import ast
import os
import psycopg2 #postgres
import io
import environ
from openai import OpenAI
from config.settings.base import BASE_DIR
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

env = environ.Env(DEBUG=(bool, True))

environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)

#일기 요약과 활동 추천
def query_postgre(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results
def ai_report():
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
    query = "SELECT content FROM diaries_diary WHERE user_id = 14 AND ymd BETWEEN '2024-12-15' AND '2024-12-15'::date + INTERVAL '6 days';" #일기 쿼리 : 일주일치
    diary = query_postgre(connection, query) #결과: [('내용1',), ('내용2',)] 튜플 만들어야 해서 쉼표가 있나봄
    diary_contents = [entry[0] for entry in diary]
    print(f'diary: {diary_contents}') #결과: ['내용1', '내용2']
    #키워드인데 일단 애매해서 뺌
    #query = "SELECT h.name FROM Hashtag h JOIN DiaryHashtag dh ON h.hashtag_id = dh.hashtag_id WHERE dh.diary_id IN (SELECT diary_id FROM Diary WHERE user_id = 14);" #키워드 쿼리
    #keywords = [query_postgre(connection, query)]
    # 관심사
    query = "SELECT i.name FROM accounts_interest i JOIN accounts_user_interests ui ON i.id = ui.interest_id WHERE ui.user_id = 14;" #관심사 쿼리
    interest = [query_postgre(connection, query)]
    interest_contents = [i[0] for i in interest[0]] #얘는 리스트형태로 나와서 interest[0]에서 첫 인덱스
    print(f'interest: {interest_contents}')
    #성격
    query = "SELECT p.name FROM accounts_personality p JOIN accounts_user_personalities up ON p.id = up.id WHERE up.user_id = 14;" # 성격 쿼리
    personality = [query_postgre(connection, query)]
    personality_contents = [i[0] for i in personality[0]] #얘는 리스트형태로 나와서 interest[0]에서 첫 인덱스
    print(f'personality: {personality_contents}')
    client = OpenAI(
        api_key = env('OPENAI_API_KEY'))
    system_instructions = """
    사용자는 너에게 사용자의 관심사, 성격, 일주일 간의 일기를 전송할 거야.
    먼저 일기를 토대로 일주일 간 있었던 일을 요약해 줘.
    그리고 관심사와 성격, 일기를 토대로 활동을 추천해.
    '일기 요약', '활동 추천'과 같은 제목은 답변에 넣지 마.
    답변은 이 양식을 따라 줘. : ['일기를 요약한 내용', ['추천 활동','추천한 이유'] ]
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
    result = [data_list[0]] #최종 반환될 리스트
    for item in data_list[1:]:
        transformed_item = [[item[0]], [item[1]]]
        result.append(transformed_item)
    return result