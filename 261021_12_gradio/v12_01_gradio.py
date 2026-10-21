import gradio as gr


def say_hello(name):
    return "Hello " + name


gr_web = gr.Interface(
    fn=say_hello,
    inputs="text",
    outputs="text",
)

gr_web.launch(share=True)
