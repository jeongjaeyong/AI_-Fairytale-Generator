import gradio as gr
import smtplib
from email.mime.text import MIMEText
from utils import *
import os
import asyncio
import threading
fail_msg = """<div style="text-align: center;">
<h3>✨ 처리할수 없는 키워드 입니다. 다른 키워드로 부탁 드립니다 ✨</h3>"""
# 이메일 전송 함수
def send_email(input1, input2, input3, email):
    path = f"/home/azureuser/example/{input1}_{input2}_{input3}"
    
    if False==os.path.isdir(path):
        check = make_vedio(input1, input2, input3)

        if check==-1:
            print("Make Vedio Error")
            return -1

    check = merge_data(path)
    if check==-1:
        print("Merge data Error")
        return -2

    check = email_send(path, email)
    if check==-1:
        print("Email Send Error")
        return -1
    
    print("All process complete!")

# Gradio 인터페이스 설정
def process_inputs(input1, input2, input3, input4):
    thread = threading.Thread(target=send_email, args=(input1, input2, input3, input4))
    thread.start()
    return_msg = """<div style="text-align: center;">
<h3>✨ 이메일이 5분 뒤에 도착할 예정입니다! ✨</h3></div>"""
    return return_msg


# Gradio UI
with gr.Blocks(css="#main-block {background-image: url('https://example.com/fairy-tale-bg.jpg'); background-size: cover;}") as app:
    gr.Markdown("""
    # ✨ **동화나라 메시지 전송** ✨
    **키워드 3개로 나만의 소중한 이야기를 만들어보세요!**
    ***(대략 5분 정도의 시간이 소요 됩니다!)***
    """, elem_id="main-title")
    
    with gr.Row():
        with gr.Column():
            input1 = gr.Textbox(label="🧚 Keyword 1", placeholder="동화 속 첫 번째 키워드")
            input2 = gr.Textbox(label="🧚 Keyword 2", placeholder="동화 속 두 번째 키워드")
            input3 = gr.Textbox(label="🧚 Keyword 2", placeholder="동화 속 세 번째 키워드")
        
        with gr.Column():
            output = gr.Textbox(label="✨ 결과를 받을 이메일 ✨")
    
    send_button = gr.Button("🌟 메시지 전송 🌟")

    with gr.Row():
        label = gr.Markdown()
    send_button.click(process_inputs, inputs=[input1, input2, input3, output], outputs=label)
    gr.HTML("""
    <script>
    const sendButton = document.getElementById('send-button');
    sendButton.addEventListener('click', () => {
        sendButton.disabled = true;
        setTimeout(() => {
            sendButton.disabled = false;
        }, 10000); // 10초 후 버튼 활성화
    });
    </script>
    """)
# Launch
app.launch(server_name="0.0.0.0", server_port=8080)

