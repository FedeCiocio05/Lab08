from database.impianto_DAO import ImpiantoDAO


'''
from model.impianto_DTO import Impianto
'''
'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        risultati = []

        for impianto in self._impianti:
            count = 0
            somma = 0

            for consumo in impianto.get_consumi():
                #data = datetime.strptime(consumo.data, "%Y-%m-%d")
                if consumo.data.month == mese:
                    somma = somma + consumo.kwh
                    count +=1

            media = somma / count
            risultati.append((impianto.nome, media))
        return risultati

        # TODO

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        """
                Implementa la ricorsione per trovare la sequenza ottimale.

                :param sequenza_parziale: lista degli ID impianto visitati finora (es. [1, 1, 2])
                :param giorno: il giorno corrente che stiamo pianificando (da 1 a 7)
                :param ultimo_impianto: ID dell'impianto visitato il giorno prima (serve per costo spostamento)
                :param costo_corrente: costo accumulato fino al giorno precedente
                :param consumi_settimana: dizionario {id_impianto: [consumi_7_giorni]}
                """

        # 🟤 E - PRUNING (Filtro C anticipato per efficienza)
        # Se il costo parziale è GIA' peggiore del miglior costo totale trovato,
        # è inutile continuare su questo "ramo" della ricorsione.
        # Questo è un filtro di ottimizzazione (Branch & Bound).
        if self.__costo_ottimo != -1 and costo_corrente >= self.__costo_ottimo:
            return

        # 🟢 A - CONDIZIONE TERMINALE (Caso Base)
        # Abbiamo pianificato tutti i 7 giorni (stiamo per iniziare il giorno 8)
        if giorno == 8:
            # Abbiamo trovato una sequenza completa.
            # Controlliamo se è migliore di quella ottima trovata finora.
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                # Salvo una COPIA della soluzione, altrimenti il .pop()
                # successivo la svuoterebbe. Errore tipico da esame!
                self.__sequenza_ottima = list(sequenza_parziale)
            return  # Termina questo ramo

        # 🔵 B - CICLO RICORSIVO (Passo Ricorsivo)
        # Per il 'giorno' corrente, provo a visitare entrambi gli impianti
        for impianto in self._impianti:
            id_impianto_scelto = impianto.id

            # CONTROLLO E CALCOLO SUGLI SPOSTAMENTI
            # 1. Calcola il costo di questa scelta
            costo_spostamento = 0
            # Se non è il primo giorno e cambio impianto rispetto a ieri
            if ultimo_impianto is not None and id_impianto_scelto != ultimo_impianto:
                costo_spostamento = 5  # Costo fisso di spostamento

            # 'giorno' è 1-based, l'indice della lista è 0-based
            giorno_index = giorno - 1
            costo_consumo = consumi_settimana[id_impianto_scelto][giorno_index]
            #print(costo_consumo, id_impianto_scelto, giorno_index)

            nuovo_costo = costo_corrente + costo_spostamento + costo_consumo

            # 2. "DO" - Aggiungo la scelta alla soluzione parziale
            sequenza_parziale.append(id_impianto_scelto)

            # 3. "RECURSE" - Chiamo la ricorsione per il giorno successivo
            self.__ricorsione(sequenza_parziale,
                              giorno + 1,  # Passo al giorno successivo
                              id_impianto_scelto,  # Questo è il "nuovo" ultimo impianto
                              nuovo_costo,
                              consumi_settimana)

            # 🟣 D - "UNDO" (Backtracking)
            # Finito questo ramo, rimuovo la mia scelta per permettere
            # al ciclo 'for' di provare l'ALTRO impianto per lo STESSO giorno.
            sequenza_parziale.pop()

        # TODO

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        consumi = {}

        for impianto in self._impianti:
            giorni = [0] * 7
            for consumo in impianto.get_consumi():
                if consumo.data.month == mese and 1 <= consumo.data.day <= 7:
                    i = consumo.data.day - 1
                    giorni[i] = consumo.kwh

            consumi[impianto.id] = giorni

        #print("\nVOCABOLARIO COMPLETO:", consumi)
        return consumi

        # TODO

