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

prompt =input("Enter the problem you want to solve:")
text = input("Please enter the basis or material of the question: ")



messages = [
    {"role": "system", "content": """
     
    context:This marine ranch, situated along the subtropical and temperate coastal zones, employs a cage culture system in waters ranging from 5 to 15 meters deep. The tidal currents significantly influence the environment, with salinity fluctuations between 25‰ and 32‰. During the recent summer heatwave, water temperatures consistently hovered between 28-30℃ Celsius. Some fish cages exhibited symptoms including sluggish movement, reduced appetite, and pinpoint hemorrhages on their skin, resulting in a mortality rate of approximately 3% that continues to rise. The ranch operators lack professional fish disease diagnosis expertise and previously relied on irregular inspections by local veterinarians. To meet market demand, the stocking density has been increased by 20% compared to spring levels.
    text:You are an expert on Marine ranching. Based on authoritative materials related to offshore aquaculture and fish disease diagnosis, please answer the questions according to the context.
    input_data:You are given a question and some context information, please answer the question based on the context information.
    output_format:Your answer should be in plain text, do not use any special characters such as #, *, etc.In addition, the answer needs to be output in Chinese text.The problem is output in a three-tier structure of "problem location-solution-implementation tool"
        """},
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
