import os
import sys
import time
import random
import argparse
import traceback
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def simula_movimento_mouse(driver, elemento):
    """Simula movimento naturale del mouse verso un elemento"""
    actions = ActionChains(driver)
    actions.move_to_element(elemento)
    actions.pause(random.uniform(0.3, 0.7))  # Pausa naturale
    actions.perform()
    
def simula_click_umano(elemento):
    """Simula un click umano con pausa prima e dopo"""
    time.sleep(random.uniform(0.1, 0.3))  # Pausa prima del click
    elemento.click()
    time.sleep(random.uniform(0.2, 0.5))  # Pausa dopo il click

def scorri_lentamente(driver, direzione="giu", pixel=None):
    """Scorri lentamente come farebbe un utente reale"""
    if pixel is None:
        pixel = random.randint(300, 500)  # Scrolling casuale
    
    if direzione == "giu":
        driver.execute_script(f"window.scrollBy(0, {pixel});")
    elif direzione == "su":
        driver.execute_script(f"window.scrollBy(0, -{pixel});")
    elif direzione == "inizio":
        driver.execute_script("window.scrollTo(0, 0);")
    
    time.sleep(random.uniform(0.8, 1.5))  # Pausa naturale dopo lo scorrimento

def collect_posts_by_indices(driver, profile_username, output_file, start_idx=1, end_idx=None, debug=False):
    """
    Raccoglie post Instagram in base al loro indice.
    - start_idx: indice del primo post da raccogliere (1-based)
    - end_idx: indice dell'ultimo post da raccogliere (1-based), None per tutti i post dopo start_idx
    """
    # Naviga al profilo
    profile_url = f"https://www.instagram.com/{profile_username}/"
    print(f"\n🌐 Accesso al profilo: {profile_url}")
    driver.get(profile_url)
    time.sleep(random.uniform(3, 5))  # Attesa per caricamento
    
    # Verifica se il profilo esiste
    if "Page Not Found" in driver.title or "Pagina non trovata" in driver.title:
        print(f"⛔ Errore: il profilo {profile_username} non esiste.")
        return []
    
    # Inizializza la raccolta di URL
    collected_urls = []
    
    # Crea/reinizializza il file di output
    with open(output_file, 'w') as f:
        f.write(f"# URL dei post Instagram di {profile_username} (post da {start_idx}")
        if end_idx:
            f.write(f" a {end_idx}")
        f.write(")\n")
    
    # Torna all'inizio della pagina
    print("\n⬆️ Torno all'inizio della pagina...")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(random.uniform(2, 3))
    
    # Contatori e limiti
    current_idx = 0  # Indice corrente dei post (0-based per calcoli interni)
    post_count = 0   # Numero di post raccolti
    scroll_count = 0 # Contatore di scrolling
    max_scrolls = 200  # Limite di sicurezza
    processed_elements = []  # Traccia gli elementi già processati
    
    print(f"\n🚀 Inizio conteggio e raccolta dei post (da {start_idx}")
    if end_idx:
        print(f" a {end_idx})...")
    else:
        print(" fino alla fine)...")
    
    try:
        while ((end_idx is None or current_idx < end_idx) and scroll_count < max_scrolls):
            # Stampa il progresso
            print(f"\n📊 STATO: Indice attuale {current_idx+1}, {post_count} post raccolti, {scroll_count} scrolling eseguiti")
            
            # Trova tutti gli elementi _aagw visibili
            print("🔎 Cerco i post con classe '_aagw'...")
            post_elements = driver.find_elements(By.CLASS_NAME, "_aagw")
            
            # Se non troviamo elementi con quella classe specifica, prova alternative
            if not post_elements or len(post_elements) == 0:
                print("⚠️ Classe '_aagw' non trovata, provo selettori alternativi...")
                
                # Alternativa 1: div con ruolo button in articoli
                post_elements = driver.find_elements(By.XPATH, "//article//div[@role='button']")
                
                # Alternativa 2: link che contengono /p/ o /reel/
                if not post_elements or len(post_elements) == 0:
                    post_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/') or contains(@href, '/reel/')]")
                
                # Alternativa 3: div cliccabili con immagini
                if not post_elements or len(post_elements) == 0:
                    post_elements = driver.find_elements(By.XPATH, "//div[@role='button']//img/ancestor::div[@role='button']")
            
            # Stampa il numero di elementi trovati
            print(f"📌 Trovati {len(post_elements)} elementi post nella vista corrente")
            
            # Se non ci sono elementi, scorri e continua
            if not post_elements or len(post_elements) == 0:
                print("⬇️ Nessun post visibile, scorro la pagina...")
                scorri_lentamente(driver, "giu")
                scroll_count += 1
                time.sleep(random.uniform(1, 2))
                continue
            
            # Filtra gli elementi che non sono stati ancora processati
            new_elements = []
            for el in post_elements:
                # Genera un identificatore basato su posizione e attributi
                try:
                    el_id = f"{el.location}_{el.size}_{el.get_attribute('class')}"
                    if el_id not in processed_elements:
                        new_elements.append((el, el_id))
                except:
                    # Se non riusciamo a generare un ID, trattiamolo come nuovo
                    new_elements.append((el, None))
            
            # Se non ci sono nuovi elementi, scorriamo per trovarne altri
            if not new_elements:
                print("\n⬇️ Nessun nuovo post trovato, scorro la pagina...")
                scorri_lentamente(driver, "giu")
                scroll_count += 1
                time.sleep(random.uniform(1, 2))
                continue
            
            # Processa i nuovi elementi - prima solo per contarli
            print(f"✨ Trovati {len(new_elements)} nuovi post da processare")
            
            for i, (post_el, el_id) in enumerate(new_elements):
                current_idx += 1  # Incrementa l'indice corrente
                
                # Aggiungi l'elemento all'elenco di quelli processati
                if el_id:
                    processed_elements.append(el_id)
                
                # Verifica se questo post rientra nel range richiesto
                if current_idx < start_idx:
                    # Questo post è prima dell'indice di inizio, lo saltiamo
                    print(f"⏭️ Salto il post #{current_idx} (< {start_idx})")
                    continue
                
                if end_idx is not None and current_idx > end_idx:
                    # Abbiamo superato l'indice finale, usciamo dal ciclo
                    print(f"🏁 Raggiunto il post #{current_idx} (> {end_idx}), termino raccolta")
                    break
                
                # Questo post rientra nel range richiesto, procediamo con la raccolta
                
                # Calcola l'indice per il feedback
                idx = current_idx
                target = "∞" if end_idx is None else end_idx
                
                # Scorri l'elemento al centro della vista per un click preciso
                print(f"\n🔍 [#{idx}/{target}] Posizionamento post al centro dello schermo...")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", post_el)
                time.sleep(random.uniform(0.8, 1.2))
                
                # Evidenzia l'elemento per debug visivo
                if debug:
                    driver.execute_script("arguments[0].style.border='3px solid red'", post_el)
                    time.sleep(0.5)
                
                # Clicca sull'elemento per aprire il post
                print(f"👆 [#{idx}/{target}] Clic sul post...")
                try:
                    # Prova con un clic standard prima
                    simula_movimento_mouse(driver, post_el)
                    simula_click_umano(post_el)
                except Exception as click_error:
                    if debug:
                        print(f"Errore durante il clic standard: {click_error}")
                    
                    # Se fallisce, prova con JavaScript (più potente)
                    print(f"⚠️ [#{idx}/{target}] Clic standard fallito, provo con JavaScript...")
                    driver.execute_script("arguments[0].click();", post_el)
                
                # Attendi che il post si carichi
                load_time = random.uniform(2.0, 3.0)
                print(f"⏳ [#{idx}/{target}] Attendo caricamento del post ({load_time:.1f} sec)...")
                time.sleep(load_time)
                
                # Verifica che siamo effettivamente in un post
                post_url = driver.current_url
                if '/p/' in post_url or '/reel/' in post_url or '/tv/' in post_url:
                    print(f"✅ [#{idx}/{target}] Post caricato correttamente: {post_url}")
                    
                    # Salva sempre l'URL della barra degli indirizzi come prima opzione
                    clean_url = post_url.split('?')[0]
                    print(f"📝 [#{idx}/{target}] Salvo URL dalla barra degli indirizzi: {clean_url}")
                    
                    # Salva l'URL
                    if clean_url not in collected_urls:
                        collected_urls.append(clean_url)
                        with open(output_file, 'a') as f:
                            f.write(f"{clean_url}\n")
                        print(f"✅ [#{idx}/{target}] URL salvato: {clean_url}")
                        post_count += 1
                    else:
                        print(f"⚠️ [#{idx}/{target}] URL già salvato, salto...")
                    
                    # Opzionalmente, proviamo anche a copiare il link ufficiale (per completezza)
                    try:
                        # PASSO 2: Trova e clicca sul pulsante "Altre opzioni"
                        print(f"🔍 [#{idx}/{target}] Cerco il pulsante 'Altre opzioni'...")
                        
                        more_options_button = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Altre opzioni"]'))
                        )
                        
                        print(f"👆 [#{idx}/{target}] Clic su 'Altre opzioni'...")
                        simula_movimento_mouse(driver, more_options_button)
                        simula_click_umano(more_options_button)
                        time.sleep(random.uniform(1.0, 1.5))  # Attendi che il menu si apra
                        
                        # PASSO 3: Trova e clicca sul pulsante "Copia link" con vari selettori
                        print(f"🔍 [#{idx}/{target}] Cerco il pulsante 'Copia link'...")
                        
                        # Prova tutti i possibili selettori per il pulsante "Copia link"
                        copy_selectors = [
                            "._a9--._ap36._a9_1",  # Classe specifica
                            "//button[contains(., 'Copia link')]",  # Contiene testo "Copia link"
                            "//button[contains(., 'Copy link')]",   # Contiene testo "Copy link"
                            "//div[@role='dialog']//button[contains(., 'Copia')]",  # Qualsiasi bottone nel dialog con "copia"
                            "//div[@role='menu']//button[contains(., 'link') or contains(., 'Link')]",  # Menu con link
                        ]
                        
                        copy_button = None
                        for selector in copy_selectors:
                            try:
                                if selector.startswith("//"):
                                    # È un XPath
                                    buttons = driver.find_elements(By.XPATH, selector)
                                else:
                                    # È un selettore CSS
                                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                
                                if buttons and buttons[0].is_displayed():
                                    copy_button = buttons[0]
                                    print(f"👉 [#{idx}/{target}] Trovato pulsante 'Copia link' con selettore: {selector}")
                                    break
                            except:
                                pass
                        
                        if copy_button:
                            print(f"👆 [#{idx}/{target}] Clic su 'Copia link'...")
                            simula_movimento_mouse(driver, copy_button)
                            simula_click_umano(copy_button)
                            time.sleep(random.uniform(1.0, 1.5))  # Attendi che il link venga copiato
                            
                            # Verifica gli appunti per il link copiato
                            try:
                                copied_url = pyperclip.paste()
                                if copied_url and ('/p/' in copied_url or '/reel/' in copied_url or '/tv/' in copied_url):
                                    # Pulisci l'URL
                                    clean_copied_url = copied_url.split('?')[0]
                                    print(f"ℹ️ [#{idx}/{target}] Link copiato dagli appunti: {clean_copied_url}")
                                    
                                    # Non sovrascriviamo l'URL già salvato, solo per debug
                                    if clean_copied_url != clean_url:
                                        print(f"⚠️ [#{idx}/{target}] URL copiato diverso da URL della barra! Uso quello della barra.")
                            except Exception as clipboard_error:
                                if debug:
                                    print(f"⚠️ Errore con la clipboard: {clipboard_error}")
                        else:
                            print(f"ℹ️ [#{idx}/{target}] Pulsante 'Copia link' non trovato, uso URL dalla barra")
                    
                    except Exception as options_error:
                        if debug:
                            print(f"ℹ️ [#{idx}/{target}] Errore durante l'interazione con i menu: {options_error}")
                        print(f"ℹ️ [#{idx}/{target}] Continuo con URL già salvato dalla barra degli indirizzi")
                else:
                    print(f"❌ [#{idx}/{target}] Non siamo in un post/reel! URL corrente: {post_url}")
                
                # Torna al profilo (usa il pulsante indietro)
                print(f"↩️ [#{idx}/{target}] Torno alla pagina del profilo...")
                driver.back()
                time.sleep(random.uniform(1.5, 2.0))
                
                # Pausa tra i post
                pause_time = random.uniform(0.8, 1.5)
                print(f"⏱️ Pausa di {pause_time:.1f} sec tra i post...")
                time.sleep(pause_time)
            
            # Pausa periodica per sembrare più umani
            if post_count > 0 and post_count % 5 == 0:
                pausa = random.uniform(2, 4)
                print(f"\n⏸️ Pausa breve di {pausa:.1f} secondi dopo 5 post...")
                time.sleep(pausa)
                
            if post_count > 0 and post_count % 10 == 0:
                pausa = random.uniform(4, 8)
                print(f"\n⏸️⏸️ Pausa più lunga di {pausa:.1f} secondi dopo 10 post...")
                time.sleep(pausa)
            
            # Verificare se abbiamo completato il range di post
            if end_idx is not None and current_idx >= end_idx:
                print(f"\n🏁 Completata la raccolta dei post dal {start_idx} al {end_idx}!")
                break
                
            # Scorri per trovare altri post se necessario
            if len(new_elements) < 3 or current_idx < end_idx:  # Se troviamo pochi nuovi elementi o non abbiamo raggiunto l'ultimo post, scorriamo
                print("\n⬇️ Scorrimento per trovare altri post...")
                scorri_lentamente(driver, "giu")
                scroll_count += 1
                time.sleep(random.uniform(1, 2))
    
    except Exception as e:
        print(f"\n❌❌❌ Si è verificato un errore durante la raccolta: {e}")
        if debug:
            traceback.print_exc()
    
    # Riassunto finale
    if collected_urls:
        print(f"\n🎉 RACCOLTA COMPLETATA! {len(collected_urls)} URL salvati in '{output_file}'")
        
        # Mostra i primi 5 URL raccolti (e il totale)
        print("\n📋 Ecco i primi URL raccolti:")
        for i, url in enumerate(collected_urls[:5]):
            print(f"  {i+1}. {url}")
        
        if len(collected_urls) > 5:
            print(f"  ... e altri {len(collected_urls) - 5} URL")
    else:
        print("\n⛔ Non è stato possibile raccogliere alcun URL.")
    
    return collected_urls

def login_to_instagram(driver, username, password, debug=False):
    """Effettua il login a Instagram gestendo i cookie e verificando il login"""
    print("\n🔑 Tentativo di login a Instagram...")
    
    # Naviga alla pagina di login
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(random.uniform(4, 6))  # Attendi più tempo per il caricamento iniziale
    
    # Gestione cookie all'avvio - diversi formati di popup cookie
    try:
        print("🍪 Cercando banner dei cookie...")
        cookie_selectors = [
            "//button[contains(text(), 'Accetta tutti i cookie')]",
            "//button[contains(text(), 'Accept All')]",
            "//button[contains(text(), 'Accept all')]",
            "//button[contains(text(), 'Consenti tutti i cookie')]",
            "//button[contains(text(), 'Consenti')]",
            "//button[contains(text(), 'Allow')]",
            "//button[contains(text(), 'Accept')]",
            "//button[contains(@class, 'aOOlW') and contains(@class, 'bIiDR')]"  # Classe comune bottoni accetta
        ]
        
        for selector in cookie_selectors:
            try:
                cookie_buttons = driver.find_elements(By.XPATH, selector)
                if cookie_buttons and cookie_buttons[0].is_displayed():
                    print(f"🍪 Banner cookie trovato! Cliccando su: {cookie_buttons[0].text}")
                    simula_movimento_mouse(driver, cookie_buttons[0])
                    simula_click_umano(cookie_buttons[0])
                    time.sleep(random.uniform(1, 2))  # Attendi che il banner scompaia
                    print("✅ Cookie accettati")
                    break
            except:
                pass
    except Exception as e:
        if debug:
            print(f"⚠️ Errore nella gestione dei cookie: {e}")
    
    # Verifica se siamo già nella pagina di login
    try:
        # Cerca campo username
        username_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
        )
        
        # Inserisci username come un umano (con pause tra i caratteri)
        print(f"👤 Inserimento nome utente: {username}")
        simula_movimento_mouse(driver, username_input)
        username_input.click()
        time.sleep(0.5)
        username_input.clear()  # Pulisci il campo
        
        # Digita lentamente come un umano
        for char in username:
            username_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        time.sleep(random.uniform(0.5, 1.0))  # Pausa tra username e password
        
        # Inserisci password
        password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        print("🔒 Inserimento password...")
        simula_movimento_mouse(driver, password_input)
        password_input.click()
        time.sleep(0.5)
        
        # Digita lentamente la password
        for char in password:
            password_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        time.sleep(random.uniform(0.5, 1.0))  # Pausa prima del click su login
        
        # Clicca sul pulsante di login
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        print("🖱️ Clic sul pulsante di login...")
        simula_movimento_mouse(driver, login_button)
        simula_click_umano(login_button)
        
        # Attendi che il login sia completato (più tempo per essere sicuri)
        print("⏳ Attesa per il completamento del login...")
        time.sleep(random.uniform(6, 8))
        
        # Verifica se siamo nella homepage o nella pagina di login
        if "instagram.com/accounts/login" in driver.current_url:
            print("❌ Errore di login: le credenziali potrebbero non essere valide")
            if debug:
                # Salva screenshot per debug
                driver.save_screenshot("login_fallito.png")
                print("📸 Screenshot salvato come 'login_fallito.png'")
            return False
        
        # Gestisci eventuali popup post-login
        print("👀 Verificando popup post-login...")
        popup_handlers = [
            # Popup "Salva le tue credenziali"
            ("//button[contains(text(), 'Non ora') or contains(text(), 'Not Now')]", "Popup 'Salva credenziali'"),
            # Popup attiva notifiche
            ("//button[contains(text(), 'Non ora') or contains(text(), 'Not Now')]", "Popup 'Attiva notifiche'"),
            # Altri popup generici con "Non ora"
            ("//button[contains(text(), 'Cancel') or contains(text(), 'Annulla')]", "Popup generico"),
            # Popup di verifica dell'account
            ("//button[contains(text(), 'Verifica più tardi') or contains(text(), 'Verify later')]", "Popup 'Verifica account'"),
        ]
        
        for selector, popup_name in popup_handlers:
            try:
                buttons = driver.find_elements(By.XPATH, selector)
                for btn in buttons:
                    if btn.is_displayed():
                        print(f"🔔 {popup_name} rilevato, gestisco...")
                        simula_movimento_mouse(driver, btn)
                        simula_click_umano(btn)
                        time.sleep(random.uniform(1, 2))
            except Exception as e:
                if debug:
                    print(f"⚠️ Errore nella gestione del {popup_name}: {e}")
        
        print("✅ Login completato con successo!")
        time.sleep(random.uniform(2, 3))  # Pausa dopo login
        return True
    
    except Exception as e:
        print(f"❌ Errore durante il login: {e}")
        if debug:
            traceback.print_exc()
            driver.save_screenshot("errore_login.png")
            print("📸 Screenshot salvato come 'errore_login.png'")
        return False

def main():
    parser = argparse.ArgumentParser(description='Collector Instagram con selezione per indici')
    parser.add_argument('username', type=str, help='Nome utente del profilo Instagram da cui raccogliere i post')
    parser.add_argument('--output', '-o', type=str, default="urls_scelti.txt", help='File di output per gli URL')
    parser.add_argument('--start_idx', '-s', type=int, default=1, help='Indice del primo post da raccogliere (default: 1)')
    parser.add_argument('--end_idx', '-e', type=int, default=None, help='Indice dell\'ultimo post da raccogliere (default: nessun limite)')
    parser.add_argument('--login_user', '-u', type=str, help='Username per il login (opzionale ma consigliato)')
    parser.add_argument('--login_pass', '-p', type=str, help='Password per il login')
    parser.add_argument('--debug', '-d', action='store_true', help='Modalità debug con output aggiuntivo')
    args = parser.parse_args()
    
    # Configurazione del driver Chrome
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1366,768")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Nascondi che stai usando un webdriver
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent realistico
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36")
    
    # Disabilita notifiche
    chrome_options.add_experimental_option("prefs", { 
        "profile.default_content_setting_values.notifications": 2 
    })
    
    print("\n🚀 Avvio del browser Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Nascondi il webdriver con JavaScript
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Login se sono fornite le credenziali
        if args.login_user and args.login_pass:
            login_success = login_to_instagram(driver, args.login_user, args.login_pass, args.debug)
            if not login_success and args.debug:
                print("⚠️ Continuando senza login...")
        else:
            print("ℹ️ Nessuna credenziale fornita, continuando senza login...")
        
        # Usa la versione specializzata per la raccolta con indici
        collect_posts_by_indices(driver, args.username, args.output, args.start_idx, args.end_idx, args.debug)
        
    except Exception as e:
        print(f"❌ Si è verificato un errore: {e}")
        if args.debug:
            traceback.print_exc()
    
    finally:
        print("\n🔚 Chiusura del browser...")
        driver.quit()

if __name__ == "__main__":
    main()