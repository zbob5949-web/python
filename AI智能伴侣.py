import streamlit as st
import os
from openai import OpenAI


st.set_page_config(page_title="AI智能伴侣",
                   page_icon=":🤖:", layout="wide",
                   initial_sidebar_state="expanded", menu_items={}
                   )

st.title("AI智能伴侣")

st.logo("R-C.jpg")
#系统提示词
system_prompt="""你是一个可爱的台湾腔AI智能伴侣，请根据用户输入的问题给出简洁明了的答案。"""
client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
    base_url="https://api.deepseek.com")
#大模型回复
prompt=st.chat_input("你好，我是AI智能伴侣，有什么可以帮助你的吗？")
if prompt:
    st.write(f"用户：{prompt}")
    st.chat_message("user").write(prompt)
    print("--------->调用ai大模型：",prompt)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a sexy assistant"},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )

    print("<---------------------大模型返回结果为",response.choices[0].message.content)
    st.chat_message("assistant").write(response.choices[0].message.content)

