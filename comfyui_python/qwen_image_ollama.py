import os
import random
import sys
from typing import Sequence, Mapping, Any, Union
import torch


def get_value_at_index(obj: Union[Sequence, Mapping], index: int) -> Any:
    """Returns the value at the given index of a sequence or mapping.

    If the object is a sequence (like list or string), returns the value at the given index.
    If the object is a mapping (like a dictionary), returns the value at the index-th key.

    Some return a dictionary, in these cases, we look for the "results" key

    Args:
        obj (Union[Sequence, Mapping]): The object to retrieve the value from.
        index (int): The index of the value to retrieve.

    Returns:
        Any: The value at the given index.

    Raises:
        IndexError: If the index is out of bounds for the object and the object is not a mapping.
    """
    try:
        return obj[index]
    except KeyError:
        return obj["result"][index]


def find_path(name: str, path: str = None) -> str:
    """
    Recursively looks at parent folders starting from the given path until it finds the given name.
    Returns the path as a Path object if found, or None otherwise.
    """
    # If no path is given, use the current working directory
    if path is None:
        path = os.getcwd()

    # Check if the current directory contains the name
    if name in os.listdir(path):
        path_name = os.path.join(path, name)
        print(f"{name} found: {path_name}")
        return path_name

    # Get the parent directory
    parent_directory = os.path.dirname(path)

    # If the parent directory is the same as the current directory, we've reached the root and stop the search
    if parent_directory == path:
        return None

    # Recursively call the function with the parent directory
    return find_path(name, parent_directory)


def add_comfyui_directory_to_sys_path() -> None:
    """
    Add 'ComfyUI' to the sys.path
    """
    comfyui_path = find_path("ComfyUI")
    if comfyui_path is not None and os.path.isdir(comfyui_path):
        sys.path.append(comfyui_path)
        print(f"'{comfyui_path}' added to sys.path")


def add_extra_model_paths() -> None:
    """
    Parse the optional extra_model_paths.yaml file and add the parsed paths to the sys.path.
    """
    try:
        from main import load_extra_path_config
    except ImportError:
        print(
            "Could not import load_extra_path_config from main.py. Looking in utils.extra_config instead."
        )
        from utils.extra_config import load_extra_path_config

    extra_model_paths = find_path("extra_model_paths.yaml")

    if extra_model_paths is not None:
        load_extra_path_config(extra_model_paths)
    else:
        print("Could not find the extra_model_paths config file.")


add_comfyui_directory_to_sys_path()
add_extra_model_paths()


def import_custom_nodes() -> None:
    """Find all custom nodes in the custom_nodes folder and add those node objects to NODE_CLASS_MAPPINGS

    This function sets up a new asyncio event loop, initializes the PromptServer,
    creates a PromptQueue, and initializes the custom nodes.
    """
    import asyncio
    import execution
    from nodes import init_extra_nodes
    import server

    # Creating a new event loop and setting it as the default loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Creating an instance of PromptServer with the loop
    server_instance = server.PromptServer(loop)
    execution.PromptQueue(server_instance)

    # Initializing custom nodes
    init_extra_nodes()


from nodes import NODE_CLASS_MAPPINGS


def main():
    import_custom_nodes()
    with torch.inference_mode():
        unetloadergguf = NODE_CLASS_MAPPINGS["UnetLoaderGGUF"]()
        unetloadergguf_5 = unetloadergguf.load_unet(unet_name="qwen-image-Q6_K.gguf")

        cliploader = NODE_CLASS_MAPPINGS["CLIPLoader"]()
        cliploader_6 = cliploader.load_clip(
            clip_name="qwen_2.5_vl_7b.safetensors", type="qwen_image", device="default"
        )

        cliptextencode = NODE_CLASS_MAPPINGS["CLIPTextEncode"]()
        cliptextencode_7 = cliptextencode.encode(
            text="drawing, text edit, human limbs",
            clip=get_value_at_index(cliploader_6, 0),
        )

        ollamaconnectivityv2 = NODE_CLASS_MAPPINGS["OllamaConnectivityV2"]()
        ollamaconnectivityv2_32 = ollamaconnectivityv2.ollama_connectivity(
            url="http://127.0.0.1:11434",
            model="qwen3:32b",
            keep_alive=5,
            keep_alive_unit="minutes",
        )

        ollamageneratev2 = NODE_CLASS_MAPPINGS["OllamaGenerateV2"]()
        ollamageneratev2_31 = ollamageneratev2.ollama_generate_v2(
            system="You are generating a prompt for qwen-image. A prompt should be different from previous generated prompt. Only respond with prompt.\n\nAt the end of prompt append 'With text on transparent foreground with rounded corners that says 'Blessed are the meek: for they shall inherit the earth. Matthew 5:5'. Provided text should be printed as is without any corrections.'",
            prompt="Create an appropriate prompt for photorealistic image illustrating 'Blessed are the meek: for they shall inherit the earth.\nMatthew 5:5'",
            think=False,
            keep_context=False,
            format="text",
            connectivity=get_value_at_index(ollamaconnectivityv2_32, 0),
        )

        cliptextencode_8 = cliptextencode.encode(
            text=get_value_at_index(ollamageneratev2_31, 0),
            clip=get_value_at_index(cliploader_6, 0),
        )

        emptylatentimage = NODE_CLASS_MAPPINGS["EmptyLatentImage"]()
        emptylatentimage_10 = emptylatentimage.generate(
            width=360, height=640, batch_size=1
        )

        vaeloader = NODE_CLASS_MAPPINGS["VAELoader"]()
        vaeloader_11 = vaeloader.load_vae(vae_name="qwen_image_vae.safetensors")

        upscalemodelloader = NODE_CLASS_MAPPINGS["UpscaleModelLoader"]()
        upscalemodelloader_29 = upscalemodelloader.EXECUTE_NORMALIZED(
            model_name="4xNomos8kSCHAT-L.pth"
        )

        ksampler = NODE_CLASS_MAPPINGS["KSampler"]()
        vaedecode = NODE_CLASS_MAPPINGS["VAEDecode"]()
        imageupscalewithmodel = NODE_CLASS_MAPPINGS["ImageUpscaleWithModel"]()
        saveimage = NODE_CLASS_MAPPINGS["SaveImage"]()
        previewany = NODE_CLASS_MAPPINGS["PreviewAny"]()

        for q in range(1):
            ksampler_27 = ksampler.sample(
                seed=random.randint(1, 2**64),
                steps=30,
                cfg=4,
                sampler_name="euler",
                scheduler="beta",
                denoise=1,
                model=get_value_at_index(unetloadergguf_5, 0),
                positive=get_value_at_index(cliptextencode_8, 0),
                negative=get_value_at_index(cliptextencode_7, 0),
                latent_image=get_value_at_index(emptylatentimage_10, 0),
            )

            vaedecode_28 = vaedecode.decode(
                samples=get_value_at_index(ksampler_27, 0),
                vae=get_value_at_index(vaeloader_11, 0),
            )

            imageupscalewithmodel_30 = imageupscalewithmodel.EXECUTE_NORMALIZED(
                upscale_model=get_value_at_index(upscalemodelloader_29, 0),
                image=get_value_at_index(vaedecode_28, 0),
            )

            saveimage_13 = saveimage.save_images(
                filename_prefix="ComfyUI",
                images=get_value_at_index(imageupscalewithmodel_30, 0),
            )

            previewany_36 = previewany.main(
                source=get_value_at_index(ollamageneratev2_31, 0)
            )


if __name__ == "__main__":
    main()
