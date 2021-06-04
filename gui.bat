@echo off

pylupdate6 --no-summary -ts ts/de_DE.ts gui.py ui/main.ui
lrelease ts/de_DE.ts
pylupdate6 --no-summary -ts ts/en_US.ts gui.py ui/main.ui
lrelease ts/en_US.ts
pyuic6 -o ui/main.py ui/main.ui
python gui.py $@
