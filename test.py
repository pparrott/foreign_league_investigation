#! python3

string = '/usr/local/opt/python@3.8/bin:/Library/Frameworks/Python.framework/Versions/3.8/bin:/Users/Phil/anaconda3/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Applications/VMware Fusion.app/Contents/Public:/opt/X11/bin'

for i in string.split(':'):
    print(i)