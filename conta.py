import os
import argparse
from datetime import datetime
import time
from instaloader import Instaloader, Post  # Importazione corretta della classe

def count_posts(urls_file):
    """Conta quanti post ci sono nel file degli URL"""
    try:
        with open(urls_file, 'r') as file:
            urls = [line.strip() for line in file if line.strip() and not line.startswith('#')]
            return len(urls)
    except FileNotFoundError:
        print(f"Errore: Il file {urls_file} non è stato trovato.")
        return 0

def download_instagram_videos(urls_file, start_index=None, end_index=None, login_user=None, login_pass=None):
    """
    Scarica i video di Instagram specificati nel file degli URL.
    Permette di specificare un intervallo di post da scaricare.
    
    Args:
        urls_file (str): Percorso del file contenente gli URL
        start_index (int, optional): Indice del primo post da scaricare (base 1). Default: None (dall'inizio)
        end_index (int, optional): Indice dell'ultimo post da scaricare (incluso). Default: None (fino alla fine)
        login_user (str, optional): Username per il login a Instagram
        login_pass (str, optional): Password per il login a Instagram
    """
    # Conta il numero totale di post disponibili
    total_posts = count_posts(urls_file)
    if total_posts == 0:
        print("Nessun post da scaricare. Assicurati che il file URLs esista e contenga link validi.")
        return
    
    # Gestisci gli indici di default
    if start_index is None:
        start_index = 1
    if end_index is None or end_index > total_posts:
        end_index = total_posts
    
    # Valida gli indici
    if start_index < 1:
        start_index = 1
        print("Indice iniziale non valido, impostato a 1")
    if start_index > total_posts:
        print(f"Errore: l'indice iniziale ({start_index}) è maggiore del numero di post disponibili ({total_posts})")
        return
    if end_index < start_index:
        print(f"Errore: l'indice finale ({end_index}) è minore dell'indice iniziale ({start_index})")
        return
    
    # Mostra riepilogo
    print(f"\n📋 RIEPILOGO:")
    print(f"  📊 Post totali nel file: {total_posts}")
    print(f"  🔢 Intervallo selezionato: dal post #{start_index} al post #{end_index}")
    print(f"  📥 Numero di post da scaricare: {end_index - start_index + 1}")
    
    # Inizializzazione di Instaloader
    L = Instaloader(download_videos=True, 
                   download_video_thumbnails=False,
                   download_pictures=False,
                   download_geotags=False,
                   download_comments=False,
                   save_metadata=False)
    
    # Login se sono fornite le credenziali
    if login_user and login_pass:
        try:
            print(f"\n🔑 Login come {login_user}...")
            L.login(login_user, login_pass)
            print("✅ Login effettuato con successo!")
        except Exception as e:
            print(f"❌ Errore durante il login: {str(e)}")
            print("⚠️ Continuo senza login, potrebbero esserci limitazioni...")
    
    # Creazione della cartella di output se non esiste
    output_dir = "instagram_videos"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Leggi gli URL dal file
    try:
        with open(urls_file, 'r') as file:
            all_urls = [line.strip() for line in file if line.strip() and not line.startswith('#')]
            
            # Seleziona solo gli URL nell'intervallo specificato
            selected_urls = all_urls[start_index-1:end_index]
    except FileNotFoundError:
        print(f"Errore: Il file {urls_file} non è stato trovato.")
        return
    
    print(f"\n🚀 INIZIO DOWNLOAD: {len(selected_urls)} post da scaricare")
    
    # Elabora ogni URL selezionato
    for i, url in enumerate(selected_urls):
        try:
            # Calcola l'indice reale nel file originale
            real_index = start_index + i
            
            # Estrai lo shortcode dall'URL
            shortcode = None
            
            if '/p/' in url:
                shortcode = url.split('/p/')[1].split('/')[0]
            elif '/reel/' in url:
                shortcode = url.split('/reel/')[1].split('/')[0]
            elif '/tv/' in url:
                shortcode = url.split('/tv/')[1].split('/')[0]
            else:
                print(f"⚠️ URL non valido: {url}")
                continue
                
            # Rimuovi eventuali parametri URL
            shortcode = shortcode.split('?')[0]
            print(f"\n📥 [{i+1}/{len(selected_urls)}] Scaricamento post #{real_index}: {shortcode}")
            
            # Scarica il post
            try:
                post = Post.from_shortcode(L.context, shortcode)
                
                # Cambia la directory di lavoro
                original_dir = os.getcwd()
                os.chdir(output_dir)
                
                # Crea una cartella per questo post
                post_dir = f"{post.owner_username}_{post.date_utc.strftime('%Y%m%d')}_{shortcode}"
                
                # Scarica il video
                print(f"🎬 Download del post di {post.owner_username}...")
                L.download_post(post, target=post_dir)
                
                # Salva la caption in un file di testo
                if post.caption:
                    caption_file = os.path.join(post_dir, "caption.txt")
                    try:
                        with open(caption_file, "w", encoding="utf-8") as f:
                            f.write(post.caption)
                        print(f"📝 Caption salvata nel file '{caption_file}'")
                    except Exception as caption_error:
                        print(f"⚠️ Impossibile salvare la caption: {str(caption_error)}")
                
                # Ritorna alla directory principale
                os.chdir(original_dir)
                
                print(f"✅ Post #{real_index} scaricato con successo!")
                
            except Exception as post_error:
                print(f"⚠️ Errore durante il download del post {shortcode}: {str(post_error)}")
            
            # Attendi per evitare di essere bloccato da Instagram
            delay = 2 + i % 3  # Varia il delay per sembrare più umano
            print(f"⏳ Attesa di {delay} secondi prima del prossimo download...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"❌ Errore generico per URL {url}: {str(e)}")
            time.sleep(2)  # Attesa anche in caso di errore
    
    print("\n✨ Download completato! ✨")
    print(f"📂 I video sono stati salvati nella cartella: {os.path.abspath(output_dir)}")

def interactive_mode(urls_file, login_user=None, login_pass=None):
    """Esegue il programma in modalità interattiva"""
    total_posts = count_posts(urls_file)
    
    if total_posts == 0:
        print("Nessun post da scaricare. Assicurati che il file URLs esista e contenga link validi.")
        return
    
    print("\n=== 📱 INSTAGRAM POST DOWNLOADER ===")
    print(f"📊 Trovati {total_posts} post nel file '{urls_file}'")
    print("\nScegli una delle seguenti opzioni:")
    print("1️⃣ Scarica tutti i post")
    print("2️⃣ Scarica un intervallo specifico di post")
    print("3️⃣ Scarica un singolo post")
    print("0️⃣ Esci")
    
    choice = input("\n👉 Inserisci la tua scelta (0-3): ")
    
    if choice == "0":
        print("Uscita dal programma.")
        return
    elif choice == "1":
        # Scarica tutti
        download_instagram_videos(urls_file, login_user=login_user, login_pass=login_pass)
    elif choice == "2":
        # Scarica intervallo
        while True:
            try:
                start = int(input(f"\n👉 Inserisci il numero del primo post da scaricare (1-{total_posts}): "))
                if 1 <= start <= total_posts:
                    break
                print(f"⚠️ Inserisci un numero tra 1 e {total_posts}.")
            except ValueError:
                print("⚠️ Inserisci un numero valido.")
        
        while True:
            try:
                end = int(input(f"👉 Inserisci il numero dell'ultimo post da scaricare ({start}-{total_posts}): "))
                if start <= end <= total_posts:
                    break
                print(f"⚠️ Inserisci un numero tra {start} e {total_posts}.")
            except ValueError:
                print("⚠️ Inserisci un numero valido.")
        
        download_instagram_videos(urls_file, start, end, login_user=login_user, login_pass=login_pass)
    elif choice == "3":
        # Scarica singolo post
        while True:
            try:
                post_num = int(input(f"\n👉 Inserisci il numero del post da scaricare (1-{total_posts}): "))
                if 1 <= post_num <= total_posts:
                    break
                print(f"⚠️ Inserisci un numero tra 1 e {total_posts}.")
            except ValueError:
                print("⚠️ Inserisci un numero valido.")
        
        download_instagram_videos(urls_file, post_num, post_num, login_user=login_user, login_pass=login_pass)
    else:
        print("⚠️ Scelta non valida.")

def main():
    parser = argparse.ArgumentParser(description='Scarica video da Instagram dai link specifici')
    parser.add_argument('--file', '-f', type=str, default="urls.txt", help='File contenente gli URL dei post')
    parser.add_argument('--start', '-s', type=int, help='Indice del primo post da scaricare (1-based)')
    parser.add_argument('--end', '-e', type=int, help='Indice dell\'ultimo post da scaricare (1-based)')
    parser.add_argument('--login_user', '-u', type=str, help='Username per il login (opzionale)')
    parser.add_argument('--login_pass', '-p', type=str, help='Password per il login (opzionale)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Esegui in modalità interattiva')
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode(args.file, args.login_user, args.login_pass)
    else:
        download_instagram_videos(args.file, args.start, args.end, args.login_user, args.login_pass)

if __name__ == "__main__":
    main()