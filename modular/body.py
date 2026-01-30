from flask import Flask, request, jsonify
from naoqi import ALProxy, ALModule, ALBroker
import time
import logging

# Import sistema azioni
from actions import NaoActions

app = Flask(__name__)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurazione NAO
nao_IP = "nao.local"
nao_port = 9559
sleep_time = 0.01

# Proxy NAOqi
tts = ALProxy("ALTextToSpeech", nao_IP, nao_port)
tts.setVolume(1.0)
animatedSpeech = ALProxy("ALAnimatedSpeech", nao_IP, nao_port)

# Inizializza sistema azioni
logger.info("Initializing NAO Actions...")
nao_actions = NaoActions(nao_IP, nao_port)
logger.info("✓ NAO Actions ready")


class AudioCaptureModule(ALModule):
    """NAOqi module for capturing audio"""
    
    def __init__(self, name):
        ALModule.__init__(self, name)
        self.audio_device = ALProxy("ALAudioDevice", nao_IP, nao_port)
        self.is_listening = False
        self.buffers = []

    def start_listening(self):
        self.audio_device.setClientPreferences(self.getName(), 16000, 3, 0)
        self.audio_device.subscribe(self.getName())
        self.is_listening = True

    def stop_listening(self):
        self.audio_device.unsubscribe(self.getName())
        self.is_listening = False

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        if self.is_listening:
            self.buffers.append(inputBuffer)

    def get_audio_chunk(self):
        if self.buffers:
            return self.buffers.pop(0)
        else:
            return None


# Inizializza broker e audio module
try:
    pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 0, nao_IP, nao_port)
    global AudioCapture
    AudioCapture = AudioCaptureModule("AudioCapture")
    logger.info("✓ AudioCapture module initialized")
except RuntimeError as e:
    logger.error("✗ Error initializing broker: {}".format(e))
    exit(1)


# ========== ENDPOINTS AUDIO (originali) ==========

@app.route("/talk", methods=["POST"])
def talk():
    """Fai parlare NAO"""
    try:
        logger.info("Received request to talk")
        message = request.json.get("message")
        animatedSpeech.say(str(message))
        return jsonify(success=True)
    except Exception as e:
        logger.error("Talk failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/start_listening", methods=["POST"])
def start_listening():
    """Inizia a registrare audio"""
    try:
        logger.info("Starting to listen...")
        AudioCapture.start_listening()
        return jsonify(success=True)
    except Exception as e:
        logger.error("Start listening failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/stop_listening", methods=["POST"])
def stop_listening():
    """Ferma registrazione audio"""
    try:
        logger.info("Stopping listening...")
        AudioCapture.stop_listening()
        return jsonify(success=True)
    except Exception as e:
        logger.error("Stop listening failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/get_audio_chunk", methods=["GET"])
def get_audio_chunk():
    """Ottieni chunk audio"""
    audio_data = AudioCapture.get_audio_chunk()
    if audio_data is not None:
        return audio_data
    else:
        while audio_data is None:
            audio_data = AudioCapture.get_audio_chunk()
            time.sleep(sleep_time)
        return audio_data


@app.route("/get_server_buffer_length", methods=["GET"])
def get_server_buffer_length():
    """Ottieni lunghezza buffer audio"""
    return jsonify(length=len(AudioCapture.buffers))


# ========== NUOVI ENDPOINTS PER AZIONI ==========

@app.route("/action/stand", methods=["POST"])
def action_stand():
    """NAO si alza in piedi"""
    try:
        data = request.json or {}
        speed = data.get("speed", 0.5)
        success, message = nao_actions.stand(speed)
        return jsonify(success=success, message=message)
    except Exception as e:
        logger.error("Action stand failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/action/sit", methods=["POST"])
def action_sit():
    """NAO si siede"""
    try:
        data = request.json or {}
        speed = data.get("speed", 0.5)
        success, message = nao_actions.sit(speed)
        return jsonify(success=success, message=message)
    except Exception as e:
        logger.error("Action sit failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/action/walk", methods=["POST"])
def action_walk():
    """NAO cammina"""
    try:
        data = request.json or {}
        direction = data.get("direction", "forward")  # forward, backward
        distance = data.get("distance", 0.5)
        
        if direction == "forward":
            success, message = nao_actions.walk_forward(distance)
        elif direction == "backward":
            success, message = nao_actions.walk_backward(distance)
        else:
            return jsonify(success=False, error="Invalid direction"), 400
        
        return jsonify(success=success, message=message)
    except Exception as e:
        logger.error("Action walk failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/action/turn", methods=["POST"])
def action_turn():
    """NAO si gira"""
    try:
        data = request.json or {}
        direction = data.get("direction", "left")  # left, right
        angle = data.get("angle", 90)
        
        if direction == "left":
            success, message = nao_actions.turn_left(angle)
        elif direction == "right":
            success, message = nao_actions.turn_right(angle)
        else:
            return jsonify(success=False, error="Invalid direction"), 400
        
        return jsonify(success=success, message=message)
    except Exception as e:
        logger.error("Action turn failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/action/head", methods=["POST"])
def action_head():
    """Muovi la testa di NAO"""
    try:
        data = request.json or {}
        action_type = data.get("type", "look")  # look, nod, shake
        
        if action_type == "look":
            direction = data.get("direction", "center")
            success, message = nao_actions.look_at(direction)
        elif action_type == "nod":
            times = data.get("times", 2)
            success, message = nao_actions.nod_yes(times)
        elif action_type == "shake":
            times = data.get("times", 2)
            success, message = nao_actions.shake_no(times)
        else:
            return jsonify(success=False, error="Invalid head action"), 400
        
        return jsonify(success=success, message=message)
    except Exception as e:
        logger.error("Action head failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/action/wave", methods=["POST"])
def action_wave():
    """NAO saluta con la mano"""
    try:
        data = request.json or {}
        hand = data.get("hand", "Right")
        success, message = nao_actions.wave_hand(hand)
        return jsonify(success=success, message=message)
    except Exception as e:
        logger.error("Action wave failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/action/dance", methods=["POST"])
def action_dance():
    """NAO balla"""
    try:
        success, message = nao_actions.dance()
        return jsonify(success=success, message=message)
    except Exception as e:
        logger.error("Action dance failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/action/celebrate", methods=["POST"])
def action_celebrate():
    """NAO festeggia"""
    try:
        success, message = nao_actions.celebrate()
        return jsonify(success=success, message=message)
    except Exception as e:
        logger.error("Action celebrate failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/action/bow", methods=["POST"])
def action_bow():
    """NAO si inchina"""
    try:
        success, message = nao_actions.bow()
        return jsonify(success=success, message=message)
    except Exception as e:
        logger.error("Action bow failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/action/eyes", methods=["POST"])
def action_eyes():
    """Cambia colore occhi"""
    try:
        data = request.json or {}
        color = data.get("color", "white")
        duration = data.get("duration", 2.0)
        success, message = nao_actions.set_eye_color(color, duration)
        return jsonify(success=success, message=message)
    except Exception as e:
        logger.error("Action eyes failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/action/battery", methods=["GET"])
def action_battery():
    """Ottieni livello batteria"""
    try:
        success, message = nao_actions.get_battery_level()
        return jsonify(success=success, message=message)
    except Exception as e:
        logger.error("Action battery failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/action/execute", methods=["POST"])
def action_execute():
    """
    Endpoint generico per eseguire qualsiasi azione
    Body: {"action": "action_name", "params": {...}}
    """
    try:
        data = request.json
        action_name = data.get("action")
        params = data.get("params", {})
        
        if not action_name:
            return jsonify(success=False, error="No action specified"), 400
        
        # Ottieni il metodo dalla classe NaoActions
        if hasattr(nao_actions, action_name):
            method = getattr(nao_actions, action_name)
            success, message = method(**params)
            return jsonify(success=success, message=message)
        else:
            return jsonify(success=False, error="Action '{}' not found".format(action_name)), 404
    
    except Exception as e:
        logger.error("Action execute failed: {}".format(e))
        return jsonify(success=False, error=str(e)), 500


@app.route("/action/list", methods=["GET"])
def action_list():
    """Lista tutte le azioni disponibili"""
    actions = [
        method for method in dir(nao_actions) 
        if callable(getattr(nao_actions, method)) and not method.startswith("_")
    ]
    return jsonify(actions=actions)


# ========== HEALTH CHECK ==========

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify(
        status="ok",
        audio_buffer_length=len(AudioCapture.buffers),
        actions_available=True
    )


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("NAO Body Server with Actions Starting...")
    logger.info("=" * 50)
    logger.info("NAO IP: {}".format(nao_IP))
    logger.info("Server Port: 5004")
    logger.info("=" * 50)
    
    app.run(host="0.0.0.0", port=5004)
