#!/usr/bin/env python
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.util.log import LOG

from nanoleaf import Aurora #https://github.com/pcwii/nanoleaf.git
from nanoleaf import setup

import threading
import socket
from time import sleep
from colour import Color
import math
import re


__author__ = 'PCWii'

# Logger: used for debug lines, like "LOGGER.debug(xyz)". These
# statements will show up in the command line when running Mycroft.
LOGGER = getLogger(__name__)

# List each of the bulbs here
Valid_Color = ['red', 'read', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet', 'purple', 'white']


class NanoLeafSkill(MycroftSkill):
    class NewThread:
        id = 0
        idStop = False
        idThread = threading.Thread

    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(NanoLeafSkill, self).__init__(name="NanoLeafSkill")
        self.settings["ipstring"] = ""
        self.settings["tokenstring"] = ""
        self._is_setup = False
        self.cinema_mode = self.NewThread
        self.IPstring = ""
        self.tokenString = ""
        self.UDP_IP = "192.168.0.251"  # This should be the IP address of the machine the code is running on (mycroft)
        self.UDP_PORT = 20450

    # This method loads the files needed for the skill's functioning, and
    # creates and registers each intent that the skill uses
    def initialize(self):
        self.load_data_files(dirname(__file__))
        # Check and then monitor for credential changes
        self.settings.set_changed_callback(self.on_websettings_changed)
        self.on_websettings_changed()

        nano_leaf_on_intent = IntentBuilder("NanoLeafOnIntent").\
            require("DeviceKeyword").require("OnKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(nano_leaf_on_intent, self.handle_nano_leaf_on_intent)

        nano_leaf_off_intent = IntentBuilder("NanoLeafOffIntent").\
            require("DeviceKeyword").require("OffKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(nano_leaf_off_intent, self.handle_nano_leaf_off_intent)

        nano_leaf_dim_intent = IntentBuilder("NanoLeafDimIntent").\
            require("DimKeyword").require("DeviceKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(nano_leaf_dim_intent, self.handle_nano_leaf_dim_intent)

        nano_leaf_set_intent = IntentBuilder("NanoLeafSetIntent").\
            require("SetKeyword").require("DeviceKeyword").\
            optionally("Lightkeyword").build()
        self.register_intent(nano_leaf_set_intent, self.handle_nano_leaf_set_intent)

        nano_leaf_get_token_intent = IntentBuilder("NanoLeafGetTokenIntent").\
            require('GetKeyword').require("DeviceKeyword").\
            require('TokenKeyword').build()
        self.register_intent(nano_leaf_get_token_intent, self.handle_nano_leaf_get_token_intent)

    def on_websettings_changed(self):
        if not self._is_setup:
            self.IPstring = self.settings.get("ipstring", "")
            self.tokenString = self.settings.get("tokenstring", "")
            try:
                if self.IPstring and self.tokenString:
                    self.IPstring = self.settings["ipstring"]
                    self.tokenString = self.settings["tokenstring"]
                    self._is_setup = True
            except Exception as e:
                LOG.error(e)

    def get_panels(self):
        MyPanels = Aurora(self.IPstring, self.tokenString)
        MyPanelIDs = [x['panelId'] for x in
                      MyPanels.panel_positions]  # retreive nanoleaf panel ID's for information only
        LOG.info(MyPanelIDs)
        return MyPanelIDs

    def do_cinema_mode(self, my_id, terminate):
        LOG.info("Starting Nanoleaf Cinema Mode", my_id)
        #Todo Update the Code here
        my_panels = self.get_panels()
        PanelIDs = my_panels[1:-1]
        lower_panel = my_panels[0]
        upper_panel = my_panels[len(my_panels) - 1]
        first_panel = PanelIDs[0]
        last_panel = PanelIDs[len(PanelIDs) - 1]
        LOG.info(my_panels)
        LOG.info(lower_panel)
        LOG.info(first_panel)
        LOG.info(upper_panel)
        LOG.info(last_panel)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        sock.bind((self.UDP_IP, self.UDP_PORT))
        my_aurora = Aurora(self.IPstring, self.tokenString)  # IP address and key for nanoleaf Aurora
        my_aurora.on = True  # Turn nanoleaf on
        my_aurora.brightness = 50  # set brightness
        sleep(1)
        strm = my_aurora.effect_stream()  # set nanoleaf to streaming mode
        while True:
            raw_data = sock.recvfrom(21)  # hyperion sends 3 bytes (R,G,B) for each configured light (3*7=21)
            byte_data = bytearray(raw_data[0])  # retrieve hyperion byte array
            RGBList = list(byte_data)  # great R-G-B list
            LOG.info(RGBList)  # for debuging only
            PanelCount = 0  # initial condition
            for Panel in PanelIDs:  # itterate through the configured PanleID's above
                # Todo - Determine if I can use Panel instead of PanelID's
                # Todo - If we can use Panel then the PanelCount should not be required
                LOG.info('Panel: ' + str(Panel) + " - Panel ID:" + str(PanelIDs[PanelCount]))
                firstByteIndex = PanelCount * 3  # Red Index
                secondByteIndex = firstByteIndex + 1  # Green Index
                thirdByteIndex = secondByteIndex + 1  # Blue Index
                intPanelID = PanelIDs[PanelCount]  # This Panel ID ***could this not just be "Panel"
                intRedValue = RGBList[firstByteIndex]
                intGreenValue = RGBList[secondByteIndex]
                intBlueValue = RGBList[thirdByteIndex]
                if intPanelID == lower_panel or intPanelID == first_panel:  # condition to handle two panels on the same vertical axis, or configure hyperion to drive this as well
                    strm.panel_set(lower_panel, intRedValue, intGreenValue, intBlueValue)
                    strm.panel_set(first_panel, intRedValue, intGreenValue, intBlueValue)
                else:
                    if intPanelID == upper_panel or intPanelID == last_panel:  # condition to handle two panels on the same vertical axis, or configure hyperion to drive this as well
                        strm.panel_set(upper_panel, intRedValue, intGreenValue, intBlueValue)
                        strm.panel_set(last_panel, intRedValue, intGreenValue, intBlueValue)
                    else:
                        strm.panel_set(intPanelID, intRedValue, intGreenValue,
                                       intBlueValue)  # set the current panel color
                PanelCount += 1  # next panel
            if terminate():
                LOG.info('Stop Signal Received')
                break
        LOG.info("Nanoleaf Cinema Mode Ended", my_id)

    @intent_handler(IntentBuilder('StartCinemaModeIntent').require('StartKeyword').require('DeviceKeyword').
                    require('CinemaKeyword').build())
    def handle_start_cinema_mode_intent(self, message):
        self.cinema_mode.idStop = False
        self.cinema_mode.id = 101
        self.cinema_mode.idThread = threading.Thread(target=self.do_cinema_mode, args=(self.cinema_mode.id,
                                                                             lambda: self.cinema_mode.idStop))
        self.cinema_mode.idThread.start()

    @intent_handler(IntentBuilder('StopCinemaModeIntent').require('StartKeyword').require('DeviceKeyword').
                    require('CinemaKeyword').build())
    def handle_stop_cinema_mode_intent(self, message):
        self.cinema_mode.id = 101
        self.cinema_mode.idStop = True
        self.cinema_mode.idThread.join()

    def handle_nano_leaf_get_token_intent(self, message):
        # retrieve the token from the nanoleaf
        try:
            token = setup.generate_auth_token(self.settings["ipstring"])
        except:
            token = "Not Found"
            self.speak("The Token Was Not Found!")
        self.settings["tokenstring"] = str(token)
        if token != "Not Found":
            self.speak('I have retrieved a new token')

    def handle_nano_leaf_on_intent(self, message):
        IPstring = self.settings["ipstring"]
        tokenString = self.settings["tokenstring"]
        MyPanels = Aurora(IPstring, tokenString)
        MyPanels.on = True
        MyPanels.brightness = 100
        self.speak_dialog("light.on")

    def handle_nano_leaf_off_intent(self, message):
        IPstring = self.settings["ipstring"]
        tokenString = self.settings["tokenstring"]
        MyPanels = Aurora(IPstring, tokenString)
        MyPanels.on = False
        self.speak_dialog("light.off")

    def handle_nano_leaf_dim_intent(self, message):
        IPstring = self.settings["ipstring"]
        tokenString = self.settings["tokenstring"]
        MyPanels = Aurora(IPstring, tokenString)
        MyPanels.brightness = 5
        self.speak_dialog("light.dim")

    def handle_nano_leaf_set_intent(self, message):
        IPstring = self.settings["ipstring"]
        tokenString = self.settings["tokenstring"]
        str_remainder = str(message.utterance_remainder())
        for findcolor in Valid_Color:
            mypos = str_remainder.find(findcolor)
            if mypos > 0:
                if findcolor == 'read':
                    findcolor = 'red'
                myRed = math.trunc(Color(findcolor).get_red() * 255)
                myGreen = math.trunc(Color(findcolor).get_green() * 255)
                myBlue = math.trunc(Color(findcolor).get_blue() * 255)
                myHex = Color(findcolor).hex_l
                self.speak_dialog("light.set", data ={"result": findcolor})
                MyPanels = Aurora(IPstring, tokenString)
                MyPanels.rgb = myHex[1:]
                break
        dim_level = re.findall('\d+', str_remainder)
        if dim_level:
            MyPanels = Aurora(IPstring, tokenString)
            MyPanels.brightness = int(dim_level[0])
            self.speak_dialog("light.set", data={"result": str(dim_level[0]) + ", percent"})

    # The "stop" method defines what Mycroft does when told to stop during
    # the skill's execution. In this case, since the skill's functionality
    # is extremely simple, the method just contains the keyword "pass", which
    # does nothing.
    def stop(self):
        pass

# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return NanoLeafSkill()
