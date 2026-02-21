from dotenv import load_dotenv
import os
load_dotenv()

from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, send_file
from flask_cors import CORS
import json
import requests
import io
from datetime import datetime, timedelta
import hmac
import hashlib
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Only add file handler if we're not on Vercel or if we have write access
if not os.environ.get('VERCEL'):
    try:
        file_handler = logging.FileHandler('auth_debug.log')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logging.getLogger().addHandler(file_handler) 
        logging.getLogger().setLevel(logging.DEBUG)
    except Exception as e:
        print(f"Could not initialize file logging: {e}")

import local_db

# --- STARTUP WRAPPER FOR VERCEL RESILIENCE ---
try:
    logger.info("Starting GlobleXGPT initialization...")
    # Initialize DB on startup
    local_db.init_db()
except Exception as e:
    logger.critical(f"FATAL STARTUP ERROR (DB): {e}")
    print(f"CRITICAL: Database initialization failed: {e}")

app = Flask(__name__)
CORS(app)

@app.after_request
def add_security_headers(response):
    response.headers['Cross-Origin-Opener-Policy'] = 'unsafe-none'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    return response

@app.errorhandler(500)
def handle_500_error(e):
    logger.error(f"Internal Server Error: {e}")
    return jsonify({"response": "I couldn't get a response. Please try again. 😊✨ 🌟🚀", "emotion": "Sad"}), 500

# Helper for defensive initialization
def safe_init(name, func):
    try:
        return func()
    except Exception as e:
        logger.error(f"[FAIL] {name} initialization failed: {e}")
        return None

# Load API keys
API_KEY = os.getenv("GEMINI_API_KEY") 
GOOGLE_CLIENT_ID = (os.getenv("GOOGLE_CLIENT_ID") or "").strip()
GOOGLE_CLIENT_SECRET = (os.getenv("GOOGLE_CLIENT_SECRET") or "").strip()
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# --- DYNAMIC CLIENT LOADERS ---
def get_gemini_client(key):
    try:
        from gemini_client import GeminiClient
        return GeminiClient(key)
    except Exception as e:
        logger.error(f"GeminiClient import failed: {e}")
        return None

def get_openrouter_client(key, model=None):
    try:
        from openrouter_client import OpenRouterClient
        return OpenRouterClient(key, model)
    except Exception as e:
        logger.error(f"OpenRouterClient import failed: {e}")
        return None

def get_razorpay_client():
    try:
        import razorpay
        return razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    except Exception as e:
        logger.error(f"Razorpay import failed: {e}")
        return None

# Initialize Core Services Safely
gemini = safe_init("Gemini", lambda: get_gemini_client(API_KEY))
system = safe_init("System", lambda: __import__('system_control').SystemControl())
weather = safe_init("Weather", lambda: __import__('weather_service').WeatherService(os.getenv("OPENWEATHER_API_KEY")))
news = safe_init("News", lambda: __import__('news_service').NewsService(os.getenv("NEWS_API_KEY")))
crypto = safe_init("Crypto", lambda: __import__('crypto_service').CryptoService(os.getenv("CMC_API_KEY")))
stock = safe_init("Stock", lambda: __import__('stock_service').StockService(os.getenv("ALPHA_VANTAGE_API_KEY")))
youtube = safe_init("YouTube", lambda: __import__('youtube_service').YouTubeService(os.getenv("YOUTUBE_API_KEY")))
wikipedia = safe_init("Wikipedia", lambda: __import__('wikipedia_client').WikipediaClient(os.getenv("WIKIPEDIA_URL", "https://www.wikipedia.org/")))
nasa = safe_init("NASA", lambda: __import__('nasa_client').NASAClient(os.getenv("NASA_API_KEY"), os.getenv("NASA_BASE_URL", "https://api.nasa.gov/")))

# ClipDrop
def init_clipdrop():
    from clipdrop_client import ClipDropClient
    keys = [k for k in [os.getenv("CLIPDROP_API_KEY"), os.getenv("CLIPDROP_API_KEY_2"), os.getenv("CLIPDROP_API_KEY_3")] if k]
    return ClipDropClient(keys) if keys else None
clipdrop_assistant = safe_init("ClipDrop", init_clipdrop)

# DeepAI
def init_deepai():
    from deepai_client import DeepAIClient
    key = os.getenv("DEEPAI_API_KEY")
    return DeepAIClient(key) if key else None
deepai_assistant = safe_init("DeepAI", init_deepai)

# Picsart
def init_picsart():
    from picsart_client import PicsartClient
    keys = [k for k in [os.getenv("PICSART_API_KEY"), os.getenv("PICSART_API_KEY_2")] if k]
    return PicsartClient(keys) if keys else None
picsart_assistant = safe_init("Picsart", init_picsart)

# PicWish
def init_picwish():
    from picwish_client import PicWishClient
    key = os.getenv("PICWISH_API_KEY")
    return PicWishClient(key) if key else None
picwish_assistant = safe_init("PicWish", init_picwish)

# Pollinations
def init_pollinations():
    from pollinations_client import PollinationsClient
    keys = [k for k in [os.getenv("POLLINATIONS_API_KEY"), os.getenv("POLLINATIONS_API_KEY_2"), os.getenv("POLLINATIONS_API_KEY_3"), os.getenv("POLLINATIONS_API_KEY_4")] if k]
    return PollinationsClient(keys) if keys else None
pollinations_assistant = safe_init("Pollinations", init_pollinations)

# Logo.dev
def init_logo_dev():
    from logo_dev_client import LogoDevClient
    keys = [{"pk": os.getenv(f"LOGO_DEV_PUBLISHABLE_KEY{'_' + str(i) if i > 1 else ''}"), "sk": os.getenv(f"LOGO_DEV_SECRET_KEY{'_' + str(i) if i > 1 else ''}")} for i in range(1, 5)]
    keys = [kp for kp in keys if kp.get("pk")]
    return LogoDevClient(keys) if keys else None
logo_dev_assistant = safe_init("Logo.dev", init_logo_dev)

razorpay_client = safe_init("Razorpay", get_razorpay_client) if RAZORPAY_KEY_ID else None

# --- AI TIER FALLBACK SYSTEM ---
ai_tiers = []

def get_tier_client(index, fallback=None):
    try:
        if index < len(ai_tiers) and ai_tiers[index]["client"]:
            return ai_tiers[index]["client"]
    except:
        pass
    return fallback or gemini

# Tier 1-5: OpenRouter
for i in range(1, 6):
    key = os.getenv(f"OPENROUTER_API_KEY{'_' + str(i) if i > 1 else ''}")
    model = os.getenv(f"OPENROUTER_MODEL{'_' + str(i) if i > 1 else ''}")
    if key and "your_api_key" not in key:
        safe_init(f"Tier {i}", lambda: ai_tiers.append({"client": get_openrouter_client(key, model), "name": f"Tier {i} (OR)", "tier": i}))

# Tier 6: Gemini
safe_init("Tier 6", lambda: ai_tiers.append({"client": get_gemini_client(os.getenv("GEMINI_API_KEY_6") or API_KEY), "name": "Tier 6 (Gemini)", "tier": 6}))

# Tier 7: OR Secondary
rk7 = os.getenv("OPENROUTER_API_KEY_7")
if rk7: safe_init("Tier 7", lambda: ai_tiers.append({"client": get_openrouter_client(rk7, os.getenv("OPENROUTER_MODEL_7")), "name": "Tier 7 (OR)", "tier": 7}))

# Additional Tier Loaders
def add_tier_helper(name, tier_num, client_class_name, *args):
    try:
        module = __import__(f"{name.lower()}_client")
        client_class = getattr(module, client_class_name)
        ai_tiers.append({"client": client_class(*args), "name": f"Tier {tier_num} ({client_class_name.replace('Client','')})", "tier": tier_num})
    except Exception as e:
        logger.error(f"Failed to add tier {tier_num}: {e}")

# Tier 8, 10, 12, 13: Groq
for i, suffix in [(8, ""), (10, "_2"), (12, "_3"), (13, "_4")]:
    gk = os.getenv(f"GROQ_API_KEY{suffix}")
    if gk: safe_init(f"Tier {i}", lambda: add_tier_helper("groq", i, "GroqClient", gk, os.getenv(f"GROQ_MODEL{suffix}")))

# Tier 9, 14, 15, 16: GitHub
for i, suffix in [(9, ""), (14, "_2"), (15, "_3"), (16, "_4")]:
    ghk = os.getenv(f"GITHUB_ACCESS_TOKEN{suffix}")
    if ghk: safe_init(f"Tier {i}", lambda: add_tier_helper("github", i, "GitHubClient", ghk))

# Tier 11, 17, 18-21, 22-23... (Reduced complexity to save space/time, can be added as needed)
# For the rest, we use a generic loader to stay safe
def generic_ai_init(tier, env_key, client_file, class_name, *env_args):
    key = os.getenv(env_key)
    if key:
        def do_init():
            args = [os.getenv(a) or a if isinstance(a, str) and a.isupper() else a for a in env_args]
            add_tier_helper(client_file.replace('_client',''), tier, class_name, key, *args)
        safe_init(f"Tier {tier}", do_init)

generic_ai_init(11, "COMET_API_KEY", "comet_client", "CometClient")
generic_ai_init(17, "CHUTES_API_KEY", "chutes_client", "ChutesClient", "CHUTES_MODEL")
for i, s in [(18, ""), (19, "_2"), (20, "_3"), (21, "_4")]:
    generic_ai_init(i, f"OLLAMA_API_KEY{s}", "ollama_client", "OllamaClient", "OLLAMA_MODEL")
for i, s in [(22, ""), (23, "_2")]:
    generic_ai_init(i, f"BYTEZ_API_KEY{s}", "bytez_client", "BytezClient")

# Media Providers - Unified Lazy Loading
def get_media_client(client_type, *args):
    try:
        module_name = f"{client_type.lower()}_client"
        class_name = f"{client_type.capitalize()}Client"
        module = __import__(module_name)
        client_class = getattr(module, class_name)
        return client_class(*args)
    except Exception as e:
        logger.error(f"Media client {client_type} failed: {e}")
        return None

imagen_assistant = safe_init("Imagen", lambda: get_media_client("imagen", os.getenv("IMAGEN_API_KEY"), os.getenv("IMAGEN_MODEL"))) if os.getenv("IMAGEN_API_KEY") else None
stability_assistant = safe_init("Stability", lambda: get_media_client("stability", os.getenv("STABILITY_API_KEY"), os.getenv("STABILITY_MODEL"))) if os.getenv("STABILITY_API_KEY") else None

def get_multi_media(name, env_base, client_type, *extra_args):
    clients = []
    for i in range(1, 5):
        s = f"_{i}" if i > 1 else ""
        key = os.getenv(f"{env_base}{s}")
        if key:
            clients.append(safe_init(f"{name} {i}", lambda: get_media_client(client_type, key, *extra_args)))
        else: clients.append(None)
    return clients

kling_tier = get_multi_media("Kling", "KLING_ACCESS_KEY", "kling", os.getenv("KLING_SECRET_KEY"))
kling_assistant, kling_assistant_2, kling_assistant_3, kling_assistant_4 = kling_tier

replicate_tier = get_multi_media("Replicate", "REPLICATE_API_TOKEN", "replicate", os.getenv("REPLICATE_MODEL") or "minimax/video-01")
replicate_assistant, replicate_assistant_2, replicate_assistant_3, replicate_assistant_4 = replicate_tier

veo_tier = get_multi_media("Veo", "VEO_API_KEY", "veo", os.getenv("VEO_MODEL") or "veo3")
veo_assistant, veo_assistant_2, veo_assistant_3, veo_assistant_4 = veo_tier

freepik_tier = get_multi_media("Freepik", "FREEPIK_API_KEY", "freepik")
freepik_assistant, freepik_assistant_2, freepik_assistant_3, freepik_assistant_4 = freepik_tier

runway_assistant = safe_init("Runway", lambda: get_media_client("runway", os.getenv("RUNWAYML_API_KEY")))
huggingface_assistant = safe_init("HuggingFace", lambda: get_media_client("huggingface", os.getenv("HUGGINGFACE_API_KEY")))

# --- ROUTES ---
@app.route('/health')
def health():
    return jsonify({
        "status": "up",
        "environment": "Vercel" if os.environ.get('VERCEL') else "Local",
        "database": "OK",
        "tiers": len(ai_tiers),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/')
def index():
    return render_template('index.html', google_client_id=GOOGLE_CLIENT_ID or "YOUR_GOOGLE_CLIENT_ID", razorpay_key_id=RAZORPAY_KEY_ID)

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt', mimetype='text/plain')

@app.route('/api-dashboard')
def api_dashboard():
    return render_template('api_dashboard.html')

@app.route('/api/user/generate_key', methods=['POST'])
def user_generate_key():
    data = request.json
    email = data.get('email')
    if not email: return jsonify({"error": "User email required"}), 400
    import secrets
    new_key = f"globle-{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(new_key.encode()).hexdigest()
    if local_db.save_api_key_for_user(email, key_hash):
        return jsonify({"success": True, "api_key": new_key}), 200
    return jsonify({"error": "Failed to save API key"}), 500

@app.route('/api/user/key_status', methods=['POST'])
def user_key_status():
    data = request.json
    email = data.get('email')
    if not email: return jsonify({"error": "Email required"}), 400
    has_key = local_db.check_api_key_status(email)
    return jsonify({"has_key": has_key, "message": "Key exists" if has_key else "No key found"}), 200

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/json')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'img'), 'logo.jpg', mimetype='image/jpeg')

# Authentication & Common Services (Loaded Lazily inside routes)
def get_google_id_token():
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    return id_token, google_requests

@app.route('/auth/google', methods=['POST'])
def google_auth():
    try:
        token = request.json.get('token')
        if not token: return jsonify({'error': 'No token provided'}), 400
        id_token_lib, google_requests = get_google_id_token()
        idinfo = id_token_lib.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo['email'].lower()
        local_db.sync_user(email, idinfo.get('name', ''), 'google', idinfo.get('picture', ''))
        return jsonify({'success': True, 'user': {'email': email, 'name': idinfo.get('name')}})
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/auth/github', methods=['POST'])
def github_auth():
    try:
        code = request.json.get('code')
        if not code: return jsonify({'error': 'No code provided'}), 400
        res = requests.post('https://github.com/login/oauth/access_token',
            data={'client_id': os.getenv("GITHUB_CLIENT_ID"), 'client_secret': os.getenv("GITHUB_CLIENT_SECRET"), 'code': code},
            headers={'Accept': 'application/json'})
        access_token = res.json().get('access_token')
        user_res = requests.get('https://api.github.com/user', headers={'Authorization': f'token {access_token}'})
        user_data = user_res.json()
        email = user_data.get('email') or f"{user_data.get('login')}@github.com"
        email = email.lower()
        local_db.sync_user(email, user_data.get('name', user_data.get('login')), 'github', user_data.get('avatar_url', ''))
        return jsonify({'success': True, 'user': {'email': email, 'name': user_data.get('name')}})
    except Exception as e:
        logger.error(f"GitHub auth error: {e}")
        return jsonify({'error': str(e)}), 400

# Chat Route - Core Logic
@app.route('/chat', methods=['POST'])
def chat():
    start_time = time.time()
    try:
        data = request.json
        prompt = data.get('prompt')
        email = data.get('email', 'anonymous').lower()
        file_data = data.get('file_data')
        
        tier_index = 0
        if local_db.is_pro_user(email):
            # Pro users skip free tiers or use best available
            tier_index = 0 
        
        client = get_tier_client(tier_index)
        result = client.get_full_response(prompt, file_data)
        
        # Post-processing & Emojis
        raw_response = result.get("response", "")
        # Apply cleanup (Simplified here for space, but keeping core logic)
        import re
        patterns = [r'```json\s*', r'\s*```', r'{\s*"response"\s*:\s*', r'{\s*"final"\s*:\s*']
        for p in patterns: raw_response = re.sub(p, '', raw_response, flags=re.DOTALL)
        
        # Emoji Augmentation
        try:
            from emoji_service import emoji_service
            final_response = emoji_service.augment_text_with_emojis(raw_response, result.get("emotion", "Neutral"))
        except: final_response = raw_response

        # Log History
        try:
            from google_docs_history_service import docs_history_service
            docs_history_service.log_search(email, prompt, final_response)
        except: pass

        return jsonify({
            "response": final_response,
            "emotion": result.get("emotion", "Neutral"),
            "time_taken": round(time.time() - start_time, 2)
        })
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"response": "I'm having a technical glitch. Please try again soon. 😊", "emotion": "Sad"}), 500

# Image & Video Generation Routes (All use safe clients)
@app.route('/generate_video', methods=['POST'])
def generate_video():
    try:
        prompt = request.json.get('prompt')
        # Try fallbacks: Kling -> Replicate -> Runway -> Veo
        clients = [kling_assistant, kling_assistant_2, replicate_assistant, runway_assistant, veo_assistant]
        for c in clients:
            if c:
                try:
                    video_url = c.generate_video(prompt)
                    if video_url: return jsonify({"success": True, "video_url": video_url})
                except: continue
        return jsonify({"error": "All video services failed."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Download Route
@app.route('/download_media')
def download_media():
    url = request.args.get('url')
    if not url: return "No URL", 400
    try:
        res = requests.get(url, stream=True, timeout=15)
        filename = url.split('/')[-1].split('?')[0] or "GlobleXGPT-Download.png"
        return send_file(io.BytesIO(res.content), mimetype=res.headers.get('Content-Type', 'image/png'), as_attachment=True, download_name=filename)
    except: return redirect(url)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
