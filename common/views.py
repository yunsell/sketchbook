import openai
import requests
import json
from django.shortcuts import render




# 이미지 생성하기 요청
def t2i(prompt, negative_prompt):
    REST_API_KEY = 'b714f19047d1ba1f100ead851b9a00ac'

    r = requests.post(
        'https://api.kakaobrain.com/v2/inference/karlo/t2i',
        json = {
            'prompt': prompt,
            'negative_prompt': negative_prompt
        },
        headers = {
            'Authorization': f'KakaoAK {REST_API_KEY}',
            'Content-Type': 'application/json'
        }
    )
    # 응답 JSON 형식으로 변환
    response = json.loads(r.content)
    return response



def index(request):
    return render(request, 'common/index.html')


def generate_story(request):
    openai.api_key = "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"

    prompt = '아래 주제를 바탕으로 어린이들이 좋아할 만한 동화 이야기를 애기들도 이해 할 수 있고, 최대한 읽기 쉽게 만들어줘.'
    messages = [
        {"role": "system", "content": prompt},
    ]

    messages.append(
        {"role": "user",
        "content": """
            주인공: 윤세일
            주인공의 성별: 남자
            주인공의 나이: 10
            동화 주제: 마법에 걸린 숲 연대기 이야기 속 마법에 걸린 숲이 살아나는 이야기를 써보세요.
        """})

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
    )

    chat_response = completion.choices[0].message.content

    messages = [
        {"role": "user", "content": chat_response + ' 이 글에 해당되는 핵심이 되는 키워드를 영어로 추출해줘.'},
    ]

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
    )

    keys_of_story = completion.choices[0].message.content

    # 프롬프트에 사용할 제시어
    negative_prompt = ""

    # 이미지 생성하기 REST API 호출
    response = t2i(keys_of_story, negative_prompt)
    
    image = response.get("images")[0].get("image")

    context = {"image": image, "story": chat_response}

    return render(request, 'common/storyboard.html', context)
