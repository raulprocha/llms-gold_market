import torch, json

def generate_json_response(prompt, model, tokenizer, device, max_new_tokens=256):
    
    conv =[{"role":"user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        conv,
        tokenize =False,
        add_generation_prompt =True
    )
    inputs = tokenizer(text, return_tensors="pt").to(device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False, 
            temperature =0.0,
            pad_token_id=tokenizer.eos_token_id,
        )
    decoded = tokenizer.decode(output[0], skip_special_tokens=True).strip()
    try:
        return json.loads(decoded)
    except Exception:
        return {"raw_prediction": decoded}
