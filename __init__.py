#!/usr/bin/env python
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from nanoleaf import Aurora #https://github.com/bharat/nanoleaf
from nanoleaf import setup
import time
from time import sleep
from colour import Color
import math
import re
import configparser


__author__ = 'PCWii'

# Logger: used for debug lines, like "LOGGER.debug(xyz)". These
# statements will show up in the command line when running Mycroft.
LOGGER = getLogger(__name__)

# List each of the bulbs here

Valid_Color = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet', 'purple', 'white']

# The logic of each skill is contained within its own class, which inherits
# base methods from the MycroftSkill class with the syntax you can see below:
# "class ____Skill(MycroftSkill)"
class NanoLeafSkill(MycroftSkill):

    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(NanoLeafSkill, self).__init__(name="NanoLeafSkill")
        self.settings["ipstring"] = ""
        self.settings["tokenstring"] = ""
        self._is_setup = False

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


    # The "handle_xxxx_intent" functions define Mycroft's behavior when
    # each of the skill's intents is triggered: in this case, he simply
    # speaks a response. Note that the "speak_dialog" method doesn't
    # actually speak the text it's passed--instead, that text is the filename
    # of a file in the dialog folder, and Mycroft speaks its contents when
    # the method is called.
    def on_websettings_changed(self):
        if not self._is_setup:
            IPstring = self.settings.get("ipstring", "")
            tokenString = self.settings.get("tokenstring", "")
            try:
                if IPstring and tokenString:
                    IPstring = self.settings["ipstring"]
                    tokenString = self.settings["tokenstring"]
                    self._is_setup = True
            except Exception as e:
                LOG.error(e)

    def handle_nano_leaf_get_token_intent(self, message):
        #iniFile = "kelsey.ini"
        #cfgfile = open(iniFile, 'w')
        try:
            token = setup.generate_auth_token(self.settings["ipstring"])
        except:
            token = "Not Found"
            self.speak("The Token Was Not Found!")
        #kelsey_ini = configparser.ConfigParser()
        #kelsey_ini.add_section('Aurora')
        #kelsey_ini.set('Aurora', 'Token', str(token))
        #kelsey_ini.set('Aurora', 'Layout', "35,216,214,157,5,112,124")
        #time.ctime()  # 'Mon Oct 18 13:35:29 2010'
        #tokenTime = time.strftime('%l:%M%p %Z on %b %d, %Y')
        #kelsey_ini.set('Aurora', 'Time', tokenTime)
        #kelsey_ini.write(cfgfile)
        #cfgfile.close()
        self.settings.set('tokenstring', str(token))
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
                myRed = math.trunc(Color(findcolor).get_red() * 255)
                myGreen = math.trunc(Color(findcolor).get_green() * 255)
                myBlue = math.trunc(Color(findcolor).get_blue() * 255)
                self.speak_dialog("light.set", data ={"result": findcolor})
                break
        dim_level = re.findall('\d+', str_remainder)
        if dim_level:
            myPanels = Aurora(IPstring, tokenString)
            MyPanels.brightness = int(dim_level[0])
            self.speak_dialog("light.set", data={"result": str(dim_level[0])+ ", percent"})

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
