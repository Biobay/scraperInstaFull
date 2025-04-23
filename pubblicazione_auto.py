import os
import time
import random
import argparse
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
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

def trova_video_casuale(directory_base):
    """
    Trova un video casuale nelle sottocartelle della directory specificata
    Restituisce il percorso del video e il testo della caption se presente
    """
    # Trova tutte le sottocartelle
    subdirs = [d for d in os.listdir(directory_base) if os.path.isdir(os.path.join(directory_base, d))]
    
    if not subdirs:
        print(f"Nessuna sottocartella trovata in {directory_base}")
        return None, None
    
    # Seleziona una sottocartella casuale
    random_subdir = random.choice(subdirs)
    subdir_path = os.path.join(directory_base, random_subdir)
    
    print(f"Selezionata cartella casuale: {random_subdir}")
    
    # Trova tutti i file nella sottocartella
    files = os.listdir(subdir_path)
    
    # Cerca file video
    video_files = [f for f in files if f.endswith(('.mp4', '.mov', '.avi'))]
    
    if not video_files:
        print(f"Nessun video trovato in {subdir_path}")
        return None, None
    
    # Seleziona un video casuale
    random_video = random.choice(video_files)
    video_path = os.path.join(subdir_path, random_video)
    
    print(f"Selezionato video casuale: {random_video}")
    
    # Cerca file di testo che potrebbe contenere la caption
    txt_files = [f for f in files if f.endswith('.txt')]
    caption = ""
    
    if txt_files:
        txt_file = txt_files[0]  # Prendi il primo file di testo trovato
        try:
            with open(os.path.join(subdir_path, txt_file), 'r', encoding='utf-8') as f:
                caption = f.read().strip()
            print(f"Caption trovata nel file {txt_file}")
        except Exception as e:
            print(f"Errore nella lettura della caption: {e}")
    
    return video_path, caption

def login_to_instagram(driver, username, password, debug=False):
    """Effettua il login a Instagram simulando comportamento umano"""
    print(f"Tentativo di login come {username}...")
    
    # Naviga alla pagina di login
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(random.uniform(2, 4))  # Attesa variabile per caricamento
    
    # Gestisci eventuali popup sui cookie
    try:
        cookie_buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "Consenti") or contains(text(), "Allow") or contains(text(), "Accept")]')
        if cookie_buttons:
            simula_movimento_mouse(driver, cookie_buttons[0])
            simula_click_umano(cookie_buttons[0])
    except Exception as e:
        if debug:
            print(f"Nessun popup cookie o errore: {e}")
    
    # Inserisci username come un umano (con pause tra i caratteri)
    try:
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
        )
        simula_movimento_mouse(driver, username_input)
        username_input.click()
        
        # Digita lentamente come un umano
        for char in username:
            username_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        time.sleep(random.uniform(0.5, 1.0))  # Pausa tra username e password
        
        # Inserisci password
        password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        simula_movimento_mouse(driver, password_input)
        password_input.click()
        
        # Digita lentamente la password
        for char in password:
            password_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        time.sleep(random.uniform(0.5, 1.0))  # Pausa prima del click su login
        
        # Clicca sul pulsante di login
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        simula_movimento_mouse(driver, login_button)
        simula_click_umano(login_button)
        
        # Attendi che il login sia completato
        time.sleep(random.uniform(5, 7))
        
        # Verifica se siamo nella homepage
        if "instagram.com/accounts/login" in driver.current_url:
            print("Errore di login: le credenziali potrebbero non essere valide")
            return False
        
        # Gestisci eventuali popup post-login
        try:
            not_now_buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "Non ora") or contains(text(), "Not Now") or contains(text(), "Cancel")]')
            if not_now_buttons:
                simula_movimento_mouse(driver, not_now_buttons[0])
                simula_click_umano(not_now_buttons[0])
        except Exception as e:
            if debug:
                print(f"Nessun popup post-login o errore: {e}")
        
        print("Login completato con successo!")
        time.sleep(random.uniform(2, 4))  # Pausa dopo login
        return True
    
    except Exception as e:
        print(f"Errore durante il login: {e}")
        if debug:
            traceback.print_exc()
        return False

def pubblica_post_instagram(driver, media_path, caption="", debug=False):
    """Pubblica un post su Instagram simulando le azioni umane"""
    try:
        if not os.path.exists(media_path):
            print(f"Errore: Il file {media_path} non esiste!")
            return False
        
        print("Navigando alla homepage di Instagram...")
        driver.get('https://www.instagram.com/')
        time.sleep(random.uniform(3, 5))
        
        # Trova il pulsante per creare un nuovo post
        print("Cercando il pulsante per creare un nuovo post...")
        create_buttons = []
        
        # Diverse strategie per trovare il pulsante di creazione post
        selectors = [
            (By.XPATH, "//span[text()='Crea']/../.."),
            (By.XPATH, "//span[text()='Create']/../.."),
            (By.XPATH, "//div[@role='button' and contains(., 'Crea')]"),
            (By.XPATH, "//div[@role='button' and contains(., 'Create')]"),
            (By.CSS_SELECTOR, "[aria-label='Nuovo post']"),
            (By.CSS_SELECTOR, "[aria-label='New post']"),
            (By.XPATH, "//div[contains(@class, 'xh8yej3')]//div[@role='button']")  # Classe comune del pulsante crea
        ]
        
        for selector_type, selector in selectors:
            try:
                elements = driver.find_elements(selector_type, selector)
                create_buttons.extend(elements)
            except:
                pass
        
        # Filtra i pulsanti visibili
        visible_buttons = [btn for btn in create_buttons if btn.is_displayed()]
        
        if not visible_buttons:
            print("Non è stato possibile trovare il pulsante per creare un nuovo post!")
            if debug:
                screenshot_path = os.path.join(os.getcwd(), "debug_screenshot.png")
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot salvato in: {screenshot_path}")
            return False
        
        # Clicca sul pulsante per creare un nuovo post
        print("Cliccando sul pulsante per creare un nuovo post...")
        simula_movimento_mouse(driver, visible_buttons[0])
        simula_click_umano(visible_buttons[0])
        time.sleep(random.uniform(2, 3))
        
        # Carica il file
        print(f"Caricando il file: {media_path}")
        try:
            # Cerca l'input file (spesso nascosto)
            file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
            if file_inputs:
                # Invia il percorso del file all'input
                file_inputs[0].send_keys(os.path.abspath(media_path))
            else:
                # Se non troviamo l'input file, proviamo a cliccare su un'area di drop
                drop_areas = driver.find_elements(By.XPATH, "//div[contains(text(), 'Trascina le foto e i video qui')]")
                if drop_areas:
                    # Simula un'operazione di drag and drop (complessa e potrebbe non funzionare)
                    print("Tentativo di simulazione drag and drop... (potrebbe non funzionare)")
                    simula_movimento_mouse(driver, drop_areas[0])
                    simula_click_umano(drop_areas[0])
                    time.sleep(1)
                    
                    # Prova a trovare di nuovo l'input file dopo aver cliccato
                    file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                    if file_inputs:
                        file_inputs[0].send_keys(os.path.abspath(media_path))
                    else:
                        print("Non è stato possibile trovare un modo per caricare il file!")
                        return False
        except Exception as upload_error:
            print(f"Errore durante il caricamento del file: {str(upload_error)}")
            return False
        
        # Attesa per il caricamento
        print("Attesa per il caricamento del file...")
        time.sleep(random.uniform(3, 5))
        
        # Cerca i pulsanti "Avanti" o "Next" e clicca su di essi
        for _ in range(3):  # Ci sono solitamente 2-3 passaggi
            print("Cercando il pulsante Avanti/Next...")
            next_buttons = []
            next_selectors = [
                (By.XPATH, "//button[contains(text(), 'Avanti')]"),
                (By.XPATH, "//button[contains(text(), 'Next')]"),
                (By.XPATH, "//div[@role='button' and contains(., 'Avanti')]"),
                (By.XPATH, "//div[@role='button' and contains(., 'Next')]")
            ]
            
            for selector_type, selector in next_selectors:
                try:
                    elements = driver.find_elements(selector_type, selector)
                    next_buttons.extend(elements)
                except:
                    pass
            
            visible_next = [btn for btn in next_buttons if btn.is_displayed()]
            
            if visible_next:
                print("Cliccando sul pulsante Avanti/Next...")
                simula_movimento_mouse(driver, visible_next[0])
                simula_click_umano(visible_next[0])
                time.sleep(random.uniform(2, 3))
            else:
                # Se non troviamo un pulsante Avanti, potrebbe essere che siamo già all'ultimo passaggio
                print("Nessun pulsante Avanti/Next trovato, potrebbe essere l'ultimo passaggio")
                break
        
        # Inserisci la caption se specificata
        if caption:
            print("Inserendo la caption...")
            caption_fields = []
            caption_selectors = [
                (By.XPATH, "//textarea[contains(@aria-label, 'Scrivi una didascalia')]"),
                (By.XPATH, "//textarea[contains(@aria-label, 'Write a caption')]"),
                (By.XPATH, "//textarea[contains(@placeholder, 'Scrivi una didascalia')]"),
                (By.XPATH, "//textarea[contains(@placeholder, 'Write a caption')]")
            ]
            
            for selector_type, selector in caption_selectors:
                try:
                    elements = driver.find_elements(selector_type, selector)
                    caption_fields.extend(elements)
                except:
                    pass
            
            visible_fields = [field for field in caption_fields if field.is_displayed()]
            
            if visible_fields:
                simula_movimento_mouse(driver, visible_fields[0])
                visible_fields[0].click()
                time.sleep(0.5)
                
                # Digitazione lenta della caption
                for char in caption:
                    visible_fields[0].send_keys(char)
                    time.sleep(random.uniform(0.01, 0.05))
                
                time.sleep(random.uniform(1, 2))
            else:
                print("Campo caption non trovato!")
        
        # Cerca e clicca il pulsante "Condividi" o "Share"
        print("Cercando il pulsante Condividi/Share...")
        share_buttons = []
        share_selectors = [
            (By.XPATH, "//button[contains(text(), 'Condividi')]"),
            (By.XPATH, "//button[contains(text(), 'Share')]"),
            (By.XPATH, "//div[@role='button' and contains(., 'Condividi')]"),
            (By.XPATH, "//div[@role='button' and contains(., 'Share')]")
        ]
        
        for selector_type, selector in share_selectors:
            try:
                elements = driver.find_elements(selector_type, selector)
                share_buttons.extend(elements)
            except:
                pass
        
        visible_share = [btn for btn in share_buttons if btn.is_displayed()]
        
        if not visible_share:
            print("Non è stato possibile trovare il pulsante Condividi/Share!")
            return False
        
        print("Cliccando sul pulsante Condividi/Share...")
        simula_movimento_mouse(driver, visible_share[0])
        simula_click_umano(visible_share[0])
        
        # Attesa per la pubblicazione
        print("Attesa per la pubblicazione del post...")
        time.sleep(random.uniform(8, 10))
        
        # Verifica se il post è stato pubblicato con successo
        success_messages = driver.find_elements(By.XPATH, "//div[contains(text(), 'Post condiviso') or contains(text(), 'Your post has been shared')]")
        
        if success_messages:
            print("Post pubblicato con successo!")
            return True
        else:
            print("Non è stato possibile verificare se il post è stato pubblicato correttamente.")
            print("Verifica manualmente sul tuo profilo Instagram.")
            return True  # Assumiamo successo anche senza conferma esplicita
        
    except Exception as e:
        print(f"Errore durante la pubblicazione: {str(e)}")
        if debug:
            traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description='Pubblicazione automatica su Instagram')
    parser.add_argument('--media', help='Percorso alla directory dei video o al file media specifico')
    parser.add_argument('--caption', default="", help='Caption per il post (opzionale, sovrascrive caption nei file txt)')
    parser.add_argument('--login_user', required=True, help='Username per il login Instagram')
    parser.add_argument('--login_pass', required=True, help='Password per il login Instagram')
    parser.add_argument('--debug', action='store_true', help='Modalità debug')
    args = parser.parse_args()
    
    print("\n🚀 INIZIO PUBBLICAZIONE AUTOMATICA POST INSTAGRAM")
    
    # Gestione del percorso media
    media_path = args.media
    caption = args.caption
    
    # Se è una directory, cerca un video casuale
    if os.path.isdir(media_path):
        print(f"📁 Media è una directory: {media_path}")
        print("🔍 Ricerca di un video casuale nelle sottocartelle...")
        
        random_video, video_caption = trova_video_casuale(media_path)
        
        if random_video:
            print(f"✅ Video casuale trovato: {random_video}")
            media_path = random_video
            
            # Usa la caption dal file TXT se esiste e se non è stata specificata una caption tramite argomento
            if video_caption and not args.caption:
                caption = video_caption
                print(f"📝 Usando caption dal file di testo: {caption[:50]}..." if len(caption) > 50 else f"📝 Usando caption dal file di testo: {caption}")
        else:
            print("❌ Nessun video trovato nelle sottocartelle!")
            return
    else:
        print(f"🎥 Usando il file media specificato: {media_path}")
    
    # Configura Chrome per simulare un browser umano
    options = Options()
    
    # Impostazioni per sembrare un browser umano
    options.add_argument("--window-size=1366,768")  # Risoluzione comune
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # User agent realistico
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15")
    
    # Disabilita notifiche
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Nasconde la stringa navigator.webdriver
    driver.execute_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    })
    """)
    
    try:
        # Effettua login
        login_successful = login_to_instagram(driver, args.login_user, args.login_pass, args.debug)
        if not login_successful:
            print("❌ Login fallito. Impossibile procedere.")
            return
        
        # Pubblica il post
        success = pubblica_post_instagram(driver, media_path, caption, args.debug)
        
        if success:
            print("\n✅ Pubblicazione completata con successo!")
            # Registra in un file log il post pubblicato
            with open("pubblicazioni.log", "a") as log:
                log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Pubblicato: {os.path.basename(media_path)}\n")
        else:
            print("\n❌ Pubblicazione fallita.")
        
    except Exception as e:
        print(f"\n❌❌❌ Si è verificato un errore critico: {e}")
        if args.debug:
            traceback.print_exc()
    
    finally:
        # Chiudi il browser
        print("\n🔚 Chiusura del browser...")
        time.sleep(random.uniform(1, 2))
        driver.quit()

if __name__ == "__main__":
    main()