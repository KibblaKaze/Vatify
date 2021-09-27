import pandas as pd
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
import os

##### Get File Function #####
def get_file():
    global shopify_file
    shopify_file = filedialog.askopenfilename(
        title = 'Select Shopify Export',
        initialdir = str(Path.home() / "Downloads"),
        filetypes = (('CSV Files', '*.csv'),)
    )
    if shopify_file == '':
        return None
    
    #Update GUI
    main_label.configure(
        text = f'Your selected shopify file is:\n{shopify_file}\nPress the "Vatify" button to process it.'
    )
    button.configure(
        text = "Vatify",
        command = vatify
    )
    

#####  Take input file and Vatify it #####
def vatify():
    global vatify_df
    try:
        #Create Dataframe from File and Process
        shopify_df = pd.read_csv(shopify_file)

        #Filter out unnescesarry rows
        shopify_df = shopify_df.loc[shopify_df['Subtotal'].notna()]

        #Create new Dataframe to be exported
        vatify_df = pd.DataFrame()
        vatify_df['Invoice Number'] = shopify_df['Name']
        vatify_df['Transaction Date'] = pd.to_datetime(shopify_df['Paid at']).dt.strftime("%d/%m/%Y")
        vatify_df['Invoice Date'] = pd.to_datetime(shopify_df['Paid at']).dt.strftime("%d/%m/%Y")
        vatify_df['Currency'] = shopify_df['Currency']
        vatify_df['Transaction type'] = 'Sale'
        vatify_df['Country Dispatch'] = 'GB'
        vatify_df['Country Arrival'] = shopify_df['Shipping Country']
        vatify_df['Seller Name'] = 'Dice Throne Inc.'
        vatify_df['Seller VAT Number'] = 'IM2500009664'
        vatify_df['Customer VAT Number'] = shopify_df['Taxes'].apply(lambda x: 'PRIVATE INDIVIDUAL' if x != 0 else '')
        vatify_df['Customer Number'] = shopify_df['Taxes'].apply(lambda x: 'PRIVATE INDIVIDUAL' if x != 0 else '')
        vatify_df['Description'] = 'goods'
        vatify_df['Taxable Basis'] = shopify_df['Subtotal'] + shopify_df['Shipping']
        vatify_df['Value VAT'] = shopify_df['Tax 1 Value']
        vatify_df['Total'] = shopify_df['Total']
        vatify_df['VAT rate'] = shopify_df['Tax 1 Name'].str.extract(r'([0-9]+\%)')
        vatify_df['GTU Code'] = ''
        vatify_df['Document Code'] = ''
        vatify_df['Example index - please delete this column before submitting to Avalara'] = shopify_df['Taxes'].apply(lambda x: '' if x != 0 else 'Needs Review!')
        vatify_df = vatify_df.loc[vatify_df['Country Arrival'] != 'GB']
        vatify_df = vatify_df.loc[vatify_df['Taxable Basis'] > 180]
        mask = vatify_df['Value VAT'] != 0
        vatify_df.loc[mask, 'Transaction type'] = 'IOSS'
        vatify_df.fillna('', inplace=True)
        
        #Update GUI
        main_label.configure(
            text = f'{shopify_file} has been Vatified!\nPress the "Export" button to save it.'
        )
        button.configure(
            text = "Export",
            command = export_file
        )
    except Exception as e:
        main_label['text'] = f'The following error occured:\n{repr(e)}\nPlease ensure your selected file\n{shopify_file}\nis the correct shopify file and try again.'
        button['text'] = "Start"
        button['command'] = get_file

#####  Export VAT File #####
def export_file():
    file_label = filedialog.asksaveasfilename(
        initialdir = str(Path.home() / "Downloads"),
        defaultextension = '.csv',
        filetypes = (('CSV Files', '*.csv'),)
    )

    if export_file == '':
        return None

    vatify_df.to_csv(file_label, index = False)

    #Update GUI
    main_label['text'] = f'Your proccessed file has been successfully exported to:\n{file_label}\nPress the "Start" button to begin again.'
    button['text'] = "Start"
    button['command'] = get_file

##### Get absolute path to resource, works for dev and for PyInstaller #####
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

##### Main - GUI Stuff #####
root = tk.Tk()
logo = resource_path('favicon-32x32.png')
root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=logo))
root.title("Vatify")
root.config(bg='black')

frm_display = tk.Frame(
    master=root,
    width=100,
    height=50
)

main_label = tk.Label(
    master=frm_display,
    text='Welcome to Vatify.\nExport your desired shopify file in .csv format and press the "Start" button to select your shopify file and begin!',
    fg="green yellow",
    width=100,
    height=20,
    bg="black",
    font=('Arial',12)
)

frm_controls = tk.Frame(
    master=root,
    width=100,
    )

button = tk.Button(
    master=frm_controls,
    text="Start",
    bg="gray",
    fg="black",
    font=('Arial',12),
    command=get_file
)

frm_display.pack()
main_label.pack()
frm_controls.pack()
button.pack()

root.mainloop()

