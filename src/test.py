from gradio_client import Client

print("starting")
client = Client("stabilityai/stable-diffusion-3-medium")
result = client.predict(
		prompt="Hello!!",
		negative_prompt="Hello!!",
		seed=0,
		randomize_seed=True,
		width=1024,
		height=1024,
		guidance_scale=5,
		num_inference_steps=28,
		api_name="/infer"
)
print(result)