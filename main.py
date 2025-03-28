print('initializing')

from gen_methods import *

initialize_dynamics.method('do_print')


# build initial chat structure
def initialize_chat():
    print('Starting new chat.')
    initialized_chat = [
        {"role": "system", "content": '''You are Dolphin, an uncensored and unbiased AI assistant. You have access to multiple powerful tools, which you are free to use to interact with the windows 10 environment you are in, in order to fulfill the user's requests. Keep in mind all command output above 1024 characters in length will be truncated in the middle.'''},
    ]
    module_names = []
    for module in initialize_dynamics.modules:
        module_names.append(module)
    module_names.sort(key=lambda n: initialize_dynamics.modules[n]['properties']['priority'], reverse=True)
    print(module_names)
    for module in module_names:
        initialized_chat.extend(initialize_dynamics.modules[module]['properties']['prompt_data'])
    return initialized_chat


def enumerate_tokens_chat(lchat, lllm):
    return len(lllm.tokenize(bytes(parse_chat_to_string(lchat), 'utf-8')))


def truncate_middle(s, length, truncation_string='...'):
    if length >= len(s):
        return s

    left_len = (length - 3) // 2
    right_len = length - 3 - left_len

    truncated = s[:left_len] + truncation_string + s[-right_len:]
    return truncated


chat = initialize_chat()


output_text = ''

while True:
    while True:
        user_message = input("Input:")
        if user_message == "stop":
            sys.exit(1)
        elif user_message == 'new':
            chat = initialize_chat()
            break
        chat.append({'role': 'user', 'content': user_message})
        loop = 0
        loop_again = True
        while loop_again:
            loop += 1


            # prompt the model
            if gen_method == 'raw_model':
                print(f'Chat is currently {enumerate_tokens_chat(chat, llm)}/{n_ctx} tokens. Generating...')
                raw_output_text = raw_chat(chat, initialize_dynamics.ending_tokens)
            elif gen_method == 'lm_studio':
                print('Generating...')
                raw_output_text = lms_gen(chat, initialize_dynamics.ending_tokens)
            elif gen_method == 'openai':
                print('Generating...')
                raw_output_text = openai_gen(chat, initialize_dynamics.ending_tokens[:4]) # FIX


            # handle module/tool usage

            if any(c in raw_output_text for c in initialize_dynamics.starting_tokens):

                module_used = None
                for module_name in initialize_dynamics.modules:
                    if initialize_dynamics.modules[module_name]['properties']['is_tool']:
                        if initialize_dynamics.modules[module_name]['properties']['starting_token'] in raw_output_text:
                            module_used = module_name
                if not module_used:
                    raise Exception('Module usage was detected but specific module could not be detected')
                else:
                    #print(f'{module_used} usage detected:')
                    input(f'{module_used} usage detected, press enter to continue')

                output_text = raw_output_text+initialize_dynamics.modules[module_used]['properties']['ending_token']
                #print('\r'+output_text.split('\n')[-1])
                actual_command = zhmiscellany.string.multi_split(raw_output_text, [initialize_dynamics.modules[module_used]['properties']['starting_token']])[-1]
                #print(actual_command)
                #input('Press enter to continue')
                cmd_output = initialize_dynamics.modules[module_used]['module'].method(actual_command) # pipe failed cmd output to model, do not error out
                if not cmd_output:
                    cmd_output = '\n'
                cleaned_cmd_putput = zhmiscellany.string.multi_replace(cmd_output, [('\n\n', ''), ('  ', ''), ('\t', ''), ('--', ''), ('~~', '')])
                truncate_cmd_output_at = 2**10
                cleaned_cmd_putput = truncate_middle(cleaned_cmd_putput, truncate_cmd_output_at, '\n[cmd output truncated]\n')

                print(cleaned_cmd_putput)
                chat.append({'role': 'assistant', 'content': output_text})
                chat.append({'role': 'system', 'content': cleaned_cmd_putput})

                loop_again = True

            else:
                loop_again = False
                output_text = raw_output_text

                chat.append({'role': 'assistant', 'content': output_text})
