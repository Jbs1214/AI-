import gradio as gr
from deep_translator import MyMemoryTranslator


def trans_ko_to_en(text):
    en_text = MyMemoryTranslator(source="ko-KR", target="en-US").translate(text)
    return en_text


gr.Interface(fn=trans_ko_to_en, inputs="text", outputs="text", title="한국말을 영어로 번역", description="한국말 입력 시 영어로 번역됨").launch(share=True)