import os
from datetime import datetime
import time
from instaloader import Instaloader, Post  # Importazione corretta della classe

def download_instagram_videos(urls_file):
    # Inizializzazione di Instaloader
    L = Instaloader(download_videos=True, 
                   download_video_thumbnails=False,
                   download_pictures=False,
                   download_geotags=False,
                   download_comments=False,
                   save_metadata=False)
    
    # Creazione della cartella di output se non esiste
    output_dir = "instagram_videos"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Leggi gli URL dal file
    try:
        with open(urls_file, 'r') as file:
            urls = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"Errore: Il file {urls_file} non è stato trovato.")
        return
    
    print(f"Trovati {len(urls)} URL da scaricare")
    
    # Elabora ogni URL
    for i, url in enumerate(urls):
        try:
            # Estrai lo shortcode dall'URL
            shortcode = None
            
            if '/p/' in url:
                shortcode = url.split('/p/')[1].split('/')[0]
            elif '/reel/' in url:
                shortcode = url.split('/reel/')[1].split('/')[0]
            elif '/tv/' in url:
                shortcode = url.split('/tv/')[1].split('/')[0]
            else:
                print(f"URL non valido: {url}")
                continue
                
            # Rimuovi eventuali parametri URL
            shortcode = shortcode.split('?')[0]
            print(f"Scaricamento post {i+1}/{len(urls)}: {shortcode}")
            
            # Scarica il post
            try:
                post = Post.from_shortcode(L.context, shortcode)
                
                # Cambia la directory di lavoro
                original_dir = os.getcwd()
                os.chdir(output_dir)
                
                # Scarica il video
                print(f"Download del post di {post.owner_username}...")
                L.download_post(post, target=f"{post.owner_username}_{post.date_utc.strftime('%Y%m%d')}_{shortcode}")
                
                # Ritorna alla directory principale
                os.chdir(original_dir)
                
                print(f"✅ Post {i+1}/{len(urls)} scaricato con successo!")
                
            except Exception as post_error:
                print(f"⚠️ Errore durante il download del post {shortcode}: {str(post_error)}")
            
            # Attendi per evitare di essere bloccato da Instagram
            delay = 3 + i % 3  # Varia il delay per sembrare più umano
            print(f"Attesa di {delay} secondi prima del prossimo download...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"❌ Errore generico per URL {url}: {str(e)}")
            time.sleep(2)  # Attesa anche in caso di errore
    
    print("Download completato!")

def login_if_needed(username, password=None):
    """Effettua il login a Instagram se necessario"""
    try:
        # Crea un'istanza di Instaloader
        L = Instaloader()
        
        # Controlla se sono già presenti le credenziali salvate
        try:
            L.load_session_from_file(username)
            print(f"Sessione caricata per l'utente {username}")
        except FileNotFoundError:
            if password:
                print(f"Login come {username}...")
                L.login(username, password)
                print("Login effettuato con successo!")
                L.save_session_to_file()
            else:
                print("Password non fornita e nessuna sessione salvata trovata.")
                return None
        
        return L
    except Exception as e:
        print(f"Errore durante il login: {str(e)}")
        return None

if __name__ == "__main__":
    # Puoi uncommenta il login per usare un account (consigliato per evitare limitazioni)
    # L = login_if_needed("il_tuo_username", "la_tua_password")
    # if L:
    #    download_instagram_videos("urls.txt", L)
    # else:
    download_instagram_videos("urls.txt")