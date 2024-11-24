from typing import Dict, Optional

from .response import *
from .actions import *
from .triggers import *


HUG_POSSIBILITIES = [
    "heheehehehe {0} hugs {1} < 3 < 3 <  ##<#,3,33<#3,#3,,3,3,#<...",
    "{0} squeezes {1} tightly.",
    "{0} wraps their arms around {1}'s",
    "{0} puts their arms around {1} and holds them tightly, because {0} likes {1} or is pleased to see {1}",
    "{0} holds {1} close to their body.",
    "{0} clasps {1} tightly in their arms.",
    "{0} wraps their arms around {1}'s back in a warm embrace",
    "{0} holds {1} close to their body, likely to show that they like, love, or value them.",
    "{0} squeezes {1} tightly, probably to express affection.",
    "{0} is trapped with {1}'s arms wrapped around their back.",
    "{0} sneaks up from behind {1} and puts their arms around {1}'s waist."
]

PAT_POSSIBILITIES = [
    "{0} softly strokes {1}'s head as a sign of affection.",
    "{1} smiled, slightly blushing, as {0} playfully taps {1}'s head.",
    "{0} lets out a quiet purr as {1}'s fingers gently scratches {0}'s head.",
    "{1} timidly placed {0}'s hand on their head.",
    "{0} reaches over and lightly taps {1}'s head.",
    "{0} gently strokes {1}'s head.",
    "{0} moves their hand over to {1}'s head and gave it a pleasure feeling.",
    "{0} runs their finger through {1}'s hair, lightly scratches {1}'s head and caressing their hair strands.",
    "{1} timidly placed {0}'s hand on their head while blushing intensely."
]

CLICK_POSSIBILTIES = [
    f"{0} clicks {1}."
]

def get_all_states() -> Dict[str, str]:
    """
    Returns all the state for all responses
    :return: A dictionary of the form {response name: response state}
    """
    return {x.name: x.get_state() for x in responses}


def get_all_enabled() -> Dict[str, bool]:
    """
    Returns whether all responses are enabled.
    :return: A dictionary of the form {response name: response enabled?}
    """
    return {x.name: x.enabled for x in responses}


def set_all_states(states: Dict[str, str]):
    """
    Sets the state of all responses to the specified.
    Any response not listed will be unchanged.
    A failure to set the state will fail silently.
    :param states: A dictionary of the form {response name: response state}
    :return: Nothing
    """
    for r in responses:
        try:
            r.set_state(states[r.name])
        except ValueError:
            pass
        except KeyError:
            pass


def set_all_enabled(states: Dict[str, bool]):
    """
    Enables/disables all responses to the specified.
    Any response not listed will be unchanged.
    :param states: A dictionary of the form {response name: response enable?}
    :return: Nothing
    """
    for r in responses:
        try:
            r.enabled = states[r.name]
        except KeyError:
            pass


def get_response_by_name(name: str) -> Optional[Response]:
    """
    Returns the given response with the given name, or None if the given Response doesn't exist.
    :param name: The name of the Response.
    :return: The Response, or None if it was not found.
    """
    for i in responses:
        if i.name.lower() == name.lower():
            return i


thanks_bot = SendOrReactResponse(
    OrTrigger(
        LiteralsTrigger(["thanks bot", "good bot"], contains=True, case_sensitive=False),
        AndTrigger(
            LiteralsTrigger(["thank"], contains=True, case_sensitive=False),
            OrTrigger(
                MentionsTrigger(587652588019908629),
                LastAuthorTrigger(587652588019908629),
                LiteralsTrigger(["amadeus"], contains=True, case_sensitive=False)
            )
        )
    ),
    "<a:kurisuthumbsup:1127702351252303892>", 1127702351252303892,
    "Thanks Bot"
)

bad_bot = SendOrReactResponse(
    OrTrigger(
        LiteralsTrigger(["bad bot", "stupid bot"], contains=True, case_sensitive=False),
        AndTrigger(
            LiteralsTrigger(["shut", "bad", "stupid", "kys"], contains=True, case_sensitive=False),
            OrTrigger(
                MentionsTrigger(587652588019908629),
                LastAuthorTrigger(587652588019908629),
                LiteralsTrigger(["amadeus"], contains=True, case_sensitive=False)
            )
        )
    ),
    "<a:kurisucry:1127702202203521044>", 1127702202203521044,
    "Bad Bot"
)

cool_bot = SendOrReactResponse(
    OrTrigger(
        LiteralsTrigger(["epic bot", "cool bot"], contains=True, case_sensitive=False),
        AndTrigger(
            LiteralsTrigger(["epic", "cool", "poggers"], contains=True, case_sensitive=False),
            OrTrigger(
                MentionsTrigger(587652588019908629),
                LastAuthorTrigger(587652588019908629),
                LiteralsTrigger(["amadeus"], contains=True, case_sensitive=False)
            )
        )
    ),
    "<a:kurisucool:1127705480471519243>", 1127705480471519243,
    "Cool Bot"
)

dad_bot = RandomChanceResponse(
    RegexTrigger(r"^.*( |^)i['‘ʼ’]?m (.+)"),
    RegexSendAction(r"^.*( |^)i['‘ʼ’]?m (.+)", r"Hi \2, I'm dad!"),
    "Dad Bot"
)

nicu = Response(
    LiteralsTrigger(["nicu"], contains=True, case_sensitive=False),
    LiteralSendAction("nicu nicu\nvery nicu shiza-chan"),
    "Nicu"
)

nullpo = Response(
    LiteralsTrigger(["nullpo"], contains=True, case_sensitive=False),
    LiteralSendAction("gah!"),
    "Nullpo"
)

amadeus = Response(
    OrTrigger(
        RegexTrigger(r"^amadeus*"),
        MentionsTrigger(587652588019908629)
    ),
    RandomLiteralAction(["uwu", "?", "hey", "waddup", lambda x: x.author.nick or x.author.name]),
    "Amadeus"
)

cyanide = SendOrReactResponse(
    LiteralsTrigger(["cyanide", "cyan", "cya", "see you" "see ya"]),
    "cyanide <a:rinwave:1127698005034807420>", 1127698005034807420,
    "Cyanide"
)

hug = Response(
    RegexTrigger(r"^\.hug*"),
    SendRandomActionEmbedAction(HUG_POSSIBILITIES),
    ".hug"
)

pat = Response(
    RegexTrigger(r"^\.pat*"),
    SendRandomActionEmbedAction(PAT_POSSIBILITIES),
    ".pat"
)

meow = RandomChanceResponse(
    ChannelCooldownTrigger(5, RegexTrigger(r"m[re]+o+w+~*")),
    EvaluateStringAction(lambda x: x.content),
    "meow"
)


responses = [thanks_bot, bad_bot, cool_bot, dad_bot, nicu, nullpo, amadeus, cyanide, hug, pat, meow]
