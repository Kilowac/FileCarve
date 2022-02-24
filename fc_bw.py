import sys
import os
#imageCpy.raw
r = ''; b = ''; g = '';
bl = ''; y = ''; c = '';
m = ''; w = ''
jcon = False
pcon = False
r_path = ''
usage = 'Usage => fc.py [-f <FILEPATH>] [-t <FILETYPE>] [-h]'
for i in range(len(sys.argv)):
    if '-h' in sys.argv:
        print(w+usage)
        print(w+'\nFC: Carve out specific files from other files using headers and footers.\n')
        print('required arguments:')
        print('  -f <FILEPATH>        One argument providing the path for the file to be read.\n')
        print('optional arguments:')
        print('  -h                   Show this help message and exit')
        print('  -t <FILETYPE>        This flag will determine what files to look for. As of the current implementation,')
        print('                       only \'jpg\' and \'pdf\' are accepted. If no arguments are provided, both jpg and pdf files')
        print('                       will be searched. ')
        exit()
    elif sys.argv[i] == '-f':
        if not((i+1) >= len(sys.argv)):
            r_path = sys.argv[i+1]
            print(g+'\n['+y+'*'+g+'] Verifying '+w+r_path+g+' path...')
            if os.path.exists(r_path):
                print(w+'['+g+'+'+w+']'+g+' File '+w+r_path+g+' found.\n')
            else:
                print(bl+'['+r+'-'+bl+']'+r+' File '+w+r_path+r+' not found')
                print(bl+'{'+r+'x'+bl+'}'+r+' Exiting program.\n')
                exit()
    elif sys.argv[i] == '-t':
        j = i+1
        for j in range(len(sys.argv)):
            if sys.argv[j] == 'jpg':
                jcon = True
            elif sys.argv[j] == 'pdf':
                pcon = True

if r_path == '':
    print(w+usage)
    print('    fc.py: error: the following arguments are required: -f <FILEPATH>')
    print('    Try \'-h\' for help')
    exit()

if not(jcon) and not(pcon):
    print(bl+'{'+r+'!'+bl+'}'+r+' No type arguments; defaulting to '+w+'.jpg'+r+' and '+w+'.pdf'+r+' files.\n')
    jcon = True
    pcon = True

rquery = ''
notify = w+'['+g+'+'+w+']'+g+' Searching for: '

if jcon and pcon:
    rquery = w+'.jpg'+g+' and '+w+'.pdf'
elif jcon:
    rquery = w+'.jpg'
elif pcon:
    rquery = w+'.pdf'

print(notify+rquery+g+' files\n')

while True:
    print(w+'('+g+'?'+w+')' +w+ ' What path would you like to write the files to?\n'+y+'    >> '+w, end = '')
    w_path = input()
    if os.path.exists(w_path):
        break
    print(bl+'\n['+r+'-'+bl+']'+r+' Path '+w+w_path+r+' does not exist.\n')

if w_path[len(w_path)-1] != '/':
    w_path += '/'

print(w+'\n['+g+'+'+w+']'+g+' Path to '+w+w_path+g+' established.\n')

file = open(r_path, 'rb')

data = file.read(512)
build = b''
b_proc = False
footer = b''
ext = ''
jpg = 1
pdf = 1
file_type = ''

def hdr(data):
    global ext, jpg, pdf, file_type, w_path
    if jcon:
        ind = data.find(b'\xff\xd8\xff')
        if ind != -1:
            ext = '.jpg'
            file_type = 'Carved_Image{}'.format(jpg)+ext;
            while os.path.exists(w_path+ file_type):
                jpg += 1
                file_type = 'Carved_Image{}'.format(jpg)+ext
            return ind

    if pcon:
        ind = data.find(b'\x25\x50\x44\x46')
        if ind != -1:
            ext = '.pdf'
            file_type = 'Carved_Document{}'.format(pdf)+ext;
            while os.path.exists(w_path+file_type):
                pdf += 1
                file_type = 'Carved_Document{}'.format(pdf)+ext
            return ind
    return -1

def ftr(data):
    global ext
    if ext == '.jpg':
        ind = data.find(b'\xff\xd9')
        if ind != -1:
            ind += 2
    elif ext == '.pdf':
        ind = data.find(b'\x45\x4f\x46\x0a')
        if ind != -1:
            ind += 4
    return ind

strt = -1
f = None

print(g+'('+y+'?'+g+')'+g+' Searching for '+w+rquery+g+' headers...\n')

while data:
    if not(b_proc):
        if hdr(data) != -1:
            print(g+'['+c+'~'+g+'] '+w+ ext + c + ' file header found.')
            strt = hdr(data)
            b_proc = True
            print(g+'['+y+'*'+g+'] Building '+w+ext+g+' file...')
            w_file = w_path + file_type
            f = open(w_file, "wb")
    if b_proc:
        end = ftr(data)
        if end == -1:
            s1 = slice(strt,len(data))
            build += data[s1]
            strt = 0
        else:
            print(g+'['+y+'*'+g+'] '+w+ ext + g + ' footer encountered, writing file...')
            s1 = slice(strt,end)
            build += data[s1]
            f.write(build)
            b_proc = False
            print(w+'['+g+'+'+w+']'+g+' File written to: '+w+w_file+'\n')
            build = b''
            footer = b''
            f.close()
            print(g+'('+y+'?'+g+')'+g+' Searching for '+w+rquery+g+' headers...\n')

    data = file.read(512)
print(w+'['+g+'+'+w+']'+' Program Completed.\n')
file.close()
