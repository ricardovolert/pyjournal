import datetime
import os
import shutil
import sys

import shell_util

figure_str = r"""
\begin{figure}[h]
\centering
\includegraphics[width=0.5\linewidth]{@figname@}
\caption{\label{fig:@figlabel@} caption goes here}
\end{figure}

"""


def get_entry_string():
    now = datetime.datetime.now()
    return str(now.replace(microsecond=0)).replace(" ", "_").replace(":",".")


def get_dir_string():
    now = datetime.date.today()
    return str(now)

    
def entry(nickname, images, defs, string=None):

    try: editor = os.environ["EDITOR"]
    except:
        editor = "emacs"

    # determine the filename
    entry_id = get_entry_string()
    entry_dir = get_dir_string()
    ofile = entry_id + ".tex"

    # determine the directory we place it in -- this is the form yyyy-mm-dd/
    odir = "{}/journal-{}/entries/{}/".format(defs[nickname]["working_path"],
                                              nickname,
                                              entry_dir)
    
    if not os.path.isdir(odir):
        try: os.mkdir(odir)
        except:
            sys.exit("ERROR: unable to make directory {}".format(odir))


    # create the entry file.  If we passed in a string, then write it
    # too.
    try: f = open(odir + ofile, "w")             
    except:
        sys.exit("ERROR: unable to open {}".format(odir + ofile))

    if not string == None:
        f.write(string)

    
    # if there are images, then copy them over and add the figure
    # headings to the entry
    images_copied = []
    if len(images) > 0:        
        for n in range(len(images)):

            # does an image by that name already live in the dest
            # directory?
            im = images[n]
            src = "{}/{}".format(defs["image_dir"], im)
            dest = odir

            if os.path.isfile("{}/{}".format(dest, im)):
                im_copy = "{}_{}".format(entry_id.replace(".", "_"), im)
            else:
                im_copy = im

            dest = "{}/{}".format(dest, im_copy)
                              
            # copy it
            try: shutil.copy(src, dest)
            except:
                print src
                print dest
                sys.exit("ERROR: unable to copy image {}".format(src))

            images_copied.append(im_copy)
            
            # create a unique label for latex referencing
            idx = im.lower().rfind(".jpg")
            idx = max(idx, im.lower().rfind(".png"))
            idx = max(idx, im.lower().rfind(".pdf"))
            
            if idx >= 0:
                im0 = "{}:{}".format(entry_id, im[:idx])

            # add the figure text
            for l in figure_str.split("\n"):
                f.write("{}\n".format(l.replace("@figname@", "entries/{}/{}".format(entry_dir, im_copy)).replace("@figlabel@", im0).rstrip()))
                

    # add the entry id as a LaTeX comment
    f.write("\n\n% entry: {}".format(entry_id))    

    f.close()
        
        
    # launch the editor specified in the EDITOR environment variable
    if string == None:
        if editor == "emacs":
            prog = "{} {}/{}".format("emacs -nw", odir, ofile)
        else:
            prog = "{} {}/{}".format(editor, odir, ofile)
            
        stdout, stderr, rc = shell_util.run(prog)
        
        
    # commit the entry to the working git repo
    os.chdir(odir)
    
    stdout, stderr, rc = shell_util.run("git add " + ofile)
    stdout, stderr, rc = shell_util.run("git commit -m 'new entry' " + ofile)

    # commit any images too
    for im in images_copied:
        stdout, stderr, rc = shell_util.run("git add " + im)
        stdout, stderr, rc = shell_util.run("git commit -m 'new image' " + im)

    # helpful edit suggestion
    print "entry created.  Use 'pyjournal.py edit {}' to edit this entry.".format(entry_id)

    
def edit(nickname, date_string, defs):

    # find the file corresponding to the date string
    entry_dir = "{}/journal-{}/entries/".format(defs[nickname]["working_path"], nickname)

    os.chdir(entry_dir)
    
    try: d, t = date_string.split(" ")
    except:
        sys.exit("invalid date string")
            
    if not os.path.isdir(d):
        sys.exit("entry directory does not exist")

    file = "{}/{}_{}.tex".format(d, d, t)
    
    # git commit any changes
    if not os.path.isfile(file):
        sys.exit("entry {} does not exist".format(file))

    # open the file for appending        
    try: editor = os.environ["EDITOR"]
    except:
        editor = "emacs"

    entry_id = get_entry_string()

    try: f = open(file, "a+")             
    except:
        sys.exit("ERROR: unable to open {}".format(file))

    f.write("\n\n% entry edited: {}".format(entry_id))    
    f.close()

    if editor == "emacs":
        prog = "{} {}".format("emacs -nw", file)
    else:
        prog = "{} {}".format(editor, file)
        
    stdout, stderr, rc = shell_util.run(prog)

    stdout, stderr, rc = shell_util.run("git commit -m 'edited entry' " + file)
    
    
def elist(nickname, num, defs):

    entry_dir = "{}/journal-{}/entries/".format(defs[nickname]["working_path"], nickname)

    entries = {}
    for d in os.listdir(entry_dir):
        if os.path.isdir(entry_dir + d):

            dir = os.path.normpath("{}/{}".format(entry_dir, d))
                                   
            for t in os.listdir(dir):
                if t.endswith(".tex"):
                    entries[t] = "{}/{}".format(dir, t)

    e = entries.keys()
    e.sort(reverse=True)

    for n in range(min(num, len(e))):
        idx = e[n].rfind(".tex")
        entry_id = e[n][:idx]
        print "{}: {}".format(entry_id, entries[e[n]])
        
    

    
        
    
