import os
import inspect

import gradio as gr
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM


from modules.paths_internal import models_path
from modules import (
    generation_parameters_copypaste as parameters_copypaste,
)  # pylint: disable=import-error # noqa


try:
    from modules.call_queue import wrap_gradio_gpu_call
except ImportError:
    from webui import wrap_gradio_gpu_call  # pylint: disable=import-error


available_prompt_type = [
    "<MORE_DETAILED_CAPTION>",
    "<DETAILED_CAPTION>",
    "<CAPTION>",
]

available_models = [
    "microsoft/Florence-2-large-ft",
    "microsoft/Florence-2-base-ft",
    "microsoft/Florence-2-large",
    "microsoft/Florence-2-base",
]


def generate_prompt_fn(
    image: Image,
    model_name: str,
    max_new_token: float,
    prompt_type: str,
):

    model_path = os.path.join(models_path, "florence2", model_name)

    if not os.path.exists(model_path):
        print(f"Downloading model to: {model_path}")
        from huggingface_hub import snapshot_download

        snapshot_download(
            repo_id=model_name, local_dir=model_path, local_dir_use_symlinks=False
        )

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
    )

    processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)

    inputs = processor(text=prompt_type, images=image, return_tensors="pt")

    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=int(max_new_token),
        do_sample=False,
        num_beams=3,
    )
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

    parsed_answer = processor.post_process_generation(
        generated_text,
        task=prompt_type,
        image_size=(image.width, image.height),
    )
    print(parsed_answer)

    result = parsed_answer[prompt_type]

    return result, result


def on_ui_tabs():

    with gr.Blocks(analytics_enabled=False) as florence_interface:
        with gr.Row():
            # input
            with gr.Column(variant="panel"):
                if "sources" in inspect.signature(gr.Image).parameters:
                    image = gr.Image(sources=["upload"], interactive=True, type="pil")
                else:
                    image = gr.Image(interactive=True, type="pil")

                model_name = gr.Dropdown(
                    label="Select Model",
                    choices=available_models,
                    value=available_models[0],
                )

                with gr.Row():
                    max_new_token = gr.Number(
                        label="Max new token", value=1024, minimum=1, maximum=4096
                    )
                    prompt_type = gr.Dropdown(
                        label="Prompt Type",
                        choices=available_prompt_type,
                        value=available_prompt_type[0],
                    )

                generate_btn = gr.Button(value="Generate", variant="primary")

            # output
            with gr.Column(variant="panel"):
                tags = gr.State(value="")
                html_tags = gr.HTML(
                    value="Output<br><br><br><br>",
                    label="Tags",
                    elem_id="tags",
                )

                with gr.Row():
                    parameters_copypaste.bind_buttons(
                        parameters_copypaste.create_buttons(
                            ["txt2img", "img2img"],
                        ),
                        None,
                        tags,
                    )

            generate_btn.click(
                fn=wrap_gradio_gpu_call(generate_prompt_fn),
                inputs=[image, model_name, max_new_token, prompt_type],
                outputs=[tags, html_tags],
            )

    return [(florence_interface, "Florence", "florence")]


# Setup A1111 initialisation hooks
try:
    import modules.script_callbacks as script_callbacks

    script_callbacks.on_ui_tabs(on_ui_tabs)
except:
    pass
