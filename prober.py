import tkinter as tk
from tkinter import filedialog
import glob
import re
import os
import zipfile
import shutil
import pandas as pd
from tqdm import tqdm

def main_1(start, end, device, search_str, folder_path):
    root = '//cpb-hjo02/backup/Driver/Prober_Log'

    # Main Directory
    months = os.listdir(root)
    if not os.path.exists(os.path.join('prober')):
        os.makedirs('prober')

    # List of Specified Months
    specified_months = months[months.index(start): months.index(end)+1]

    # Main Function
    print('Downloading files ...')
    for ym in specified_months:
        ym_path = os.path.join(root, ym)
        last_day = os.listdir(ym_path)[-1]
        d = os.path.join(ym_path, last_day)
        print(f'{ym}-{last_day}')

        if not os.path.exists(os.path.join('prober', f'{ym}-{last_day}')):
            os.makedirs(os.path.join('prober', f'{ym}-{last_day}'))
        
        files = [f for f in os.listdir(d) if re.search(f'^{device}', f)]
        for file in files:
            
            machine_name = file.split('.')[0]
            file_path = os.path.join(ym_path, last_day, file)
            # print(file_path)

            local_dir = os.path.join('prober', f'{ym}-{last_day}', machine_name) # 本地資料夾位置

            if not os.path.exists(local_dir):
                os.makedirs(local_dir)

            with zipfile.ZipFile(file_path,"r") as zip_ref: # 解壓縮
                zip_ref.extractall(local_dir)
    
    # 移動.dat到外層資料夾tmp
    if not os.path.exists(os.path.join('prober', 'tmp')):
        os.makedirs(os.path.join('prober', 'tmp'))

    dat = glob.glob(os.path.join('prober', '*', '*', '*.dat'))
    for d in dat:
        shutil.move(d, os.path.join('prober', 'tmp'))

    # 根據同一個機台合併成一個.csv file
    dat_paths = glob.glob(os.path.join('prober', 'tmp', '*.dat'))
    
    print('Searching ...')
    df = []

    for d in tqdm(dat_paths):
        with open(d) as f:
            try:
                for l in f.readlines():
                    if search_str.lower() in l.lower():
                        df.append([os.path.split(d)[-1].split('_')[-1].split('.')[0], l[:20].replace(',', ' '), l[20:-1]])
            except:
                pass
    pd.DataFrame(df, columns = ['Machine Name', 'Time', 'Code']).to_csv(os.path.join(folder_path, f'{device}.csv'), index=False)

    # Delete Unused files
    print('Deleting Unused files ...')
    shutil.rmtree('prober/tmp')
    del_files =  [f for f in os.listdir('prober') if f[-3:] != 'csv']
    for f in tqdm(del_files):
        shutil.rmtree(os.path.join('prober', f))

    print('Done.')


def convert_txt(src, tar):
    root = '//cpb-hjo02/backup/Driver/Prober_Log'
    with open(tar, 'w') as ff:
        with open(src, 'rb') as f:
            try:
                for l in f.readlines():
                    a = l.replace(b'\x00', b'0x0A')
                    ff.write(str(a).replace('0x0A', '\n'))
            except:
                pass


def main_2(start, end, device, search_str, folder_path):
    root = '//cpb-hjo02/backup/Driver/Prober_Log'
    # Main Directory
    months = os.listdir(root)
    if not os.path.exists(os.path.join('prober')):
        os.makedirs('prober')
        
    # List of Specified Months
    specified_months = months[months.index(start): months.index(end)+1]

    # Main Function
    print('Downloading files ...')
    for ym in specified_months:
        ym_path = os.path.join(root, ym)
        for date in os.listdir(ym_path):
            d = os.path.join(ym_path, date)
            print(f'{ym}-{date}')

            if not os.path.exists(os.path.join('prober', f'{ym}-{date}')):
                os.makedirs(os.path.join('prober', f'{ym}-{date}'))
            
            files = [f for f in os.listdir(d) if re.search(f'^{device}', f)]
            for file in files:
                
                machine_name = file.split('.')[0]
                file_path = os.path.join(ym_path, date, file)
                # print(file_path)

                local_dir = os.path.join('prober', f'{ym}-{date}', machine_name) # 本地資料夾位置

                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)

                with zipfile.ZipFile(file_path,"r") as zip_ref: # 解壓縮
                    zip_ref.extractall(local_dir)

    # 移動.dat到外層資料夾tmp
    if not os.path.exists(os.path.join('prober', 'tmp')):
        os.makedirs(os.path.join('prober', 'tmp'))

    # 轉檔成.txt格式
    print('Converting to text files ...')
    log = glob.glob(os.path.join('prober', '*', '*', '*.log'))
    for d in tqdm(log):
        file_name = os.path.split(d)[-1].split('.')[0]
        convert_txt(d, os.path.join('prober', 'tmp', f'{file_name}.txt'))

    txt_paths = glob.glob(os.path.join('prober', 'tmp', '*.txt'))

    print('Searching ...')
    df = []
    # 找關鍵字
    for d in tqdm(txt_paths):
        # print(d)
        machine_name = os.path.split(d)[-1].split('.')[0][15:-6]
        with open(d) as f:
            try:
                for l in f.readlines():
                    if search_str.lower() in l.lower():
                        df.append([machine_name, l[:14], l[19:23], l[24:-1]])
            except:
                pass

    pd.DataFrame(df, columns = ['Machine Name', 'Time', 'Code', 'Message']).to_csv(os.path.join(folder_path, f'{device}.csv'), index=False)

    # Delete Unused files
    print('Deleting Unused files ...')
    shutil.rmtree('prober/tmp')
    del_files =  [f for f in os.listdir('prober') if f[-3:] != 'csv']
    for f in tqdm(del_files):
        shutil.rmtree(os.path.join('prober', f))

    print('Done.')



if __name__ == "__main__":

    window = tk.Tk()
    window.title('Prober Log Tool')
    window.geometry('400x150')
    window.resizable(False, False)

    start_month_var = tk.StringVar()
    end_month_var = tk.StringVar()
    device_name = tk.StringVar()
    search_str_var = tk.StringVar()

    def submit_1():
        # First select a folder path to save the processed .csv file
        folder_path = filedialog.askdirectory()
        print(f'Save file to {folder_path}')
        start = start_month_var.get()
        end = end_month_var.get()
        device = device_name.get()
        search_str = search_str_var.get()
        main_1(start, end, device, search_str, folder_path)
    
    def submit_2():
        # First select a folder path to save the processed .csv file
        folder_path = filedialog.askdirectory()
        print(f'Save file to {folder_path}')
        start = start_month_var.get()
        end = end_month_var.get()
        device = device_name.get()
        search_str = search_str_var.get()
        main_2(start, end, device, search_str, folder_path)

    # creating a label for
    # name using widget Label
    start_label = tk.Label(window, text = 'Start Month (YYYY-MM)', font=('calibre',10, 'bold'))
    start_entry = tk.Entry(window,textvariable = start_month_var, font=('calibre',10,'normal'))
    end_label = tk.Label(window, text = 'End Month (YYYY-MM)', font = ('calibre',10,'bold'))
    end_entry=tk.Entry(window, textvariable = end_month_var, font = ('calibre',10,'normal'))
    device_label = tk.Label(window, text = 'Machine Name (EX: UF3000, UF3000-01)', font = ('calibre',10,'bold'))
    device_entry=tk.Entry(window, textvariable = device_name, font = ('calibre',10,'normal'))
    search_label = tk.Label(window, text = 'Search String/Code', font = ('calibre',10,'bold'))
    search_entry=tk.Entry(window, textvariable = search_str_var, font = ('calibre',10,'normal'))


    # creating a button using the widget
    # Button that will call the submit function
    dat_btn = tk.Button(window,text = 'Submit (.dat)', command = submit_1)
    log_btn = tk.Button(window,text = 'Submit (.log)', command = submit_2)
    # placing the label and entry in
    # the required position using grid
    # method
    start_label.grid(row=0,column=0)
    start_entry.grid(row=0,column=1)
    end_label.grid(row=1,column=0)
    end_entry.grid(row=1,column=1)
    device_label.grid(row=2,column=0)
    device_entry.grid(row=2,column=1)
    search_label.grid(row=3,column=0)
    search_entry.grid(row=3,column=1)
    dat_btn.grid(row=4,column=0)
    log_btn.grid(row=4,column=1)
    # performing an infinite loop
    # for the window to display
    window.mainloop()
        
