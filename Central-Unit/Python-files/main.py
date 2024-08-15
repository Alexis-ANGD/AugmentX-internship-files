import time
import threading
import datetime
from config import LedPinW, LedPinB, LedPinY, LedPinR, BuzzerPin, RecordingPin, RedLightsPin, DoorButtonPin, get_time_date, GPIO, buzzer_pwm
from interface import create_interface, sg
from pylsl import StreamInfo, StreamOutlet
import os

timers_list = []
timers_list2 = []
timers_lists = []
current_event = threading.Event()
paused_event = threading.Event()
timer_started = False
current_timer_index = 0  # Pour suivre l'index du timer en cours
timer_running = False  # Pour indiquer si le timer est en cours ou non
door_button_pressed = False  # Pour gérer l'état du bouton de la porte

# Fonction pour le timer
def countdown(remaining_time, event, paused_event, selected_outputs):
    global timer_running, current_timer_index, timer_started
    
    # Suivre le temps initial restant
    initial_remaining_time = remaining_time
    
    # Suivre le temps depuis le début pour permettre des ajustements
    start_time = time.monotonic()
    
    while remaining_time > 1:
        if not paused_event.is_set():
            elapsed_time = time.monotonic() - start_time  # Temps écoulé depuis le dernier calcul
            remaining_time = initial_remaining_time - elapsed_time  # Temps restant ajusté
            remaining_time = max(remaining_time, 0)  # Éviter les valeurs négatives

            formatted_time = str(datetime.timedelta(seconds=int(remaining_time)))
            window['-TIMER-'].update(f"{formatted_time}")

            if remaining_time <= 1:
                break
        else:
            # Mettre à jour le temps de départ si en pause
            start_time = time.monotonic()
            initial_remaining_time = remaining_time  # Conserver le temps restant
        time.sleep(0.1)

        if event.is_set():
            break

    if not event.is_set():
        # Activer les LEDs et le buzzer sélectionnés pendant 1 seconde
        on_time = time.monotonic()  # Temps de début d'allumage
        while time.monotonic() - on_time < 0.5:  # Garder les LEDs et le buzzer allumés pendant 1 seconde
            for output in selected_outputs:
                if output == BuzzerPin:
                    buzzer_pwm.ChangeDutyCycle(50)  # Activer le buzzer à 50% du cycle de travail
                else:
                    GPIO.output(output, GPIO.HIGH)
            time.sleep(0.1)
        
        # Éteindre les LEDs et le buzzer
        off_time = time.monotonic()  # Temps de début d'extinction
        while time.monotonic() - off_time < 0.3:  # Garder les LEDs et le buzzer éteints pendant 1 seconde
            for output in selected_outputs:
                if output == BuzzerPin:
                    buzzer_pwm.ChangeDutyCycle(0)  # Éteindre le buzzer
                else:
                    GPIO.output(output, GPIO.LOW)

        event.set()
        time.sleep(0.1)
        
def timer_thread():
    global timers_list, timer_started, current_timer_index
    while True:
        if timers_list and timer_started:
            remaining_time = timers_list[current_timer_index]
            selected_outputs = timers_list2[current_timer_index]  # LEDs et buzzer sélectionnés avec le timer
            countdown_thread = threading.Thread(target=countdown, args=(remaining_time, current_event, paused_event, selected_outputs))
            countdown_thread.start()
            countdown_thread.join()  # Attendre la fin du timer
            current_event.clear()
            timer_running = False  # Mettre à jour l'état du timer une fois terminé

            if timers_list:  # Assurez-vous que la liste n'est pas vide avant de calculer l'index
                current_timer_index = (current_timer_index + 1) % len(timers_list)  # Passer au timer suivant, et recommencer la liste si nécessaire
            else:
                current_timer_index = 0
        
# Fonction pour charger les timers depuis un fichier .txt
def load_timers_from_file(file_path):
    global timers_list, timers_list2, timers_lists
    with open(file_path, 'r') as f:
        lines = f.readlines()
    for line in lines[1:]:  # Skipping the header
        parts = line.strip().split('\t')
        hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
        remaining_time = hours * 3600 + minutes * 60 + seconds
        timers_list.append(remaining_time)
        selected_outputs = []
        if parts[3] == 'ON':
            selected_outputs.append(BuzzerPin)
        if parts[4] == 'ON':
            selected_outputs.append(LedPinW)
        if parts[5] == 'ON':
            selected_outputs.append(LedPinB)
        if parts[6] == 'ON':
            selected_outputs.append(LedPinY)
        if parts[7] == 'ON':
            selected_outputs.append(LedPinR)
        timers_list2.append(selected_outputs)
        formatted_timer = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        output_names = {
            BuzzerPin: 'BUZZER',
            LedPinW: 'LED W',
            LedPinB: 'LED B',
            LedPinY: 'LED Y',
            LedPinR: 'LED R'
        }
        timer_description = f"{formatted_timer} - {' / '.join([output_names[output] for output in selected_outputs])}"
        timers_lists.append(timer_description)
    window['-TIMER_LIST-'].update(values=timers_lists)

def save_timers_to_file(file_path):
    with open(file_path, 'w') as f:
        f.write("Hours\tMinutes\tSeconds\tBUZZER\tLED-W\tLED-B\tLED-Y\tLED-R\n")
        for i in range(len(timers_list)):
            hours = timers_list[i] // 3600
            minutes = (timers_list[i] % 3600) // 60
            seconds = timers_list[i] % 60
            buzzer = 'ON' if BuzzerPin in timers_list2[i] else 'OFF'
            led_w = 'ON' if LedPinW in timers_list2[i] else 'OFF'
            led_b = 'ON' if LedPinB in timers_list2[i] else 'OFF'
            led_y = 'ON' if LedPinY in timers_list2[i] else 'OFF'
            led_r = 'ON' if LedPinR in timers_list2[i] else 'OFF'
            f.write(f"{hours:02d}\t{minutes:02d}\t{seconds:02d}\t{buzzer}\t{led_w}\t{led_b}\t{led_y}\t{led_r}\n")

    # Renommer le fichier si nécessaire
    if file_path.endswith('save.txt'):
        directory = '/home/augmentix/Desktop/Central Unit V3'
        new_file_path = file_path.replace('save.txt', 'preset.txt')
        os.rename(file_path, new_file_path)
        # Mettre à jour les listes de fichiers
        txt_files = [f for f in os.listdir(directory) if f.endswith('preset.txt')]
        save_files = [f for f in os.listdir(directory) if f.endswith('save.txt')]
        window['-TXT_FILE-'].update(values=txt_files)
        window['-SAVE_FILE-'].update(values=save_files)

# Création de l'interface
window = create_interface()

# Fonction pour gérer le Door Button et les Red Lights
def door_button_thread():
    global door_button_pressed
    while True:
        if GPIO.input(DoorButtonPin) == GPIO.HIGH:
            press_start_time = time.time()
            while GPIO.input(DoorButtonPin) == GPIO.HIGH:
                if time.time() - press_start_time >= 0.1:
                    if not door_button_pressed:
                        door_button_pressed = True
                        GPIO.output(RedLightsPin, GPIO.HIGH)
                        window['-DOORLIGHTS-'].update(True)
                        window['-DOORLIGHTS_STATUS-'].update('ON', text_color='blue')
                    break
            while GPIO.input(DoorButtonPin) == GPIO.HIGH:
                time.sleep(0.1)
        else:
            time.sleep(0.1)

def lsl_thread():
    info = StreamInfo('Central_Unit', 'Flags', 8, 20, 'float32', 'rpi_gpio_stream')
    outlet = StreamOutlet(info)
    while True:
        data = [
            GPIO.input(RedLightsPin),
            GPIO.input(DoorButtonPin),
            GPIO.input(LedPinW),
            GPIO.input(LedPinB),
            GPIO.input(LedPinY),
            GPIO.input(LedPinR),
            GPIO.input(BuzzerPin),
            GPIO.input(RecordingPin)
        ]
        outlet.push_sample(data)
        time.sleep(0.1)

# Démarrage des threads
threading.Thread(target=timer_thread).start()
threading.Thread(target=door_button_thread).start()
threading.Thread(target=lsl_thread).start()

# Boucle principale
while True:
    event, values = window.read(timeout=500)
    heure, date = get_time_date()
    window['-TIME-'].update(f"{heure}")
    window['-DATE-'].update(f"{date}")

    # Mettre à jour le numéro du timer en cours en utilisant len(timers_list) pour le nombre total de timers
    window['-CURRENT_TIMER-'].update(f"Timer {current_timer_index + 1} / {len(timers_list)}")

    if event == 'OK':
        # Ajouter le timer à la liste des timers
        remaining_time = int(values['-HOURS-']) * 3600 + int(values['-MINUTES-']) * 60 + int(values['-SECONDS-'])
        formatted_time = str(datetime.timedelta(seconds=remaining_time))
        window['-TIMER-'].update(f"{formatted_time}")
        timers_list.append(remaining_time)
        
        # Enregistrer les LEDs et le buzzer sélectionnés avec le timer
        selected_outputs = []
        if values['-BUZZ-']:
            selected_outputs.append(BuzzerPin)
        if values['-LED1-']:
            selected_outputs.append(LedPinW)
        if values['-LED2-']:
            selected_outputs.append(LedPinB)
        if values['-LED3-']:
            selected_outputs.append(LedPinY)
        if values['-LED4-']:
            selected_outputs.append(LedPinR)
        timers_list2.append(selected_outputs)

        output_names = {
            BuzzerPin: 'BUZZER',
            LedPinW: 'LED W',
            LedPinB: 'LED B',
            LedPinY: 'LED Y',
            LedPinR: 'LED R'
        }
        formatted_timer = f"{int(values['-HOURS-']):02d}:{int(values['-MINUTES-']):02d}:{int(values['-SECONDS-']):02d}"
        timer_description = f"{formatted_timer} - {' / '.join([output_names[output] for output in selected_outputs])}"
        timers_lists.append(timer_description)
        window['-TIMER_LIST-'].update(values=timers_lists)

    if event == 'GO' and timers_list and not timer_running:  # Vérifier si le timer est déjà en cours
        # Démarrer le timer en cours (déterminé par l'index)
        timer_started = True
        timer_running = True
        paused_event.clear()
        if current_timer_index < len(timers_list):
            countdown_thread = threading.Thread(target=countdown, args=(timers_list[current_timer_index], current_event, paused_event, timers_list2[current_timer_index]))
            countdown_thread.start()

    if event == 'STOP' and timers_list :
        # Arrêter le timer en cours
        paused_event.set()
        current_event.set()  # Pour arrêter immédiatement le timer en cours
        timer_running = False  # Mettre à jour l'état du timer
        timer_started = False  # Ne pas redémarré le timer en fond

    if event == 'PLAY/PAUSE' and timers_list :
        # Mettre en pause ou reprendre le timer en cours
        if paused_event.is_set():
            paused_event.clear()
        else:
            paused_event.set()

    if event == 'LOAD FILE':  # Ajout de la fonctionnalité de chargement du fichier
        file_path = values['-TXT_FILE-']
        if file_path:
            load_timers_from_file(file_path[0])  # Prendre le premier élément de la liste
            
    if event == 'SAVE FILE' and timers_list:  # Vérifier si des timers sont présents
        file_path = values['-SAVE_FILE-']
        if file_path:
            save_timers_to_file(file_path[0])  # Prendre le premier élément de la liste

    if event == 'DELETE':
        # Supprimer le dernier timer de la liste
        if timers_list:
            if current_timer_index == len(timers_list) - 1:  # Vérifier si le timer en cours est le dernier de la liste
                paused_event.set()  # Arrêter le timer actuel
                current_event.set()  # Stopper immédiatement le timer en cours
            timers_list.pop()
            timers_list2.pop()
            timers_lists.pop()
            window['-TIMER_LIST-'].update(values=timers_lists)
            if not timers_list:  # Réinitialiser les états si la liste est vide
                timer_started = False
                timer_running = False
                current_timer_index = 0
                window['-TIMER-'].update('')
                window['-CURRENT_TIMER-'].update('')

    if event == 'RESET':
        # Arrêter tous les timers en cours
        paused_event.set()  # Arrêter le timer actuel
        current_event.set()  # Stopper immédiatement le timer en cours
    
        # Réinitialiser l'état des timers
        timer_started = False
        timer_running = False
    
        # Réinitialiser toutes les listes de timers
        timers_list = []
        timers_list2 = []
        timers_lists = []
        window['-TIMER_LIST-'].update(values=timers_lists)
        window['-TIMER-'].update('')
        window['-CURRENT_TIMER-'].update('')
        
        current_timer_index = 0

        # Ajouter une pause pour garantir que le thread principal a le temps de gérer les événements
        time.sleep(0.1)

    if event == sg.WIN_CLOSED or event == 'EXIT':
        break
    
    # Mettre à jour l'état de chaque LED dans l'interface
    for i in range(1, 5):
        led_key = f'-LED{i}-'
        status_key = f'-LED{i}_STATUS-'
        status_text = 'ON' if values[led_key] else 'OFF'
        status_color = 'blue' if status_text == 'ON' else 'red'  # Couleur bleue pour ON, rouge pour OFF
        window[status_key].update(status_text, text_color=status_color)

    # Mettre à jour l'état de l'option Buzzer dans l'interface
    buzzer_status_text = 'ON' if values['-BUZZ-'] else 'OFF'
    buzzer_status_color = 'blue' if buzzer_status_text == 'ON' else 'red'
    window['-BUZZ_STATUS-'].update(buzzer_status_text, text_color=buzzer_status_color)

    # Mettre à jour l'état de l'option Recording dans l'interface et le GPIO
    if values['-RECORDING-']:
        GPIO.output(RecordingPin, GPIO.HIGH)
        window['-RECORDING_STATUS-'].update('ON', text_color='blue')
    else:
        GPIO.output(RecordingPin, GPIO.LOW)
        window['-RECORDING_STATUS-'].update('OFF', text_color='red')

    # Mettre à jour l'état de l'option Door Lights dans l'interface et le GPIO
    if values['-DOORLIGHTS-']:
        if not door_button_pressed:
            door_button_pressed = True
            GPIO.output(RedLightsPin, GPIO.HIGH)
        window['-DOORLIGHTS_STATUS-'].update('ON', text_color='blue')
    else:
        GPIO.output(RedLightsPin, GPIO.LOW)
        door_button_pressed = False  # Permettre une nouvelle détection du bouton de la porte
        window['-DOORLIGHTS_STATUS-'].update('OFF', text_color='red')

    # Mettre à jour l'état de Mic dans l'interface
    if values['-MIC-']:
        window['-MIC_STATUS-'].update('ON', text_color='blue')
    else:
        window['-MIC_STATUS-'].update('OFF', text_color='red')
        
window.close()
