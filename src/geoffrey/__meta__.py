# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from collections import namedtuple

# Developer definition.
# AFAIK: A human being capable of turn pizza & coke into code.
Developer = namedtuple("Developer", ("name", "email"))


__all__ = [
    "__packagename__",
    "__version__",
    "__summary__",
    "__url__",
    "__author__",
    "__email__",
    "__license__"
]

DEVELOPERS = {
    "nilp0inter": Developer("Roberto Abdelkader Martínez Pérez",
                            "robertomartinezp@gmail.com"),
    "mreguero": Developer("Miguel Reguero Bejar",
                           "mreguerob0@gmail.com"),
    "rrequero": Developer("Raul Requero",
                          "rareq1987@gmail.com"),
    "jdgg1983": Developer("Juan Diego Gonzalez Gallardo",
                          "jdgg1983@gmail.com"),
}

__packagename__ = "geoffrey"
__version__ = "0.1.2"
__summary__ = "Geoffrey: Real Time Continuous Integration Server"
__keywords__ = "geoffrey continuous integration server"
__url__ = "https://github.com/nilp0inter/geoffrey"
__author__ = ", ".join(dev.name for dev in DEVELOPERS.values())
__email__ = ", ".join(dev.email for dev in DEVELOPERS.values())
__maintainer__ = DEVELOPERS["nilp0inter"].name
__maintainer_email__ = DEVELOPERS["nilp0inter"].email
__license__ = "LGPLv3"
