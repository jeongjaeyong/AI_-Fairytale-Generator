from openai import OpenAI

def make_vedio(key1, key2, key3):
    from openai import OpenAI
    import os
    try:
        client = OpenAI()
        prompt = """
너는 사용자의 입력을 정보를 바탕으로 동화를 만들어 주는 AI야

사용자가 입력하는 조건에 맞는 재밌는 동화를 4개의 문단으로 구성된 동화는 만들어줘!

조건 : 말투는 상냥하게, 전개는 기승전결을 맞춰서!
조건 : 주인공은 1명이고, 주인공의 생김새를 간단하게 묘사해줘!
조건 : 주인공이 외의 다른 사람은 등장하지 않도록 해줘.
조건 : 각 문단은 그림을 그리기 위한 프롬프트로 "그림용 문단"으로 요약한 프롬프트를 제공해줘

출력 포맷
```JSON
{
이름:"...",
생김새:"...",
문단1:"...",
그림용 문단1:"...",
문단2:"...",
그림용 문단2:"...",
문단3:"...",
그림용 문단3:"...",
문단4:"..."
그림용 문단4:"...",
}
```
"""
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"키워드 : {key1}, {key2}, {key3}"
                }
            ],
            response_format={ "type": "json_object" }
   
        )

        import json
        data = json.loads(completion.choices[0].message.content)

        for i in range(1,5):
            data[f'그림용 문단{i}_image'] = data[f'문단{i}'].replace(data["이름"], f'{data["이름"]}({data["생김새"]})')
    
        import requests
        from PIL import Image
        from io import BytesIO


        # 만들고자 하는 폴더 경로 (절대 경로 또는 상대 경로)
        path = f"/home/azureuser/example/{key1}_{key2}_{key3}"
        os.makedirs(path, exist_ok=True)
        import pickle
        with open(f"{path}/log.pickle","wb") as fw:
            pickle.dump(data,fw)
        # 폴더 생성 (필요한 상위 디렉토리까지 생성)
        for i in range(1,5):
            response = client.images.generate(
            model="dall-e-3",
            prompt="시드번호 3985654853를 사용해서 이라스토야 그림체로 그려줘!, 문장 :"+data[f'그림용 문단{i}_image'],
            size="1024x1024",
            quality="standard",
            n=1,
        )
   
            # 이미지 다운로드
            response = requests.get(response.data[0].url)

            # 응답 상태 확인 (200이면 정상)
            if response.status_code == 200:
                # 이미지 데이터를 메모리에서 읽기
                img = Image.open(BytesIO(response.content))
                # 이미지 저장
                img.save(f"{path}/downloaded_image{i}.jpg")
                print("이미지가 성공적으로 다운로드되었습니다!")
            else:
                print("이미지 다운로드 실패. 상태 코드:", response.status_code)

        for i in range(1,5):
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=data[f'문단{i}'],
            )
            response.stream_to_file(f"{path}/output{i}.mp3")
        return 0

    except Exception as e:
        print(e)
        return -1



def merge_data(path):
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
    import requests
    from PIL import Image
    from io import BytesIO

    try:
        # 이미지 파일 경로 리스트
        image_files = [f"{path}/downloaded_image{i}.jpg" for i in range(1, 5)]

        # 오디오 파일 경로 리스트
        audio_files = [f"{path}/output{i}.mp3" for i in range(1, 5)]
    except:
        return -1

    # 이미지와 오디오 클립을 결합할 리스트
    video_clips = []

    # 이미지와 오디오를 대응시켜서 동영상 클립 생성
    for i in range(len(image_files)):
        print(f"\nProcessing clip {i+1}")

        # 이미지 클립 만들기
        try:
            image_clip = ImageClip(image_files[i])
            print(f"Loaded image: {image_files[i]}")
        except Exception as e:
            print(f"Error loading image {image_files[i]}: {e}")
            continue

        # 이미지 크기 확인
        print(f"ImageClip size before resize: {image_clip.size}")

        # 이미지 크기 통일
        target_size = (1280, 720)  # 원하는 해상도로 설정
        image_clip = image_clip.resize(newsize=target_size)
        print(f"ImageClip size after resize: {image_clip.size}")

        # 오디오 클립 만들기
        try:
            audio_clip = AudioFileClip(audio_files[i])
            print(f"Loaded audio: {audio_files[i]}")
        except Exception as e:
            print(f"Error loading audio {audio_files[i]}: {e}")
            return -1

        # 이미지 클립의 지속 시간을 오디오 클립의 길이에 맞추기
        image_clip = image_clip.set_duration(audio_clip.duration)
        print(f"ImageClip duration set to: {audio_clip.duration}")

        # 오디오를 이미지 클립에 결합하기
        image_clip = image_clip.set_audio(audio_clip)

        # fps 설정
        image_clip.fps = 24
        print(f"ImageClip fps set to: {image_clip.fps}")

        # 이미지 클립을 리스트에 추가
        video_clips.append(image_clip)

    # 모든 동영상 클립을 순차적으로 결합하기
    final_video = concatenate_videoclips(video_clips, method="compose")

    # 최종 비디오 클립 속성 확인
    print(f"\nFinal video size: {final_video.size}")
    print(f"Final video duration: {final_video.duration}")
    print(f"Final video fps before setting: {getattr(final_video, 'fps', 'Not set')}")

    # fps 설정
    final_video.fps = 24
    print(f"Final video fps after setting: {final_video.fps}")

    # 출력 동영상 파일 경로
    output_path = f"{path}/output_video.mp4"

    # 동영상 파일로 저장
    final_video.write_videofile(output_path, fps=24)

    print("동영상이 성공적으로 생성되었습니다!")
    return 0
def email_send(path, email):
    import smtplib
    import os
    from email.message import EmailMessage

    # 이메일 계정 정보 설정
    smtp_server = 'smtp.gmail.com'  # SMTP 서버 주소 (예: Gmail의 경우 smtp.gmail.com)
    smtp_port = 587  # SMTP 포트 번호 (TLS: 587, SSL: 465)
    email_user = os.environ.get('MAIL_NAME')  # 본인 이메일 주소
    email_password = os.environ.get('MAIL_PASSWD')  # 이메일 비밀번호 또는 앱 비밀번호
    # 이메일 내용 설정
    from_email = email_user
    to_email = email  # 수신자 이메일 주소
    subject = '동화 제작 파일입니다'
    body = '이메일 본문입니다. mp4 파일이 첨부되어 있습니다.'
    attachment_path = f'{path}/output_video.mp4'  # 첨부할 mp4 파일 경로

    # 이메일 메시지 생성
    msg = EmailMessage()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)

    # mp4 파일 첨부
    with open(attachment_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype='video', subtype='mp4', filename=file_name)

    # 이메일 전송
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # TLS 시작
            server.login(email_user, email_password)  # 로그인
            server.send_message(msg)
        print('이메일이 성공적으로 전송되었습니다.')
        return 0
    except Exception as e:
        print(f'이메일 전송 중 오류 발생: {e}')
        return -1



