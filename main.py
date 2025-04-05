#Import librerie necessarie
import sys
import random
import json
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QCheckBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QDialog, QComboBox, QSpinBox, QHBoxLayout, QButtonGroup, QRadioButton
)

DEFAULT_FILE = "default_operations.json"

#Creazione classe oggetto operation
class Operation:
    """
    Classe operation: contiene tutti i parametri dell'oggetto Operation e le funzioni di get/set e lettura e scrittura dizionario
    per interpretazione file JSON
    """
    #Funzione inizializzazione parametri oggetto classe
    def __init__(self, nome, macchinario, tempo_min, tempo_max, capacity_max, randomRange = 0, materiali=[], prodotto=""):
        self.nome = nome
        self.macchinario = macchinario
        self.tempo_min = tempo_min
        self.tempo_max = tempo_max
        self.capacity_max = capacity_max
        self.materiali = materiali
        self.prodotto = prodotto
        self.randomRange = randomRange
        self.set_randomRange()

    #Funzione che setta il parametro randomRange facendo random tra tempo min e tempo max
    def set_randomRange(self):
        self.randomRange = random.randint(self.tempo_min, self.tempo_max)
        
    #Funzione che restituisce il randomRange
    def get_tempo_esecuzione(self):
        return self.randomRange
    
    #Funzione che restituisce la capacità massima dell'operazione
    def get_capacity_max(self):
        return (self.capacity_max)

    #Funzione di inserimento dati operazione in dizionario per passaggio a file json
    def to_dict(self):
        return {
            "nome": self.nome,
            "macchinario": self.macchinario,
            "tempo_min": self.tempo_min,
            "tempo_max": self.tempo_max,
            "capacity_max": self.capacity_max,
            "prodotto": self.prodotto
        }

    #Funzione per conversione dati da file json a dizionario utilizzando decorotara staticmethod per creare un'istanza rapida senza creazione oggetto
    @staticmethod
    def from_dict(data):
        return Operation(data["nome"], data["macchinario"], data["tempo_min"], data["tempo_max"], data["capacity_max"], prodotto=data["prodotto"])

#Creazione menù principale
class ProductionSimulator(QWidget):
    """
    Classe principale dell'applicazione che gestisce la simulazione del processo produttivo.
    Inizializza la finestra principale con il menù, carica operazioni predefinite e gestisce le quantità
    di prodotti.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulatore Produzione") #Titolo mostrato in finestra
        self.operations = {"Codolo ORFS 12-10": [], "Ghiera AD1-08": [], "Tubo raccordato": []} #Dizionario operazioni per prodotti
        self.quantities = {"Codolo ORFS 12-10": 0, "Ghiera AD1-08": 0, "Tubo raccordato": 0} #Dizionario quantità per prodotti
        self.load_defaults() #Funzione di caricamento operazioni da file JSON
        self.initUI() #Funzione di inizializzazione elementi grafici

    def initUI(self):
        #Definizione layout base
        layout = QVBoxLayout()

        #Creazione pulsanti interfaccia
        self.start_simulation_btn = QPushButton("Nuova Simulazione")
        self.archive_btn = QPushButton("Archivio Simulazioni")
        self.settings_btn = QPushButton("Impostazioni")
        self.warehouse_btn = QPushButton("Magazzino")
        
        #Aggiunta pulsanti al layout
        layout.addWidget(self.start_simulation_btn)
        layout.addWidget(self.archive_btn)
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.warehouse_btn)

        #Cristallizzazione layout
        self.setLayout(layout)
        
        #Collegamento pulsanti a funzioni
        self.start_simulation_btn.clicked.connect(self.new_simulation) #pulsante nuova simulazione collegato a funzione new_simulation
        self.archive_btn.clicked.connect(lambda: QMessageBox.information(self, "Info", "Sviluppo in corso")) #pulsante archivio simulazioni collegato a funzione lambda che mostra un messaggio di sviluppo in corso
        self.settings_btn.clicked.connect(lambda: QMessageBox.information(self, "Info", "Sviluppo in corso")) #pulsante impostazioni collegato a funzione lambda che mostra un messaggio di sviluppo in corso
        self.warehouse_btn.clicked.connect(lambda: QMessageBox.information(self, "Magazzino", "Macchinari e Materiali")) #pulsante magazzino collegato a funzione lambda che mostra un messaggio di sviluppo in corso

    #Funzione che apre in una nuova finestra la nuova simulazione
    def new_simulation(self):
        self.sim_window = SimulationWindow(self)
        self.sim_window.show()

    #Funzione di caricamento dati dal file JSON caricato ad inizio programma per non appesantire l'apertura della nuova finestra
    def load_defaults(self):
        try: #Operazione inserita in blocco try except per evitare eccezioni da eventuale inesistenza file
            with open(DEFAULT_FILE, "r") as file:
                data = json.load(file) #Caricamento file JSON in variabile data
                #For innestato di scorrimento del file JSON
                for prodotto, ops in data.items():
                    self.operations[prodotto] = [Operation.from_dict(op) for op in ops]
        except FileNotFoundError:
            pass
    
    #Funzione di salvataggio su file json (utilizzata nella classe addoperationdialog)
    def save_defaults(self):
        data = {prodotto: [op.to_dict() for op in ops] for prodotto, ops in self.operations.items()}
        with open(DEFAULT_FILE, "w") as file:
            json.dump(data, file, indent = 4)

#Creazione finestra "nuova simulazione"
class SimulationWindow(QWidget):
    """
    Finestra nuova simulazione.
    Consente all'utente di definire le quantità da produrre, visualizzare le operazioni attive in tabella,
    aggiungere nuove operazioni e avviare il calcolo dei tempi totali di produzione.
    """
    def __init__(self, parent): #Inizializzazione parametri
        super().__init__()
        self.parent = parent #Riferimento alla finestra principale, consente la lettura del file JSON e l'utilizzo delle funzionalità 
        self.setWindowTitle("Nuova Simulazione") #titolo mostrato in finestra
        self.initUI() #Inizializzazione elementi grafici
        self.update_table() #Funzione che aggiorna la tabella delle operazioni da file JSON precedentemente caricato

    def initUI(self):
        #definizione layout principale
        layout = QVBoxLayout()
        
        #creazione primi 3 caampi editabili sulle quantità di prodotti da produrre ed aggiunta al layout, creati con for per possibili future espansioni
        self.quantity_labels = {}
        for prodotto in ["Codolo ORFS 12-10", "Ghiera AD1-08", "Tubo raccordato"]:
            hbox = QHBoxLayout()
            label = QLabel(prodotto)
            input_field = QLineEdit()
            self.quantity_labels[prodotto] = input_field
            hbox.addWidget(label)
            hbox.addWidget(input_field)
            layout.addLayout(hbox)

        #creazione pulsanti
        self.generate_params_btn = QPushButton("Genera Quantità Casuali")
        self.add_op_btn = QPushButton("Aggiungi Operazione")
        self.calculate_total_btn = QPushButton("Calcola Tempo Totale")
        
        #creazione tabella operazioni con intestazione
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Codolo ORFS 12-10", "Ghiera AD1-08", "Tubo raccordato"])
        
        #Creazione delle label titolo e legenda della tabella
        self.label_operation = QLabel("LISTA OPERAZIONI:")
        self.label_legend = QLabel("Operazione: Nome, Macchinario, Capacità massima, Range temporale, Tempo Random in range")
        
        #Aggiunta in ordine dei pulsanti, label e tabella al layout
        layout.addWidget(self.generate_params_btn)
        layout.addWidget(self.add_op_btn)
        layout.addWidget(self.label_operation)
        layout.addWidget(self.table)
        layout.addWidget(self.label_legend)
        layout.addWidget(self.calculate_total_btn)
        
        #Cristallizzazione layout
        self.setLayout(layout)

        #Collegamento pulsanti a funzioni
        self.generate_params_btn.clicked.connect(self.generate_random_quantities)
        self.add_op_btn.clicked.connect(self.add_operation)
        self.calculate_total_btn.clicked.connect(self.calculate_total_time)
    
    #funzione che genera le quantità random per i lotti da produrre
    def generate_random_quantities(self):
        #For di compilazione dizionario parent.quantities dichiarato in finestra principale
        for prodotto in self.parent.quantities.keys():
            value = random.randint(300, 500) #Range random impostato tra 300 e 500
            self.parent.quantities[prodotto] = value #Settaggio valore in dizionario
            self.quantity_labels[prodotto].setText(str(value)) #Settaggio valore in campo editabile

    #Apertura finestra di inserimento nuova operazione
    def add_operation(self):
        dialog = AddOperationDialog(self) 
        if dialog.exec(): #Attende la conferma (premendo il pulsante "Conferma")
            operation, save_default = dialog.get_operation() #Legge i dati inseriti dall'utente
            self.parent.operations[operation.prodotto].append(operation) #Inserisce l'operazione appena creata al prodotto corrispondente
            if save_default: #Se la checkbox "Salva come default" è stata selezionata aggiunge l'operazione al JSON
                self.parent.save_defaults()
            self.update_table() #Fa l'update della tabella per mostrare la nuova operazione appena generata
            
    #Funzione che esegue il calcolo finale secondo la formula: sommatoria (tempo operazione * intero successivo(quantità/capacità))
    def calculate_total_time(self):
        message = "Tempi totali per prodotto (quantità incluse):\n" #Prima parte messaggeBox
        for prodotto in ["Codolo ORFS 12-10", "Ghiera AD1-08", "Tubo raccordato"]: #For scorrimento prodotti
            total_time = 0
            try: #Blocco try except che previene crash per mancato inserimento parametri
                #For innestato che per ogni prodotto scorre tutte le operazioni
                for op in self.parent.operations[prodotto]:
                    op.set_randomRange() #Funzione che genera per ogni operazione un nuovo random compreso nel range dei tempi
                    total_time += op.get_tempo_esecuzione() * math.ceil(int(self.quantity_labels[prodotto].text())/int(op.get_capacity_max())) #Formula
            except: #In caso di fallimento della formula genara un Alert e chiude l'esecuzione della funzione
                QMessageBox.information(self, "Alert quantità non inserite", "ATTENZIONE: quantità non inserite correttamente")
                return
            
            #Ritrasformazione del tempo in secondi in formato HH:MM:SS
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            seconds = total_time % 60
            #Composizione messaggio di output con sommatoria f-string
            message += f"{prodotto}: {hours}h {minutes}m {seconds}s ({self.quantity_labels[prodotto].text()} pz)\n"
            self.update_table() #Update della tabella per showing nelle operazioni dei valori randomici utilizzati per la simulazione
        QMessageBox.information(self, "Tempo Totale Produzione", message) #Finestra di dialogo con messaggio finale completo

    #Funzione che va ad aggiornare la tabella con tutte le operazioni disponibili a runtime (comprese quelle del file JSON per escluderle bisogna eliminare il JSON)
    def update_table(self):
        self.table.setRowCount(max(len(self.parent.operations[p]) for p in ["Codolo ORFS 12-10", "Ghiera AD1-08", "Tubo raccordato"])) #Settaggio numero massimo colonne e righe
        #For innestato che itera per colonne e righe associando ad ogni prodotto tutte le operazioni disponibili
        for col, prodotto in enumerate(["Codolo ORFS 12-10", "Ghiera AD1-08", "Tubo raccordato"]):
            for row, operation in enumerate(self.parent.operations[prodotto]):
                item = QTableWidgetItem(f"{operation.nome}, {operation.macchinario}, {operation.capacity_max}, ({operation.tempo_min}s - {operation.tempo_max}s), {operation.get_tempo_esecuzione()}s") #Definisce la stringa descrittiva dell'operazione composta da: nome, macchinario, capacità massima, range temporale, tempo random generato
                self.table.setItem(row, col, item) #Aggiunge effettivamente l'item alla tabella
        #Resize automatico righe e colonne in base al contenuto
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()


class AddOperationDialog(QDialog):
    """
    Finestra di creazione dell'operazione. Consente di settare il prodotto per il quale si vuole aggiungere l'operazione,
    nome operazione, capacità massima, macchinario tempo di esecuzione sia in range che determinato.
    """
    def __init__(self, parent):
        super().__init__(parent) #Collegamento a finestra precedente
        self.setWindowTitle("Aggiungi Operazione") #Titolo della finestra
        self.initUI() #Inizializzazione grafica

    def initUI(self):
        #Creazione layout verticale di base
        layout = QVBoxLayout()

        #Creazione elementi grafici per inserimento dati
        self.prodotto_select = QComboBox()
        self.nome_operazione = QLineEdit()
        self.cap_max = QLineEdit()
        self.macchinario_select = QComboBox()
        self.tempo_tipo_group = QButtonGroup(self)
        self.radio_determinato = QRadioButton("Tempo Determinato")
        self.radio_range = QRadioButton("Range")
        self.time_widget_min = QWidget()
        self.time_widget_max = QWidget()
        self.save_default = QCheckBox("Salva come Default")
        self.confirm_btn = QPushButton("Conferma")
        
        #Funzionalità di base pulsanti
        self.prodotto_select.addItems(["Codolo ORFS 12-10", "Ghiera AD1-08", "Tubo raccordato"]) #Aggiunge alla ComboBox la lista di prodotti
        self.macchinario_select.addItems(["Pressa", "Taglierina", "Multimandrino Schutte", "Manuale", "Lavatrice", "Forno", "Nastro trasportatore", "Banco prova 400ATM"]) #Aggiunge alla ComboBox la lista dei macchinari
        self.radio_determinato.setChecked(True) #Imposta il tasto Tempo determinato checkato di default
        self.tempo_tipo_group.addButton(self.radio_determinato) #Aggiunge pulsante tempo determinato al gruppo time group
        self.tempo_tipo_group.addButton(self.radio_range) #Aggiunge pulsante Range al gruppo time group
        
        #Utilizza la funzione create_time_input() per generare le caselle di input per gg, hh, mm, ss
        self.time_layout_min = self.create_time_input("Tempo Minimo") 
        self.time_layout_max = self.create_time_input("Tempo Massimo")
        
        #Aggiunta elementi grafici ai layout
        layout.addWidget(QLabel("Seleziona Prodotto"))
        layout.addWidget(self.prodotto_select)
        layout.addWidget(QLabel("Nome Operazione"))
        layout.addWidget(self.nome_operazione)
        layout.addWidget(QLabel("Capacità massima"))
        layout.addWidget(self.cap_max)
        layout.addWidget(QLabel("Seleziona Macchinario"))
        layout.addWidget(self.macchinario_select)
        tempo_layout = QHBoxLayout() #Creazione layout orizzontale da innestare in layout verticale base per inserimento tempi in formato GG:HH:MM:SS
        tempo_layout.addWidget(self.radio_determinato)
        tempo_layout.addWidget(self.radio_range)
        layout.addLayout(tempo_layout)
        self.time_widget_min.setLayout(self.time_layout_min)
        self.time_widget_max.setLayout(self.time_layout_max)
        self.time_widget_max.hide() #Essendo checkato di default il pulsante tempo determinato la parte tempo massimo viene nascosta 
        layout.addWidget(self.time_widget_min)
        layout.addWidget(self.time_widget_max)
        layout.addWidget(self.save_default)
        layout.addWidget(self.confirm_btn)
        
        #Cristallizzazione layout
        self.setLayout(layout)
        
        #Collegamento pulsanti a funzioni
        self.radio_determinato.toggled.connect(self.toggle_range)
        self.confirm_btn.clicked.connect(self.accept)
       
    #Funzione che crea il layout di inserimento tempi esecuzione
    def create_time_input(self, label_text):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        for label in ["gg", "hh", "mm", "ss"]:
            spin = QSpinBox() #Crea una casella di selezione numerica per ogni unità di tempo
            if label == "gg":
                spin.setRange(0, 365) #Setta il range di GG a 0 - 365
            elif label == "hh": 
                spin.setRange(0, 23) #Setta il range di hh a 0 - 23
            else:
                spin.setRange(0, 59) #Setta il range di mm e ss a 0 - 59
                
            setattr(self, f"{label_text}_{label}", spin) #Crea un attributo dinamico nell'oggetto per memorizzare ogni QSpinBox
            
            #Aggiunge quanto creato al layout
            layout.addWidget(spin)
            layout.addWidget(QLabel(label))
            
        return layout #Restituisce il layout completo

    #Funzione per nascondere e mostrare la riga tempo massimo in base al tasto Tempo determinato/range selezionato 
    def toggle_range(self):
        if self.radio_range.isChecked():
            self.time_widget_max.show()
        else:
            self.time_widget_max.hide()

    #Funzione che trasforma il tempo inserito in formato GG:HH:MM:SS in secondi
    def get_seconds(self, prefix):
        days = getattr(self, f"{prefix}_gg").value()
        hours = getattr(self, f"{prefix}_hh").value()
        minutes = getattr(self, f"{prefix}_mm").value()
        seconds = getattr(self, f"{prefix}_ss").value()
        return days*86400 + hours*3600 + minutes*60 + seconds

    #Funzione per il recupero delle informazioni inserite in input
    def get_operation(self):
        if self.radio_determinato.isChecked(): #Se tempo determinato tempo min e tempo max sono uguali
            tempo_min = tempo_max = self.get_seconds("Tempo Minimo")
        else: #Altrimenti setta entrambi per quanto inserito in input
            tempo_min = self.get_seconds("Tempo Minimo")
            tempo_max = self.get_seconds("Tempo Massimo")
            
        #Return di tutti i campi compilati
        return Operation(
            self.nome_operazione.text(), self.macchinario_select.currentText(),
            tempo_min = tempo_min, tempo_max = tempo_max, capacity_max = self.cap_max.text(),
            prodotto = self.prodotto_select.currentText()
        ), self.save_default.isChecked()

#Esecuzione Main
if __name__ == "__main__":
    app = QApplication(sys.argv) #Crea un'istanza dell'applicazione Qt, passando gli argomenti della riga di comando
    mainWin = ProductionSimulator() #Crea l'istanza principale della finestra dell'applicazione
    mainWin.show() #Mostra la finestra principale
    sys.exit(app.exec()) #Avvia il ciclo di eventi dell'applicazione e termina correttamente al termine