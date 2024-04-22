import os

i = 1
path = 'c_img_v2'
name = 'dupa'

files = os.listdir(path)

# for file in files:
#     if file.startswith('image'):
#         new_name = path + '/' + name + '_' + str(i) + '.png'
#         os.rename(path + '/' + file, new_name)
#         i += 1


switch_center = 1
switch_edge = 20
switch_out = 46
switch_side = 67
delete_files = []
for file in files:
    if file.startswith(name) and '_p' not in file:
        last_underscore = file.rfind('_')
        last_dot = file.rfind('.')
        image_number = int(file[last_underscore + 1:last_dot])

        if image_number in delete_files:
            os.remove(path + '/' + file)
            os.remove(path + '/c_' + file)
            i += 1
            continue

        if image_number < switch_edge:
            new_name = path + '/' + file[:last_underscore] + '_' + 'pcenter' + file[last_underscore:]
            new_c_name = path + '/c_' + file[:last_underscore] + '_' + 'pcenter' + file[last_underscore:]
        elif image_number < switch_out:
            new_name = path + '/' + file[:last_underscore] + '_' + 'pedge' + file[last_underscore:]
            new_c_name = path + '/c_' + file[:last_underscore] + '_' + 'pedge' + file[last_underscore:]
        elif image_number < switch_side:
            new_name = path + '/' + file[:last_underscore] + '_' + 'pout' + file[last_underscore:]
            new_c_name = path + '/c_' + file[:last_underscore] + '_' + 'pout' + file[last_underscore:]
        else:
            new_name = path + '/' + file[:last_underscore] + '_' + 'pside' + file[last_underscore:]
            new_c_name = path + '/c_' + file[:last_underscore] + '_' + 'pside' + file[last_underscore:]
        os.rename(path + '/' + file, new_name)
        os.rename(path + '/c_' + file, new_c_name)
        i += 1

# for file in files:
#     new_file = file
#     # new_file = new_file[:-4]  #remove .png
#     last_underscore = new_file.rfind('_')
#     new_file = new_file[:last_underscore] + new_file[last_underscore + 1:]  # remove last underscore
#     pre_last_underscore = new_file.rfind('_')
#     new_file = new_file[:pre_last_underscore + 1] + new_file[last_underscore:]  #remove last word
#     os.rename(path + '/' + file, path + '/' + new_file)
