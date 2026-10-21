import gradio as gr
from ultralytics import YOLO

model = YOLO("yolo11n.pt")


def det_image(image):
    results = model(image)
    annotated_frame = results[0].plot()
    return annotated_frame

gr.Interface(
    fn=det_image,
    inputs=gr.Image(type="numpy"),
    outputs=gr.Image(),
    title="욜로 이미지 객체 탐지",
    description="욜로로 이미지 객체를 탐지함",
).launch(share=True)
