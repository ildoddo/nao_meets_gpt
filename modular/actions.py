# -*- coding: utf-8 -*-
"""
NAO Robot Actions System - Python 2 Compatible
Gestisce tutti i movimenti e le azioni fisiche del robot NAO
"""

from naoqi import ALProxy
import time
import logging

logger = logging.getLogger(__name__)


class NaoActions:
    """Classe per gestire tutte le azioni fisiche di NAO"""
    
    def __init__(self, nao_ip, nao_port=9559):
        """
        Inizializza i proxy NAOqi necessari
        
        Args:
            nao_ip (str): Indirizzo IP del robot NAO
            nao_port (int): Porta NAOqi (default: 9559)
        """
        self.nao_ip = nao_ip
        self.nao_port = nao_port
        
        try:
            # Proxy per movimenti e posture
            self.motion = ALProxy("ALMotion", nao_ip, nao_port)
            self.posture = ALProxy("ALRobotPosture", nao_ip, nao_port)
            self.animation = ALProxy("ALAnimationPlayer", nao_ip, nao_port)
            self.behavior = ALProxy("ALBehaviorManager", nao_ip, nao_port)
            self.leds = ALProxy("ALLeds", nao_ip, nao_port)
            self.autonomous = ALProxy("ALAutonomousLife", nao_ip, nao_port)
            
            logger.info("✓ NAO Actions initialized successfully")
            
        except Exception as e:
            logger.error("✗ Failed to initialize NAO Actions: {}".format(e))
            raise
    
    # ========== POSTURE (Posizioni Base) ==========
    
    def stand(self, speed=0.5):
        """Metti NAO in piedi"""
        try:
            logger.info("Standing up...")
            self.posture.goToPosture("Stand", speed)
            return True, "Mi sono alzato in piedi"
        except Exception as e:
            logger.error("Stand failed: {}".format(e))
            return False, "Non riesco ad alzarmi: {}".format(e)
    
    def sit(self, speed=0.5):
        """Fai sedere NAO"""
        try:
            logger.info("Sitting down...")
            self.posture.goToPosture("Sit", speed)
            return True, "Mi sono seduto"
        except Exception as e:
            logger.error("Sit failed: {}".format(e))
            return False, "Non riesco a sedermi: {}".format(e)
    
    def crouch(self, speed=0.5):
        """NAO si accuccia"""
        try:
            logger.info("Crouching...")
            self.posture.goToPosture("Crouch", speed)
            return True, "Mi sono accucciato"
        except Exception as e:
            logger.error("Crouch failed: {}".format(e))
            return False, "Non riesco ad accucciarmi: {}".format(e)
    
    def lie_down(self, position="Belly", speed=0.5):
        """NAO si sdraia (Belly o Back)"""
        try:
            posture = "LyingBelly" if position == "Belly" else "LyingBack"
            logger.info("Lying down on {}...".format(position))
            self.posture.goToPosture(posture, speed)
            msg = "Mi sono sdraiato sulla {}".format('pancia' if position == 'Belly' else 'schiena')
            return True, msg
        except Exception as e:
            logger.error("Lie down failed: {}".format(e))
            return False, "Non riesco a sdraiarmi: {}".format(e)
    
    def rest(self):
        """Metti NAO in modalità riposo (motori rilassati)"""
        try:
            logger.info("Entering rest mode...")
            self.motion.rest()
            return True, "Sto riposando, i miei motori sono rilassati"
        except Exception as e:
            logger.error("Rest failed: {}".format(e))
            return False, "Non riesco ad entrare in modalità riposo: {}".format(e)
    
    def wake_up(self):
        """Risveglia NAO dalla modalità riposo"""
        try:
            logger.info("Waking up...")
            self.motion.wakeUp()
            return True, "Mi sono svegliato, sono pronto"
        except Exception as e:
            logger.error("Wake up failed: {}".format(e))
            return False, "Non riesco a svegliarmi: {}".format(e)
    
    # ========== MOVIMENTI BASE ==========
    
    def walk_forward(self, distance=0.5, speed=0.5):
        """Cammina in avanti"""
        try:
            logger.info("Walking forward {}m...".format(distance))
            self.motion.moveTo(distance, 0, 0)
            return True, "Ho camminato in avanti per {} metri".format(distance)
        except Exception as e:
            logger.error("Walk forward failed: {}".format(e))
            return False, "Non riesco a camminare in avanti: {}".format(e)
    
    def walk_backward(self, distance=0.5):
        """Cammina all'indietro"""
        try:
            logger.info("Walking backward {}m...".format(distance))
            self.motion.moveTo(-distance, 0, 0)
            return True, "Ho camminato all'indietro per {} metri".format(distance)
        except Exception as e:
            logger.error("Walk backward failed: {}".format(e))
            return False, "Non riesco a camminare all'indietro: {}".format(e)
    
    def turn_left(self, angle=90):
        """Gira a sinistra (angolo in gradi)"""
        try:
            import math
            radians = angle * math.pi / 180
            logger.info("Turning left {}°...".format(angle))
            self.motion.moveTo(0, 0, radians)
            return True, "Mi sono girato a sinistra di {} gradi".format(angle)
        except Exception as e:
            logger.error("Turn left failed: {}".format(e))
            return False, "Non riesco a girarmi a sinistra: {}".format(e)
    
    def turn_right(self, angle=90):
        """Gira a destra (angolo in gradi)"""
        try:
            import math
            radians = -(angle * math.pi / 180)
            logger.info("Turning right {}°...".format(angle))
            self.motion.moveTo(0, 0, radians)
            return True, "Mi sono girato a destra di {} gradi".format(angle)
        except Exception as e:
            logger.error("Turn right failed: {}".format(e))
            return False, "Non riesco a girarmi a destra: {}".format(e)
    
    def sidestep_left(self, distance=0.3):
        """Passo laterale a sinistra"""
        try:
            logger.info("Sidestepping left {}m...".format(distance))
            self.motion.moveTo(0, distance, 0)
            return True, "Mi sono spostato a sinistra di {} metri".format(distance)
        except Exception as e:
            logger.error("Sidestep left failed: {}".format(e))
            return False, "Non riesco a spostarmi lateralmente: {}".format(e)
    
    def sidestep_right(self, distance=0.3):
        """Passo laterale a destra"""
        try:
            logger.info("Sidestepping right {}m...".format(distance))
            self.motion.moveTo(0, -distance, 0)
            return True, "Mi sono spostato a destra di {} metri".format(distance)
        except Exception as e:
            logger.error("Sidestep right failed: {}".format(e))
            return False, "Non riesco a spostarmi lateralmente: {}".format(e)
    
    # ========== GESTIONE TESTA ==========
    
    def move_head(self, yaw=0.0, pitch=0.0, speed=0.2):
        """
        Muovi la testa
        yaw: rotazione sinistra(-)/destra(+) in radianti (-2.08 a 2.08)
        pitch: su(-)/giù(+) in radianti (-0.67 a 0.52)
        """
        try:
            logger.info("Moving head: yaw={}, pitch={}".format(yaw, pitch))
            self.motion.setAngles(["HeadYaw", "HeadPitch"], [yaw, pitch], speed)
            return True, "Ho mosso la testa"
        except Exception as e:
            logger.error("Move head failed: {}".format(e))
            return False, "Non riesco a muovere la testa: {}".format(e)
    
    def nod_yes(self, times=2):
        """Annuisci (sì)"""
        try:
            logger.info("Nodding yes {} times...".format(times))
            for _ in range(times):
                self.motion.setAngles("HeadPitch", 0.3, 0.3)
                time.sleep(0.3)
                self.motion.setAngles("HeadPitch", -0.3, 0.3)
                time.sleep(0.3)
            self.motion.setAngles("HeadPitch", 0.0, 0.3)
            return True, "Ho annuito"
        except Exception as e:
            logger.error("Nod yes failed: {}".format(e))
            return False, "Non riesco ad annuire: {}".format(e)
    
    def shake_no(self, times=2):
        """Scuoti la testa (no)"""
        try:
            logger.info("Shaking no {} times...".format(times))
            for _ in range(times):
                self.motion.setAngles("HeadYaw", 0.5, 0.3)
                time.sleep(0.3)
                self.motion.setAngles("HeadYaw", -0.5, 0.3)
                time.sleep(0.3)
            self.motion.setAngles("HeadYaw", 0.0, 0.3)
            return True, "Ho scosso la testa"
        except Exception as e:
            logger.error("Shake no failed: {}".format(e))
            return False, "Non riesco a scuotere la testa: {}".format(e)
    
    def look_at(self, direction):
        """Guarda in una direzione (up, down, left, right, center)"""
        try:
            import math
            directions = {
                "up": (0.0, -0.4),
                "down": (0.0, 0.4),
                "left": (0.8, 0.0),
                "right": (-0.8, 0.0),
                "center": (0.0, 0.0)
            }
            
            if direction.lower() not in directions:
                return False, "Direzione non valida: {}".format(direction)
            
            yaw, pitch = directions[direction.lower()]
            logger.info("Looking {}...".format(direction))
            self.motion.setAngles(["HeadYaw", "HeadPitch"], [yaw, pitch], 0.2)
            
            direction_it = {
                "up": "in alto",
                "down": "in basso",
                "left": "a sinistra",
                "right": "a destra",
                "center": "al centro"
            }
            return True, "Sto guardando {}".format(direction_it[direction.lower()])
            
        except Exception as e:
            logger.error("Look at failed: {}".format(e))
            return False, "Non riesco a guardare in quella direzione: {}".format(e)
    
    # ========== GESTIONE BRACCIA ==========
    
    def wave_hand(self, hand="Right"):
        """Saluta con la mano (Right o Left)"""
        try:
            logger.info("Waving {} hand...".format(hand))
            
            arm = "RArm" if hand == "Right" else "LArm"
            shoulder_pitch = "{}ShoulderPitch".format(arm[0])
            shoulder_roll = "{}ShoulderRoll".format(arm[0])
            elbow_roll = "{}ElbowRoll".format(arm[0])
            elbow_yaw = "{}ElbowYaw".format(arm[0])
            wrist_yaw = "{}WristYaw".format(arm[0])
            
            # Alza il braccio
            self.motion.setAngles([shoulder_pitch, shoulder_roll, elbow_roll, elbow_yaw], 
                                 [-1.0, -0.3 if hand == "Right" else 0.3, 1.5, 1.5], 0.3)
            time.sleep(1)
            
            # Muovi la mano per salutare
            for _ in range(3):
                self.motion.setAngles(wrist_yaw, 1.0, 0.5)
                time.sleep(0.3)
                self.motion.setAngles(wrist_yaw, -1.0, 0.5)
                time.sleep(0.3)
            
            # Riporta il braccio giù
            self.motion.setAngles([shoulder_pitch, shoulder_roll, elbow_roll, elbow_yaw, wrist_yaw], 
                                 [1.5, -0.15 if hand == "Right" else 0.15, 0.5, 1.2, 0.0], 0.3)
            
            hand_it = 'destra' if hand == 'Right' else 'sinistra'
            return True, "Ho salutato con la mano {}".format(hand_it)
            
        except Exception as e:
            logger.error("Wave hand failed: {}".format(e))
            return False, "Non riesco a salutare: {}".format(e)
    
    def raise_arms(self, both=True):
        """Alza le braccia"""
        try:
            logger.info("Raising arms...")
            
            if both:
                self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [-1.5, -1.5], 0.3)
                msg = "Ho alzato entrambe le braccia"
            else:
                self.motion.setAngles("RShoulderPitch", -1.5, 0.3)
                msg = "Ho alzato il braccio destro"
            
            return True, msg
            
        except Exception as e:
            logger.error("Raise arms failed: {}".format(e))
            return False, "Non riesco ad alzare le braccia: {}".format(e)
    
    def open_hand(self, hand="Right"):
        """Apri la mano"""
        try:
            logger.info("Opening {} hand...".format(hand))
            hand_proxy = "{}Hand".format('R' if hand == 'Right' else 'L')
            self.motion.setAngles(hand_proxy, 1.0, 0.3)
            hand_it = 'destra' if hand == 'Right' else 'sinistra'
            return True, "Ho aperto la mano {}".format(hand_it)
        except Exception as e:
            logger.error("Open hand failed: {}".format(e))
            return False, "Non riesco ad aprire la mano: {}".format(e)
    
    def close_hand(self, hand="Right"):
        """Chiudi la mano"""
        try:
            logger.info("Closing {} hand...".format(hand))
            hand_proxy = "{}Hand".format('R' if hand == 'Right' else 'L')
            self.motion.setAngles(hand_proxy, 0.0, 0.3)
            hand_it = 'destra' if hand == 'Right' else 'sinistra'
            return True, "Ho chiuso la mano {}".format(hand_it)
        except Exception as e:
            logger.error("Close hand failed: {}".format(e))
            return False, "Non riesco a chiudere la mano: {}".format(e)
    
    # ========== ANIMAZIONI COMPLESSE ==========
    
    def dance(self):
        """Balla!"""
        try:
            logger.info("Dancing...")
            # Cerca comportamenti di danza disponibili
            behaviors = self.behavior.getInstalledBehaviors()
            dance_behaviors = [b for b in behaviors if 'dance' in b.lower() or 'balla' in b.lower()]
            
            if dance_behaviors:
                self.behavior.runBehavior(dance_behaviors[0])
                return True, "Sto ballando!"
            else:
                # Danza semplice personalizzata
                for _ in range(2):
                    self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [-1.0, -1.0], 0.5)
                    time.sleep(0.5)
                    self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.0, 1.0], 0.5)
                    time.sleep(0.5)
                return True, "Ho fatto una piccola danza!"
            
        except Exception as e:
            logger.error("Dance failed: {}".format(e))
            return False, "Non riesco a ballare: {}".format(e)
    
    def celebrate(self):
        """Festeggia (braccia in alto)"""
        try:
            logger.info("Celebrating...")
            
            # Alza le braccia velocemente
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch", 
                                  "LShoulderRoll", "RShoulderRoll"], 
                                 [-1.5, -1.5, 0.3, -0.3], 0.8)
            time.sleep(0.5)
            
            # Muovile su e giù
            for _ in range(2):
                self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], 
                                     [-1.2, -1.2], 0.8)
                time.sleep(0.3)
                self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], 
                                     [-1.5, -1.5], 0.8)
                time.sleep(0.3)
            
            # Torna alla posizione normale
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch", 
                                  "LShoulderRoll", "RShoulderRoll"], 
                                 [1.5, 1.5, 0.15, -0.15], 0.3)
            
            return True, "Sto festeggiando! Evviva!"
            
        except Exception as e:
            logger.error("Celebrate failed: {}".format(e))
            return False, "Non riesco a festeggiare: {}".format(e)
    
    def bow(self):
        """Inchino"""
        try:
            logger.info("Bowing...")
            
            # Piega in avanti
            self.motion.setAngles("HeadPitch", 0.5, 0.2)
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.2)
            time.sleep(1.5)
            
            # Torna su
            self.motion.setAngles("HeadPitch", 0.0, 0.2)
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.5, 1.5], 0.2)
            
            return True, "Mi sono inchinato"
            
        except Exception as e:
            logger.error("Bow failed: {}".format(e))
            return False, "Non riesco a inchinarmi: {}".format(e)
    
    def think(self):
        """Posa pensierosa"""
        try:
            logger.info("Thinking pose...")
            
            # Mano sul mento (approssimazione)
            self.motion.setAngles(["RShoulderPitch", "RElbowRoll"], [0.3, 1.5], 0.3)
            self.motion.setAngles("HeadPitch", 0.3, 0.2)
            time.sleep(2)
            
            # Torna normale
            self.motion.setAngles(["RShoulderPitch", "RElbowRoll"], [1.5, 0.5], 0.3)
            self.motion.setAngles("HeadPitch", 0.0, 0.2)
            
            return True, "Sto pensando..."
            
        except Exception as e:
            logger.error("Think failed: {}".format(e))
            return False, "Non riesco a fare la posa pensierosa: {}".format(e)
    
    # ========== LED E OCCHI ==========
    
    def set_eye_color(self, color="white", duration=2.0):
        """
        Cambia colore degli occhi
        Colori: white, red, green, blue, yellow, magenta, cyan
        """
        try:
            colors = {
                "white": (1.0, 1.0, 1.0),
                "red": (1.0, 0.0, 0.0),
                "green": (0.0, 1.0, 0.0),
                "blue": (0.0, 0.0, 1.0),
                "yellow": (1.0, 1.0, 0.0),
                "magenta": (1.0, 0.0, 1.0),
                "cyan": (0.0, 1.0, 1.0)
            }
            
            if color.lower() not in colors:
                return False, "Colore non valido: {}".format(color)
            
            r, g, b = colors[color.lower()]
            logger.info("Setting eye color to {}...".format(color))
            
            # Imposta colore RGB per entrambi gli occhi
            self.leds.fadeRGB("FaceLeds", r, g, b, duration)
            
            color_names = {
                "white": "bianco",
                "red": "rosso",
                "green": "verde",
                "blue": "blu",
                "yellow": "giallo",
                "magenta": "magenta",
                "cyan": "ciano"
            }
            
            return True, "I miei occhi sono ora {}".format(color_names[color.lower()])
            
        except Exception as e:
            logger.error("Set eye color failed: {}".format(e))
            return False, "Non riesco a cambiare colore degli occhi: {}".format(e)
    
    def blink(self, times=3):
        """Batti le palpebre (simulato con LED)"""
        try:
            logger.info("Blinking {} times...".format(times))
            for _ in range(times):
                self.leds.off("FaceLeds")
                time.sleep(0.1)
                self.leds.on("FaceLeds")
                time.sleep(0.3)
            return True, "Ho battuto le palpebre"
        except Exception as e:
            logger.error("Blink failed: {}".format(e))
            return False, "Non riesco a battere le palpebre: {}".format(e)
    
    # ========== STATO E INFORMAZIONI ==========
    
    def get_battery_level(self):
        """Ottieni livello batteria"""
        try:
            battery = ALProxy("ALBattery", self.nao_ip, self.nao_port)
            level = battery.getBatteryCharge()
            logger.info("Battery level: {}%".format(level))
            return True, "La mia batteria è al {}%".format(level)
        except Exception as e:
            logger.error("Get battery failed: {}".format(e))
            return False, "Non riesco a leggere il livello della batteria"
    
    def get_temperature(self):
        """Ottieni temperatura dei motori"""
        try:
            temps = self.motion.getTemperatures("Head")
            avg_temp = sum(temps) / len(temps)
            logger.info("Temperature: {}°C".format(avg_temp))
            return True, "La mia temperatura è di circa {:.1f} gradi".format(avg_temp)
        except Exception as e:
            logger.error("Get temperature failed: {}".format(e))
            return False, "Non riesco a leggere la temperatura"
    
    def enable_autonomous_life(self):
        """Abilita vita autonoma (movimenti casuali)"""
        try:
            logger.info("Enabling autonomous life...")
            self.autonomous.setState("solitary")
            return True, "Ho attivato la modalità autonoma"
        except Exception as e:
            logger.error("Enable autonomous failed: {}".format(e))
            return False, "Non riesco ad attivare la modalità autonoma"
    
    def disable_autonomous_life(self):
        """Disabilita vita autonoma"""
        try:
            logger.info("Disabling autonomous life...")
            self.autonomous.setState("disabled")
            return True, "Ho disattivato la modalità autonoma"
        except Exception as e:
            logger.error("Disable autonomous failed: {}".format(e))
            return False, "Non riesco a disattivare la modalità autonoma"
