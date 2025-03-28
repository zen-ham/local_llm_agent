import os, zhmiscellany


modules = {}
starting_tokens = []
ending_tokens = []

tools_folder = zhmiscellany.fileio.read_json_file('base_properties.json')['tools_folder']
lessons_folder = zhmiscellany.fileio.read_json_file('base_properties.json')['lessons_folder']
default_stop_token = zhmiscellany.fileio.read_json_file('base_properties.json')['default_stop_token']


def method(input_text):
    global modules, starting_tokens, ending_tokens

    do_print = False
    if input_text == 'do_print':
        do_print = True

    output_text = ''

    modules = {}
    # import tools
    for root, dirs, files in os.walk(os.path.join(os.getcwd(), tools_folder), topdown=True, onerror=None, followlinks=False):
        for f in files:
            if f.endswith('.py'):
                module_path = '\\'.join(os.path.join(root, f).split('\\')[-3:])
                properties_path = '\\'.join(module_path.split('\\')[:-1]+['properties.json'])
                module_name = module_path.split('\\')[1]
                dbs = '\\'
                out_data = f'Importing {dbs.join(module_path.split(dbs))}'
                if do_print:
                    print(out_data)
                else:
                    output_text += f'{out_data}\n'
                module = zhmiscellany.misc.import_module_from_path(module_path)
                properties = zhmiscellany.fileio.read_json_file(properties_path)
                modules[module_name] = {'module': module, 'properties': properties}
    # load lessons
    for root, dirs, files in os.walk(os.path.join(os.getcwd(), lessons_folder), topdown=True, onerror=None, followlinks=False):
        for f in files:
            if f.endswith('.json'):
                module_path = '\\'.join(os.path.join(root, f).split('\\')[-3:])
                properties_path = '\\'.join(module_path.split('\\')[:-1]+['properties.json'])
                module_name = module_path.split('\\')[1]
                dbs = '\\'
                out_data = f'Importing {dbs.join(module_path.split(dbs))}'
                if do_print:
                    print(out_data)
                else:
                    output_text += f'{out_data}\n'
                properties = zhmiscellany.fileio.read_json_file(properties_path)
                modules[module_name] = {'properties': properties}

    # set tokens
    ending_tokens = [default_stop_token]
    for i in modules.values():
        if i['properties']['is_tool']:
            ending_tokens.append(i['properties']['ending_token'])

    starting_tokens = []
    for i in modules.values():
        if i['properties']['is_tool']:
            starting_tokens.append(i['properties']['starting_token'])

    if not do_print:
        output_text += 'Initialized successfully'

    return output_text