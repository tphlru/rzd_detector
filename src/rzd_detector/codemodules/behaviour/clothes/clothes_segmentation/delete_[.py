from glob import glob
from tqdm import tqdm
count0 = 0
count1 = 0
def delete(path):
    global count0, count1
    files = glob(path + "\\*.*")
    for file in tqdm(files):
        with open(file, 'r') as f:
            filedata = f.read()
            
        for x in filedata:
            if x[0] == '0':
                    count0 += 1
            elif x[0] == '1':
                count1 += 1

        filedata = filedata.replace('[', '')
        filedata = filedata.replace(']', '')

        with open(file, 'w') as file:
            file.write(filedata)

delete(r'C:\Users\Georges\Projects\datasets\DeepFashion2_YOLO\labels\train')
delete(r'C:\Users\Georges\Projects\datasets\DeepFashion2_YOLO\labels\test')
delete(r'C:\Users\Georges\Projects\datasets\DeepFashion2_YOLO\labels\validation')
print(f'Count of 0: {count0}\n count of 1: {count1}')