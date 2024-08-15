import PySimpleGUI as sg
import os

def create_interface():
    # Directory containing the preset timers files
    directory = '/home/augmentix/Desktop/Central Unit V3'
    
    # List available .txt files in the directory
    txt_files = [f for f in os.listdir(directory) if f.endswith('preset.txt')]
    save_files = [f for f in os.listdir(directory) if f.endswith('save.txt')]
    
    layout = [
        [
            # First column
            sg.Column([
                [sg.Text("", size=(10, 1), font=('Helvetica', 7))],
                [sg.Text("Configuration", size=(20, 1), font=('Helvetica', 30), justification='center')],
                [sg.Text("", size=(10, 1), font=('Helvetica', 16))],
                [sg.HorizontalSeparator()],
                [sg.Text("", size=(10, 1), font=('Helvetica', 12))],
                [sg.Text("Hours", size=(10, 1), font=('Helvetica', 16), justification='center')],
                [sg.Slider(range=(0, 24), default_value=0, orientation='h', size=(40, 30), key='-HOURS-')],
                [sg.Text("", size=(10, 1), font=('Helvetica', 5))],
                [sg.Text("Minutes", size=(10, 1), font=('Helvetica', 16), justification='center')],
                [sg.Slider(range=(0, 59), default_value=0, orientation='h', size=(40, 30), key='-MINUTES-')],
                [sg.Text("", size=(10, 1), font=('Helvetica', 5))],
                [sg.Text("Seconds", size=(10, 1), font=('Helvetica', 16), justification='center')],
                [sg.Slider(range=(0, 59), default_value=0, orientation='h', size=(40, 30), key='-SECONDS-')],
                [sg.Text("", size=(10, 1), font=('Helvetica', 20))],
                [sg.Frame(layout=[
                    [sg.Checkbox('BUZZER', key='-BUZZ-', font=('Helvetica', 14), text_color='white', size=(8, 1)), sg.Text('', key='-BUZZ_STATUS-', size=(5, 1), font=('Helvetica', 14))],
                    [sg.Checkbox('LED W', key='-LED1-', font=('Helvetica', 14), text_color='white', size=(8, 1)), sg.Text('', key='-LED1_STATUS-', size=(5, 1), font=('Helvetica', 14))],
                    [sg.Checkbox('LED B', key='-LED2-', font=('Helvetica', 14), text_color='white', size=(8, 1)), sg.Text('', key='-LED2_STATUS-', size=(5, 1), font=('Helvetica', 14))],
                    [sg.Checkbox('LED Y', key='-LED3-', font=('Helvetica', 14), text_color='white', size=(8, 1)), sg.Text('', key='-LED3_STATUS-', size=(5, 1), font=('Helvetica', 14))],
                    [sg.Checkbox('LED R', key='-LED4-', font=('Helvetica', 14), text_color='white', size=(8, 1)), sg.Text('', key='-LED4_STATUS-', size=(5, 1), font=('Helvetica', 14))]
                ], title='LEDs & Buzzer', font=('Helvetica', 20), relief=sg.RELIEF_SUNKEN)],
                [sg.Text("", size=(10, 1), font=('Helvetica', 20))],                
                [sg.Button('OK', size=(10, 2), pad=(20, 10)), sg.Button('DELETE', size=(10, 2), pad=(20, 10)), sg.Button('RESET', size=(10, 2), pad=(20, 10))],
                [sg.Text("", size=(10, 1), font=('Helvetica', 20))],
                [sg.HorizontalSeparator()],
                [sg.Text("", size=(10, 1), font=('Helvetica', 20))],
                [sg.Frame(layout=[
                    [sg.Checkbox('Recording', key='-RECORDING-', font=('Helvetica', 14), text_color='white', size=(10, 1)), sg.Text('', size=(5, 1), key='-RECORDING_STATUS-', font=('Helvetica', 14))],
                    [sg.Checkbox('Access Req.', key='-DOORLIGHTS-', font=('Helvetica', 14), text_color='white', size=(10, 1)), sg.Text('', size=(5, 1), key='-DOORLIGHTS_STATUS-', font=('Helvetica', 14))],
                    [sg.Checkbox('Mic', key='-MIC-', font=('Helvetica', 14), text_color='white', size=(10, 1)), sg.Text('', size=(5, 1), key='-MIC_STATUS-', font=('Helvetica', 14))]
                ], title='Other Options', font=('Helvetica', 20), relief=sg.RELIEF_SUNKEN)]
            ], element_justification='center'),
            sg.VerticalSeparator(),
            
            # Second column
            sg.Column([
                [sg.Image(filename='/home/augmentix/Downloads/Logo2000Px.png', key='-IMAGE-', subsample=5)],
                [sg.Text("", size=(20, 1), font=('Helvetica', 20))],
                [sg.HorizontalSeparator()],
                [sg.Text("", size=(20, 1), font=('Helvetica', 30))],
                [sg.Text("", size=(12, 1), font=('Helvetica', 100), justification='center', key='-TIME-')],
                [sg.Text("", size=(12, 1), font=('Helvetica', 100), justification='center', key='-DATE-')],
                [sg.Text("", size=(20, 1), font=('Helvetica', 30))],
                [sg.HorizontalSeparator()],
                [sg.Text("", size=(20, 1), font=('Helvetica', 30))],
                [sg.Text("", size=(12, 1), font=('Helvetica', 100), justification='center', key='-TIMER-')],
                [sg.Text("", size=(20, 1), font=('Helvetica', 15))],
                [sg.Text("", size=(16, 1), font=('Helvetica', 70), justification='center', key='-CURRENT_TIMER-')],
                [sg.Text("", size=(20, 1), font=('Helvetica', 20))],
                [sg.Button('GO', size=(20, 2)), sg.Button('STOP', size=(20, 2)), sg.Button('PLAY/PAUSE', size=(20, 2))],
                [sg.Text("", size=(20, 1), font=('Helvetica', 30))]
            ], element_justification='center'),
            sg.VerticalSeparator(),
            
            # Third column
            sg.Column([
                [sg.Text("", size=(10, 1), font=('Helvetica', 37))],
                [sg.Text("Timers List", size=(20, 1), font=('Helvetica', 30), justification='center')],
                [sg.Text("", size=(10, 1), font=('Helvetica', 16))],
                [sg.HorizontalSeparator()],
                [sg.Text("", size=(10, 1), font=('Helvetica', 11))],
                [sg.Listbox(values=[], size=(45, 8), key='-TIMER_LIST-', font=('Helvetica', 14), enable_events=True, auto_size_text=True)],
                [sg.Text("", size=(10, 1), font=('Helvetica', 11))],
                [sg.Text("Choose Preset Timers File", size=(25, 1), font=('Helvetica', 16), justification='center')],
                [sg.Text("", size=(10, 1), font=('Helvetica', 1))],
                [sg.Listbox(values=txt_files, size=(45, 6), key='-TXT_FILE-', font=('Helvetica', 14), enable_events=True)],
                [sg.Text("", size=(10, 1), font=('Helvetica', 5))],
                [sg.Button('LOAD FILE', size=(20, 2))],
                [sg.Text("", size=(10, 1), font=('Helvetica', 11))],
                [sg.Text("Save Timers in a File", size=(25, 1), font=('Helvetica', 16), justification='center')],
                [sg.Text("", size=(10, 1), font=('Helvetica', 1))],
                [sg.Listbox(values=save_files, size=(45, 6), key='-SAVE_FILE-', font=('Helvetica', 14), enable_events=True)],
                [sg.Text("", size=(10, 1), font=('Helvetica', 5))],
                [sg.Button('SAVE FILE', size=(20, 2))],
                [sg.Text("", size=(10, 1), font=('Helvetica', 11))],
                [sg.HorizontalSeparator()],
                [sg.Text("", size=(20, 1), font=('Helvetica', 30))],
                [sg.Button('EXIT', size=(10, 2), pad=(20, 10))],
                [sg.Text("", size=(20, 1), font=('Helvetica', 30))]
            ], element_justification='center')
        ]
    ]
    window = sg.Window("Minuteur", layout, finalize=True)
    window.Maximize()
    return window

