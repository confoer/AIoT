from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import transformers.utils.logging as logging
logging.disable_progress_bar()
device = "cuda" # the device to load the model onto
path = 'D:\OceanGPT'
model = AutoModelForCausalLM.from_pretrained(
    path,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True  
)
tokenizer = AutoTokenizer.from_pretrained(path)

prompt =input("Please enter your prompt: ")

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(device)

generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512,
    past_key_values=None,
    use_cache=False,
    pad_token_id=tokenizer.eos_token_id
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)
