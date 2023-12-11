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
from openai import OpenAI
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
OpenAI.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()
userID=''
mins=0
def chatGPT_response(text,chatmodel='gpt-4'):
    # 接收回應
    response = client.chat.completions.create(model=chatmodel, 
                                              messages = [
                                                {'role': 'user', 'content': text}
                                              ], 
                                              temperature=0.5
                                             )
    print(response)
    # 重組回應
    answer = response.choices[0].message.content
    return answer
def audioGPT_response(audio,audiomodel):
    # 接收回應
    response=client.audio.transcriptions.create(model=audiomodel,
                                                file=audio,
                                                response_format="text")
    answer =response
    return answer
def imageGPT_generate_response(imagetext,imagemodel):
    # 接收回應
    response = client.images.generate(prompt = imagetext,
                n=1,
                model=imagemodel,
                size="1024x1024"
            )
    image_url = response.data[0].url.strip()
    # 重組回應
    return image_url
def timecount(x):
   for i in range(10):
        x+=1
        time.sleep(60)
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
    if event.source.user_id ==userID:
        mins=0
        if msg == 'c@useid':
            userID=event.source.user_id
        elif msg == "c@function":
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
        elif mode =='Image':
                print('成功')
                try:
                    image_url=imageGPT_generate_response(msg,imagemodel)
                    line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))
                except:
                    print(traceback.format_exc())
                    line_bot_api.reply_message(event.reply_token, TextSendMessage('你所使用的OPENAI API key額度可能已經超過，請於後台Log內確認錯誤訊息---目前模式:'+mode))
        else:   
                try:
                    if model=='':
                        GPT_answer = chatGPT_response(msg)
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
                        
                    else:
                        GPT_answer = chatGPT_response(msg,chatmodel=model)
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
                except:
                    print(traceback.format_exc())
                    line_bot_api.reply_message(event.reply_token, TextSendMessage('你所使用的OPENAI API key額度可能已經超過，請於後台Log內確認錯誤訊息---目前模型:'+model))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('Bot使用中!請稍後'))
    
        

@handler.add(PostbackEvent)
def handle_message(event):
    global model
    global mode
    global imagemodel
    global audiomodel
    mins=0
    if isinstance(event, PostbackEvent):
        if event.postback.data == "A":
            mode='Chat'
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
            mode='Audio'
            audiomodel='whisper-1'
            print(audiomodel)
            line_bot_api.reply_message(event.reply_token, TextSendMessage('目前使用語音模型:'+audiomodel+'---請輸入語音檔---'))
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
            line_bot_api.reply_message(event.reply_token, TextSendMessage('目前使用語言模型:'+model+'---請輸入文字---'))
        elif event.postback.data[0:1]== "2":
            model=event.postback.data[2:]
            line_bot_api.reply_message(event.reply_token, TextSendMessage('目前使用語言模型:'+model+'---請輸入文字---'))
        elif event.postback.data[0:1]== "3":
            model=event.postback.data[2:]
            line_bot_api.reply_message(event.reply_token, TextSendMessage('目前使用語言模型:'+model+'---請輸入文字---'))
    #audiobot------------------------------------------
    #imagebot------------------------------------------
        elif event.postback.data[0:1]== "6":
            imagemodel=event.postback.data[2:]
            line_bot_api.reply_message(event.reply_token, TextSendMessage('目前使用繪圖模型:'+imagemodel+'---請輸入圖片---'))
        elif event.postback.data[0:1]== "7":
            imagemodel=event.postback.data[2:]
            mode='Image'
            line_bot_api.reply_message(event.reply_token, TextSendMessage('目前使用繪圖模型:'+imagemodel+'---請輸入圖片描述---'))
@handler.add(MessageEvent, message=AudioMessage)  # 取得聲音時做的事情
def handle_message_Audio(event):
    mins=0
    #接收使用者語音訊息並存檔
    UserID = event.source.user_id
    path="./audio/"+UserID+".mp3"
    audio_content = line_bot_api.get_message_content(event.message.id)
    path='./temp.mp3'
    with open(path,'wb') as audio:
       for chuck in audio_content.iter_content():
          audio.write(chuck)
    print(audio)
    with open('temp.mp3','rb') as audio_file:     
        try:
            Audio_answer=audioGPT_response(audio_file,audiomodel)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(Audio_answer))
        except:
            print(traceback.format_exc())
            line_bot_api.reply_message(event.reply_token, TextSendMessage('錯誤'))
    
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
