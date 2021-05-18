#!/bin/sh

pylupdate6 gui.py ui/main.ui -ts ts/de_DE.ts
lrelease ts/de_DE.ts
pylupdate6 gui.py ui/main.ui -ts ts/en_US.ts
lrelease ts/en_US.ts
pyuic6 -o ui/main.py ui/main.ui
/usr/bin/env python3 gui.py $@
