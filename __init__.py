#!/usr/bin/env python
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from yeelight import Bulb
from time import sleep
from colour import Color
import math
import re


__author__ = 'PCWii'

# Logger: used for debug lines, like "LOGGER.debug(xyz)". These
# statements will show up in the command line when running Mycroft.
LOGGER = getLogger(__name__)

# List each of the bulbs here
seq_delay = 0.5
effect_delay = 3000

bulbRHS = Bulb("192.168.0.50")
bulbLHS = Bulb("192.168.0.51")
Valid_Color = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet', 'purple', 'white']

# The logic of each skill is contained within its own class, which inherits
# base methods from the MycroftSkill class with the syntax you can see below:
# "class ____Skill(MycroftSkill)"
class YeeLightSkill(MycroftSkill):

    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(YeeLightSkill, self).__init__(name="YeeLightSkill")

    # This method loads the files needed for the skill's functioning, and
    # creates and registers each intent that the skill uses
    def initialize(self):
        self.load_data_files(dirname(__file__))

        yee_light_on_intent = IntentBuilder("YeeLightOnIntent").\
            require("DeviceKeyword").require("OnKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(yee_light_on_intent, self.handle_yee_light_on_intent)

        yee_light_off_intent = IntentBuilder("YeeLightOffIntent").\
            require("DeviceKeyword").require("OffKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(yee_light_off_intent, self.handle_yee_light_off_intent)

        yee_light_dim_intent = IntentBuilder("YeeLightDimIntent").\
            require("DimKeyword").require("DeviceKeyword").\
            optionally("LightKeyword").build()
        self.register_intent(yee_light_dim_intent, self.handle_yee_light_dim_intent)

        yee_light_set_intent = IntentBuilder("YeeLightSetIntent").\
            require("SetKeyword").require("DeviceKeyword").\
            optionally("Lightkeyword").build()
        self.register_intent(yee_light_set_intent, self.handle_yee_light_set_intent)


    # The "handle_xxxx_intent" functions define Mycroft's behavior when
    # each of the skill's intents is triggered: in this case, he simply
    # speaks a response. Note that the "speak_dialog" method doesn't
    # actually speak the text it's passed--instead, that text is the filename
    # of a file in the dialog folder, and Mycroft speaks its contents when
    # the method is called.
    def handle_yee_light_on_intent(self, message):
        bulbRHS.turn_on()
        sleep(seq_delay)
        bulbLHS.turn_on()
        sleep(seq_delay)
        bulbLHS.set_rgb(255, 255, 255)
        sleep(seq_delay)
        bulbRHS.set_rgb(255, 255, 255)
        sleep(seq_delay)
        bulbRHS.set_brightness(100, duration=effect_delay)
        sleep(seq_delay)
        bulbLHS.set_brightness(100, duration=effect_delay)
        self.speak_dialog("light.on")

    def handle_yee_light_off_intent(self, message):
        bulbRHS.turn_off(duration=effect_delay)
        sleep(seq_delay)
        bulbLHS.turn_off(duration=effect_delay)
        self.speak_dialog("light.off")

    def handle_yee_light_dim_intent(self, message):
        bulbRHS.set_brightness(5, duration=effect_delay)
        sleep(seq_delay)
        bulbLHS.set_brightness(5, duration=effect_delay)
        self.speak_dialog("light.dim")

    def handle_yee_light_set_intent(self, message):
        str_remainder = str(message.utterance_remainder())
        for findcolor in Valid_Color:
            mypos = str_remainder.find(findcolor)
            if mypos > 0:
                myRed = math.trunc(Color(findcolor).get_red() * 255)
                myGreen = math.trunc(Color(findcolor).get_green() * 255)
                myBlue = math.trunc(Color(findcolor).get_blue() * 255)
                bulbLHS.set_rgb(myRed, myGreen, myBlue)
                sleep(seq_delay)
                bulbRHS.set_rgb(myRed, myGreen, myBlue)
                self.speak_dialog("light.set", data ={"result": findcolor})
                break
        dim_level = re.findall('\d+', str_remainder)
        if dim_level:
            bulbLHS.set_brightness(int(dim_level[0]), duration=effect_delay)
            sleep(seq_delay)
            bulbRHS.set_brightness(int(dim_level[0]), duration=effect_delay)
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
    return YeeLightSkill()
