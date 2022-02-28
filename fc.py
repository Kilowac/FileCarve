#THIS WILL ONLY CARVE OUT CONTIGUOUS FILES.
import sys
import os
from colorama import init, deinit, Fore, Back, Style
init()
print(Style.BRIGHT, end = '')
r = Fore.RED; b = Fore.BLUE; g = Fore.GREEN;
bl = Fore.BLACK; y = Fore.YELLOW; c = Fore.CYAN;
m = Fore.MAGENTA; w = Fore.WHITE

#jcon and pcon are the flags that tells the program what type of file(s) to look for
jcon = False
pcon = False

#the read path of the image file
r_path = ''


#General information for the user; argument processing
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
        for k in range(j,len(sys.argv)):
            if sys.argv[k] == 'jpg':
                jcon = True
            elif sys.argv[k] == 'pdf':
                pcon = True


#Verify path's existance
if r_path == '':
    print(w+usage)
    print('    fc.py: error: the following arguments are required: -f <FILEPATH>')
    print('    Try \'-h\' for help')
    exit()

#default file searching conditions
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

#Query the user for the writing location; verify and set writing path
while True:
    print(w+'('+g+'?'+w+')' +w+ ' What path would you like to write the files to?\n'+y+'    >> '+w, end = '')
    w_path = input()
    if os.path.exists(w_path):
        break
    print(bl+'\n['+r+'-'+bl+']'+r+' Path '+w+w_path+r+' does not exist.\n')

#Add '/' if non-existant for file writing; e.g. ./Folder[carved file] -> ./Folder/[carved file]
if w_path[len(w_path)-1] != '/':
    w_path += '/'

print(w+'\n['+g+'+'+w+']'+g+' Path to '+w+w_path+g+' established.\n')

file = open(r_path, 'rb')

#'build' is the variable that will be building the file to carve
#'b_proc' means 'build process;' this is a flag to focus on building the file and searching for
#    the file footer until completion
#'ext' is the extension of the file, this is used for defining what footer to look for after the file
#    building has started as well as being used for file writing reasons
#'pdf' and 'jpg' are for the file writing names
data = file.read(512)
build = b''
b_proc = False
footer = b''
ext = ''
jpg = 1
pdf = 1
file_type = ''

#search for file headers and naming the file to be written while cheking for pre-existing file names
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

#find footer determined by 'ext,' adjust index for offset, return index
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

#Starting index of the file header; 'f' is for file writing
strt = -1
f = None

print(g+'('+y+'?'+g+')'+g+' Searching for '+w+rquery+g+' headers...\n')

#Search for headers, if return is not -1, set b_proc flag, build file, and look for the footer
while data:
    if not(b_proc):
        if hdr(data) != -1:
            print(g+'['+c+'~'+g+'] '+w+ ext + c + ' file header found.')
            strt = hdr(data)
            b_proc = True
            print(g+'['+y+'*'+g+'] Building '+w+ext+g+' file...'+w)
            w_file = w_path + file_type
            f = open(w_file, "wb")
    if b_proc:
        end = ftr(data)
        #if the footer is not within the 512 byte sector contatonate the sector from strt to end, set strt to 0
        #    as this program is currently assuming the file is contifuous. Else, if footer is found, write from strt
        #    to the footer (including the footer as a result of the index offset)
        #Write to file
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
deinit()
