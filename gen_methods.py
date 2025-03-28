import sys, zhmiscellany, copy, os, httpx
from llama_cpp import Llama
from openai import OpenAI
import tools.initialize_dynamics.method as initialize_dynamics


def parse_chat_to_string(lchat):
    loc = copy.deepcopy(lchat)
    text = []
    for message in loc:
        text.append('<|im_start|>' + message['role'] + '\n' + message['content'] + '<|im_end|>\n')
    text.append('<|im_start|>assistant\n')
    return ''.join(text)


def raw_gen(lchat, stop):
    llchat = parse_chat_to_string(lchat)
    #print(llchat)
    output = llm(
        llchat,
        stop=stop,
        max_tokens=n_ctx,
        temperature=0.1,
        top_k=40,
        top_p=0.1,
        repeat_penalty=1.1,
        min_p=0.05,
        stream=True
    )
    output_text = []
    for token in output:
        current_token = token['choices'][0]['text']
        output_text.append(current_token)
        print(current_token, end='')

    output_text = ''.join(output_text)
    print()
    return output_text


def raw_chat(messages, stop_tokens=None, do_print=True):
    if stop_tokens:
        output = llm.create_chat_completion(
            messages = messages,
            stream=True,
            max_tokens=n_ctx,
            temperature=0.1,
            top_k=40,
            top_p=0.1,
            repeat_penalty=1.1,
            min_p=0.05,
            stop=stop_tokens,
        )
    else:
        output = llm.create_chat_completion(
            messages = messages,
            stream=True,
            max_tokens=n_ctx,
            temperature=0.1,
            top_k=40,
            top_p=0.1,
            repeat_penalty=1.1,
            min_p=0.05,
        )

    output_text = []

    for token in output:
        if 'content' in token['choices'][0]['delta']:
            current_token = token['choices'][0]['delta']['content']
        else:
            current_token = None

        if current_token:
            output_text.append(current_token)

        if do_print and current_token:
            print(current_token, end='')

    output_text = ''.join(output_text)
    if do_print:
        print()

    return output_text


def force_load_llm(da_chat):
    def chat(messages, do_print=True):
        output = llm.create_chat_completion(
            messages=messages,
            stream=True
        )

        output_text = []

        for token in output:
            if 'content' in token['choices'][0]['delta']:
                current_token = token['choices'][0]['delta']['content']
            else:
                current_token = None

            if current_token:
                output_text.append(current_token)

            if do_print and current_token:
                print(current_token, end='')

        output_text = ''.join(output_text)
        if do_print:
            print()

        return output_text

    chat(
        da_chat,
        do_print=False,
    )


def apply_prompt_formatting(lchat, added_text=''):
    fuck = copy.deepcopy(lchat)
    prompt_format = {'system': {'pre': '<|im_start|>system\n', 'suf': '<|im_end|>\n'}, 'user': {'pre': '<|im_start|>user\n', 'suf': '<|im_end|>\n'}, 'assistant': {'pre': '<|im_start|>assistant\n', 'suf': '<|im_end|>\n'}}
    output = [{"role": "system", "content": ''''''}]

    for message in fuck:
        output[0]['content'] += prompt_format[message['role']]['pre']+message['content']+prompt_format[message['role']]['suf']
        #message['content'] = prompt_format[message['role']]['pre']+message['content']+prompt_format[message['role']]['suf']
    #fuck[-1]['content'] = fuck[-1]['content']+prompt_format['assistant']['pre']+added_text
    output[0]['content'] += prompt_format['assistant']['pre']+added_text
    return output


def lms_gen(lchat, stop):

    # this function is 10x more complicated then it needs to be thanks to all the bugs in LM Studio that I have to smooth over in code, like not streaming the last token in a batch and not formatting prompts correctly, so I have to handle all that here.

    client = OpenAI(base_url="http://localhost:50091/v1", api_key="not-needed")
    l_chat = copy.deepcopy(lchat)
    l_chat = apply_prompt_formatting(lchat)
    #print(l_chat)
    try:
        output = client.chat.completions.create(
            model='N/A',
            messages=l_chat,
            temperature=0.5,
            stream=True,
            stop=[]
        )
        output_text = []

        for token in output:
            current_token = token.choices[0].delta.content
            if current_token is not None:
                output_text.append(str(current_token))
                raw_output_text = ''.join(output_text)
                print(current_token, end='')

                if any(c in raw_output_text for c in initialize_dynamics.ending_tokens):
                    client.close()

                    module_used = None
                    for module_name in initialize_dynamics.modules:
                        if initialize_dynamics.modules[module_name]['properties']['is_tool']:
                            if initialize_dynamics.modules[module_name]['properties']['starting_token'] in raw_output_text:
                                module_used = module_name
                    if not module_used:
                        raw_output_text = raw_output_text.split(initialize_dynamics.default_stop_token)[0]
                        bsn = '\n'
                        print(f'\r{raw_output_text.split(bsn)[-1]}')
                    else:
                        raw_output_text = raw_output_text.split(initialize_dynamics.modules[module_used]['properties']['ending_token'])[0]

    except httpx.ReadError as e:
        pass
    print()
    return raw_output_text


def openai_gen(lchat, stop):
    l_chat = copy.deepcopy(lchat)
    l_chat = apply_prompt_formatting(l_chat)
    client = OpenAI(api_key='')
    try:
        output = client.chat.completions.create(
            model='gpt-4',
            messages=l_chat,
            temperature=0.5,
            stream=True
        )
        output_text = []

        for token in output:
            current_token = token.choices[0].delta.content
            if current_token is not None:
                output_text.append(str(current_token))
                raw_output_text = ''.join(output_text)
                print(current_token, end='')

                if any(c in raw_output_text for c in initialize_dynamics.ending_tokens):
                    client.close()

                    module_used = None
                    for module_name in initialize_dynamics.modules:
                        if initialize_dynamics.modules[module_name]['properties']['is_tool']:
                            if initialize_dynamics.modules[module_name]['properties']['starting_token'] in raw_output_text:
                                module_used = module_name
                    if not module_used:
                        raw_output_text = raw_output_text.split(initialize_dynamics.default_stop_token)[0]
                        bsn = '\n'
                        print(f'\r{raw_output_text.split(bsn)[-1]}')
                    else:
                        raw_output_text = raw_output_text.split(initialize_dynamics.modules[module_used]['properties']['ending_token'])[0]

    except httpx.ReadError as e:
        pass
    print()
    return raw_output_text

gen_method = zhmiscellany.fileio.read_json_file('base_properties.json')['gen_method']
if gen_method == 'raw_model':
    model = r"C:\Users\zenma\models\TheBloke\dolphin-2_6-phi-2-GGUF\dolphin-2_6-phi-2.Q6_K.gguf"
    model = r"C:\Users\zenma\models\TheBloke\dolphin-2.6-mistral-7b-GGUF\dolphin-2.6-mistral-7b.Q5_K_M.gguf"
    model = r"C:\Users\zenma\Downloads\internlm2_5-7b-chat-Q2_K.0.gguf"
    model = r"..\internlm2_5-7b-chat-Q5_K_M.0.gguf"
    n_ctx = 32768
    llm = Llama(
        model_path=model,  # Download the model file first
        n_ctx=n_ctx,  # The max sequence length to use - note that longer sequence lengths require much more resources
        n_threads=8,            # The number of CPU threads to use, tailor to your system and the resulting performance
        n_gpu_layers=-1,         # The number of layers to offload to GPU, if you have GPU acceleration available
        verbose=False
    )
elif gen_method == 'lm_studio':
    pass
elif gen_method == 'openai':
    pass