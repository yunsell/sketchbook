import re
import openai
import requests
import json
from django.shortcuts import render
from .models import Story, POST

# 이미지 생성하기 요청
def t2i(prompt, negative_prompt):
    # Kakao Karlo API Key 입력
    REST_API_KEY = 'REST_API_KEY'

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
    print("#### generate_story 시작 ####")

    # OpenAI API Key 입력
    openai.api_key = "openai_api_key"

    prompt = """아래 주제를 바탕으로 아이가 좋아하는 동화를 만들어줘. 내용은 너무 길지 않게, 기승전결에 따라 4개의 문단으로 나눠줘(엔터 2번으로), 최대한 읽기 쉽게 만들어줘.
1장:
2장:
3장:
4장:
"""
    messages = [
        {"role": "system", "content": prompt},
    ]

    title = request.POST.get('title')
    character_name = " " + request.POST.get('character')
    character_sex = " " + request.POST.get('gender')
    character_age = " " + request.POST.get('age')
    story_theme = " " + request.POST.get('contents')

    print(title, character_name, character_sex, character_age, story_theme)

    messages.append(
        {"role": "user",
         "content": f"""
            제목: {title}
            주인공: {character_name}
            주인공의 성별: {character_sex}
            주인공의 나이: {character_age}
            동화 주제: {story_theme}
         """})

    completion = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages
    )

    chat_response = completion.choices[0].message.content

    # 응답을 문단별로 나누기 테스트 필요

    split_response = re.sub(r'([0-9]+장:)', '', chat_response )
    print("split_result ==> ", split_response)
    split_response = split_response.split('\n\n')
    split_response_list = [x.replace('\n', '') for x in split_response]
    print("split_result1 ==> ", split_response_list[0])
    print("split_result2 ==> ", split_response_list[1])
    print("split_result3 ==> ", split_response_list[2])

    story = Story.objects.create(title=title)

    for split_res in split_response_list:
        
        messages = [
            {"role": "user", "content": title + character_sex + character_age + story_theme + ', ' + split_res + ' 이 글에 해당되는 핵심이 되는 키워드를 영어로 추출해줘. (단, 이름은 제외)'},
        ]

        completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
        )

        # 프롬프트에 사용할 스타일
        prompt_style = "children's animate style, fairy tales style, no text, "
        keys_of_story = completion.choices[0].message.content
        print("image_prompt ==> ", keys_of_story)

        # 프롬프트에 사용할 제시어
        negative_prompt = ""

        # 이미지 생성하기 REST API 호출
        response = t2i(prompt_style + keys_of_story, negative_prompt)
        
        image = response.get("images")[0].get("image")
        post = POST.objects.create(story=story, message=split_res, image_url=image)
        post.get_remote_image()
    

    posts = POST.objects.filter(story=story).order_by('created_at')

    print(posts[0])
    context = {"image": image, "story": story, "posts": posts}

    return render(request, 'common/storyboard.html', context)
