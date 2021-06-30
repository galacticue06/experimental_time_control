import logging
import psutil
import GPUtil

logger = logging.getLogger(__name__)

enabled = True

def pr(n):
    for i in range(2,int(n**(1/2))+1):
        if n%i==0:
            return False
    return (True if n>1 else False)

def get_size(bytes, suffix):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return "{:.2f} {}{}".format(bytes,unit,suffix)
        bytes /= factor

class Conversation:
    def __init__(self, game, engine, xhr, version, challenge_queue):
        self.game = game
        self.engine = engine
        self.xhr = xhr
        self.version = version
        self.challengers = challenge_queue

    command_prefix = "!"

    def react(self, line, game):
        logger.info("*** {} [{}] {}: {}".format(self.game.url(), line.room, line.username, line.text.encode("utf-8")))
        if (line.text[0] == self.command_prefix):
            self.command(line, game, line.text[1:].lower())

    def command(self, line, game, cmd):
        cmds = cmd.split(":")
        cmd = cmds[0]
        if cmd == "commands" or cmd == "help":
            self.send_reply(line, "Supported commands: !wait, !name, !eval, !usage")
        elif cmd == "wait" and game.is_abortable():
            game.ping(60, 120)
            self.send_reply(line, "Waiting 60 seconds...")
        elif cmd == "name":
            name = game.me.name
            self.send_reply(line, "{} running {}".format(name, self.engine.name()))
        elif cmd == "eval":
            stats = self.engine.get_stats()
            self.send_reply(line, ", ".join(stats))
        elif cmd == "state":
            try:
                stats = self.engine.get_stats()[score]
                if stats > 100:
                    self.send_reply(line, "Winning")
                elif stats < -100:
                    self.send_reply(line, "Losing")
                else:
                    self.send_reply(line, "Draw")
            except:
                pass
        elif cmd == "usage":
            cmds[1] = cmds[1].upper()
            if cmds[1] == "CPU":
                self.send_reply(line, f"CPU Usage: {psutil.cpu_percent()}%")
            elif cmds[1] == "CPU_FREQ":
                cpufreq = psutil.cpu_freq()
                self.send_reply(line, f"CPU Frequency: {cpufreq.current}Mhz")
            elif cmds[1] == "GPU":
                gpu = GPUtil.getGPUs()[0]
                self.send_reply(line, f"GPU Usage: {gpu.load*100}%")
            elif cmds[1] == "RAM":
                svmem = psutil.virtual_memory()
                self.send_reply(line, "RAM Usage: {}".format(get_size(svmem.used,"B")))
            else:
                self.send_reply(line, f"No identifier found: {cmds[1]}")


    def send_reply(self, line, reply):
        self.xhr.chat(self.game.id, line.room, reply)


class ChatLine:
    def __init__(self, json):
        self.room = json.get("room")
        self.username = json.get("username")
        self.text = json.get("text")
