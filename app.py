import gradio as gr
import smtplib
from email.mime.text import MIMEText
from utils import *
import os


fail_msg = """<div style="text-align: center;">
<h3>✨ 처리할수 없는 키워드 입니다. 다른 키워드로 부탁 드립니다 ✨</h3>"""
# 이메일 전송 함수
def send_email(input1, input2, input3, email):
    path = f"/home/azureuser/example/{input1}_{input2}_{input3}"
    
    if False==os.path.isdir(path):
        check = make_vedio(input1, input2, input3)

        if check==-1:
            return fail_msg

    check = merge_data(path)
    if check==-1:
        return fail_msg

    check = email_send(path, email)
    if check==-1:
        return fail_msg
    

    return_msg = """<div style="text-align: center;">
<h3>✨ 동영상 제작이 완료 되었습니다! 메일을 확인해 보세요~! ✨</h3>  
    """
    return return_msg

# Gradio 인터페이스 설정
def process_inputs(input1, input2, input3, input4):
    return send_email(input1, input2, input3, input4)

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

# Launch
app.launch(server_name="0.0.0.0", server_port=8080)

