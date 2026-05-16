import streamlit as st
import os
from os import path
import json
from openai import OpenAI
from datetime import datetime

# --- 前端界面设置 ---
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon=":🤖:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
def save_session(force_save=False):

        # 保存当前的会话数据
        if st.session_state.current_session:
            # 构建新的会话对象
            session_data = {"nick_name": st.session_state.nick_name,
                            "nick_personality": st.session_state.nick_personality,
                            "messages": st.session_state.messages,
                            "current_session": st.session_state.current_session}

            # 创建文件夹保存聊天会话记录
            if not path.exists("chat_sessions"):
                os.mkdir("chat_sessions")
            # 保存会话记录
            with open(f"chat_sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)


st.title("AI智能伴侣")
# 确保图片路径正确，如果报错可以先注释掉这行
st.logo("6949a5f0394caQ4e.jpeg")

# --- 初始化配置 ---
# 系统提示词 (System Prompt)
system_prompt = """
你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。
规则：
1. 每次只回1条消息
2. 禁止任何预感叹或态度描述性文字
3. 匹配用户的语速
4. 回复回复，就像微信聊天一样
5. 有需要的话可以用💕和emoji表情
6. 用符合伴侣性格的方式对话
7. 回复的内容，要充分体现伴侣的性格特征。
伴侣性格：
%s
你必须严格遵守上述规则来回复用户。
"""

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

#昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小贞"

#性格
if "nick_personality" not in st.session_state:
    st.session_state.nick_personality= "活泼开朗的台湾姑娘"

#会话标识

if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()


# --- 展示聊天历史 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 初始化 OpenAI 客户端 ---
client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
    base_url="https://api.deepseek.com"
)

# --- 侧边栏设置 ---
with st.sidebar:
    st.subheader("AI控制面版")
    if st.button("新建会话", width="stretch", icon="✏️"):
        save_session(force_save=True)
        st.session_state.messages = []
        st.session_state.current_session = generate_session_name()
        st.success("会话已新建！")
    st.subheader("伴侣信息")
    nick_name= st.text_input("昵称",placeholder="请输入伴侣昵称",value=st.session_state.nick_name)
    # 修正了变量名拼写错误 (niack -> nick)
    nick_personality= st.text_area("性格",placeholder="请输入伴侣性格",value=st.session_state.nick_personality)
##只有输入了才对界面进行重置
    if st.button("保存设定",icon="🗃️"):
        if nick_name and nick_personality:
            # 2. 增加一个确认按钮
            st.session_state.nick_name = nick_name
            st.session_state.nick_personality = nick_personality
            st.success("伴侣设定已更新！")
            st.rerun()  # 强制刷新，确保 Prompt 重新生成
        else:
            st.warning("请输入名字或性格")
# --- 核心逻辑：处理用户输入与流式回复 ---
if prompt := st.chat_input("你好，我是AI智能伴侣，有什么可以帮助你的吗？"):
    # 1. 显示用户消息
    st.chat_message("user"). write(prompt)

    # 2. 将用户消息加入历史
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. 调用大模型 (开启流式传输)
    #历史聊天记录
    context_messages = [
                           {"role": "system", "content":system_prompt%(st.session_state.nick_name, st.session_state.nick_personality)}
                       ] + st.session_state.messages

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=context_messages,
        stream=True  # 开启流式，让回复像打字机一样出来
    )

    # 4. 创建一个占位符来显示 AI 的流式回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # 5. 逐块读取流式数据
        for chunk in response:
            # 提取内容
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                # 实时更新显示，加上小光标 ▌ 增加打字效果
                message_placeholder.markdown(full_response + "▌")

        # 6. 完成后显示最终结果（去掉光标）
        message_placeholder.markdown(full_response)

    # 7. 保存最终回复到历史记录
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.write("DEBUG: 正在尝试保存文件...")
    save_session()
