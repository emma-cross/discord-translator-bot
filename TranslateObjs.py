from translate import IsValidLanguage

class TranslateChannel:
    def __init__(self, cid, language):
        self.cid = cid
        self.language = language

    def __eq__(self, other_cid):
        return self.cid == other_cid

    def getID(self):
        return int(self.cid.strip("<").strip(">").strip("#"))

class TranslateServer:
    def __init__(self, name):
        self.name = name
        self.file = "servers/" + name.replace(" ", "_") + ".txt"
        self.channels = []
        self.read()

    def __eq__(self, other_name):
        return self.name == other_name

    def read(self):
        try:
            # try to open file
            file = open(self.file, "r")
            if file:
                while True:
                    line = file.readline().strip("\n\r")
                    if "" == line: break
                    tokens = line.split(" ")
                    if len(tokens) >= 2:
                        self.registerChannel(TranslateChannel(tokens[0], tokens[1]))
                file.close()
        except FileNotFoundError:
            # not a problem - will eventually make a file when channels are registered
            None

    def write(self):
        file = open(self.file, "w")
        if file:
            for channel in self.channels:
                file.write(f"{channel.cid} {channel.language}\n")
            file.close()
    
    def registerChannel(self, channel):
        if channel.cid in self.channels:
            # update existing channel registry 
            self.channels[self.channels.index(channel.cid)] = channel
        else:
            # check that the given language is valid
            if IsValidLanguage(channel.language):
                #@todo check that language hasnt been registered already
                # register new channel
                self.channels.append(channel)
                return 0
            else:
                # invalid/unknown language entered
                return -1

    def unregisterChannel(self, cid):
        # unregister channel
        self.channels.remove(cid)
