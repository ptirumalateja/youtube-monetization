#!/usr/bin/env bash
# Downloads all models for the Slow Light pipeline onto the RunPod network volume.
# Stills: Qwen-Image-Edit 2511 (fp8) + Lightning 4-step LoRA.
# Video:  Wan 2.2 I2V A14B (fp8, high + low noise) + Lightx2v 4-step LoRAs; LTX-2.3 distilled fp8.
# Upscale: SeedVR2 3B/7B int8. Network volume: 150 GB.
set -e
C=$(dirname "$(find /workspace -maxdepth 4 -name main.py -path '*ComfyUI*' | head -1)")
[ -d "$C/models" ] || { echo "ComfyUI not found under /workspace"; exit 1; }
echo "ComfyUI at $C"
HF=https://huggingface.co
get() { mkdir -p "$C/models/$1"; wget -c -q --show-progress -O "$C/models/$1/$(basename "$2")" "$HF/$2"; }

# Stills (~31 GB)
get diffusion_models Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2511_fp8mixed.safetensors
get text_encoders    Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors
get vae              Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors
get loras            lightx2v/Qwen-Image-Edit-2511-Lightning/resolve/main/Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors

# Video (~38 GB)
get diffusion_models Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors
get diffusion_models Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors
get vae              Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors
get text_encoders    Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors
get loras            Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors
get loras            Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors

# LTX-2.3 video (~37 GB): distilled fp8 checkpoint, Gemma 3 text encoder, latent upscaler
get checkpoints/LTX-2.3      Lightricks/LTX-2.3-fp8/resolve/main/ltx-2.3-22b-distilled-fp8.safetensors
get text_encoders            Comfy-Org/ltx-2/resolve/main/split_files/text_encoders/gemma_3_12B_it_fp4_mixed.safetensors
get latent_upscale_models    Lightricks/LTX-2.3/resolve/main/ltx-2.3-spatial-upscaler-x2-1.1.safetensors

# SeedVR2 upscaler (~12 GB): 3B for video, 7B for stills
get vae                      Comfy-Org/SeedVR2/resolve/main/vae/seedvr2_ema_vae_fp16.safetensors
get diffusion_models         Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_3b_int8_convrot.safetensors
get diffusion_models         Comfy-Org/SeedVR2/resolve/main/diffusion_models/seedvr2_7b_int8_convrot.safetensors

# Reference image
mkdir -p "$C/input/slowlight"
echo "Done. Upload refs/abhimanyu_ref.png to $C/input/slowlight/ (or Claude will do it via the API)."
df -h /workspace | tail -1
