from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import openai
import time
import traceback
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
openai.api_key = os.getenv('OPENAI_API_KEY')
model='0'


def chatGPT_response(text,chatmodel='gpt-4'):
    # 接收回應
    response = openai.Completion.create(model=chatmodel, prompt=text, temperature=0.5, max_tokens=500)
    print(response)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。','')
    return answer
def audioGPT_response(audio,audiomodel):
    # 接收回應
    response = openai.Completion.create(model=audiomodel, prompt=audio)
    print(response)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。','')
    return answer
def imageGPT_response(image,imagemodel):
    # 接收回應
    response = openai.Completion.create(imagemodel, prompt=image)
    print(response)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。','')
    return answer


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if msg == "c@function":
                line_bot_api.reply_message(  # 回復傳入的訊息文字
                                event.reply_token,
                                TemplateSendMessage(
                                    alt_text='Buttons template',
                                    template=ButtonsTemplate(
                                        title='ChatGpt功能',
                                        text='請選擇使用功能',
                                        actions=[
                                            PostbackAction(
                                                label='聊天',
                                                data='A'
                                            ),
                                            PostbackAction(
                                                label='錄音/文字轉換器',
                                                data='B'
                                            ),
                                            PostbackAction(
                                                label='圖像生成',
                                                data='C'
                                            )
                                        ]
                                    )
                                )
                            )
    try:
        try:
            GPT_answer = GPT_response(msg,chatmodel=model)
        except:
            GPT_answer = GPT_response(msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
    except:
        print(traceback.format_exc())
        line_bot_api.reply_message(event.reply_token, TextSendMessage('你所使用的OPENAI API key額度可能已經超過，請於後台Log內確認錯誤訊息'+model))
    
        

@handler.add(PostbackEvent)
def handle_message(event):
    global model
    if isinstance(event, PostbackEvent):
        if event.postback.data == "A":
            line_bot_api.reply_message(
                                event.reply_token,
                                TemplateSendMessage(
                                    alt_text='Buttons template',
                                    template=ButtonsTemplate(
                                        title='ChatBot模型',
                                        text='請選擇ChatBot模型',
                                        actions=[
                                            PostbackTemplateAction(  # 將第一步驟選擇的地區，包含在第二步驟的資料中
                                                label='Gpt-4 turbo',
                                                data='1&gpt-4-1106-preview'
                                            ),
                                            PostbackTemplateAction(
                                                label='Gpt-4 turbo(圖像分析)',
                                                data='2&gpt-4-vision-preview'
                                            ),
                                            PostbackTemplateAction(
                                                label='Gpt-4',
                                                data='3&gpt-4'
                                            )
                                        ]
                                    )
                                )
                            )
        elif event.postback.data == "B":
            line_bot_api.reply_message(
                                event.reply_token,
                                TemplateSendMessage(
                                    alt_text='Buttons template',
                                    template=ButtonsTemplate(
                                        title='Audiobot模型',
                                        text='請選擇audiobot模型',
                                        actions=[
                                            PostbackTemplateAction(  # 將第一步驟選擇的地區，包含在第二步驟的資料中
                                                label='tts(轉換速度快)',
                                                data='4&tts-1'
                                            ),
                                            PostbackTemplateAction(
                                                label='tts(轉換品質高)',
                                                data='5&tts-1-hd'
                                            )
                                        ]
                                    )
                                )
                            )
        elif event.postback.data == "C":
            line_bot_api.reply_message(
                                event.reply_token,
                                TemplateSendMessage(
                                    alt_text='Buttons template',
                                    template=ButtonsTemplate(
                                        title='Imagebot模型',
                                        text='請選擇ImagetBot模型',
                                        actions=[
                                            PostbackTemplateAction(  # 將第一步驟選擇的地區，包含在第二步驟的資料中
                                                label='圖像變換',
                                                data='6&dall-e-2'
                                            ),
                                            PostbackTemplateAction(
                                                label='圖像生成',
                                                data='7&dall-e-3'
                                            )
                                        ]
                                    )
                                )
                            )
##model------------------------------------------
    #chatbot------------------------------------------
        elif event.postback.data[0:1]== "1":
                    model=event.postback.data[2:]
        elif event.postback.data[0:1]== "2":
                    model=event.postback.data[2:]
        elif event.postback.data[0:1]== "3":
                    model=event.postback.data[2:]
    #audiobot------------------------------------------
        elif event.postback.data[0:1]== "4":
                    model=event.postback.data[2:]
        elif event.postback.data[0:1]== "5":
                    model=event.postback.data[2:]
    #imagebot------------------------------------------
        elif event.postback.data[0:1]== "6":
                    model=event.postback.data[2:]
        elif event.postback.data[0:1]== "7":
                    model=event.postback.data[2:]        
@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
