'''
js_tweaker.py\n
JS Tweaker for Steam Library UI by Jonius7\n
Handles the applying process of JS tweaks

libraries needed: jsbeautifier, jsmin
'''

import jsbeautifier
from jsmin import jsmin
import yaml

import platform
import os
import sys
import shutil
import traceback
import re
import time
import datetime
import copy

import js_manager

LOCAL_DEBUG = 0 #Set to 1 to not copy files to/from Steam directory

# Determine Steam Library Path
OS_TYPE = platform.system()
if OS_TYPE == "Windows":
    import winreg

swap_js = {'5:"libraryroot"': '5:"libraryreet"',
           #'h=m.nTop,': 'h = (t.children[0] && t.children[0].childNodes[0] && t.children[0].childNodes[0].childNodes[0] && t.children[0].childNodes[0].childNodes[0].classList && t.children[0].childNodes[0].childNodes[0].classList.contains("gamelistentry_HoverOverlay_3cMVy") && t.children[0].childNodes[0].childNodes[0].classList.contains("gamelistentry_Container_2-O4Z")) || (t.children[0].classList && t.children[0].classList.contains("gamelistentry_FriendStatusHover_2iiN7")) ? m.nTop * 0.75 : m.nTop,'
            #'([a-z])=([a-z]).slice\(0,6\);': '\\1=\\2.slice(0,12);'
           }
swapback_js = {'5:"libraryreet"': '5:"libraryroot"',
               #'h = (t.children[0] && t.children[0].childNodes[0] && t.children[0].childNodes[0].childNodes[0] && t.children[0].childNodes[0].childNodes[0].classList && t.children[0].childNodes[0].childNodes[0].classList.contains("gamelistentry_HoverOverlay_3cMVy") && t.children[0].childNodes[0].childNodes[0].classList.contains("gamelistentry_Container_2-O4Z")) || (t.children[0].classList && t.children[0].classList.contains("gamelistentry_FriendStatusHover_2iiN7")) ? m.nTop * 0.75 : m.nTop,': 'h=m.nTop,'
               #'([a-z])=([a-z]).slice\(0,12\);': '\\1=\\2.slice(0,6);'
               }

fixes_dict = {}
#yaml_data = {}

def initialise():
    fixes_dict.clear() #not fixes_dict = {}
    #yaml_data.clear()

def library_dir():
    '''
    Returns the Steam Library directory path (OS specific)
    '''
    try:
        steamui_path = ""
        if OS_TYPE == "Windows":
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\Valve\Steam")
            steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
            steamui_path = steam_path.replace("/","\\") + "\steamui"
            #print(steamui_path)
        elif OS_TYPE ==  "Darwin":
            steamui_path = os.path.expandvars('$HOME') + "/Library/Application Support/Steam" + "/steamui"
        elif OS_TYPE ==  "Linux":
            steamui_path = os.path.expandvars('$HOME') + "/.steam/steam" + "/steamui"
        return steamui_path
    except:
        error_exit("Steam library directory could not be found.")

######

def copy_files_from_steam(reset=0): #set reset to 1 to overwrite files with fresh copy (useful for updates)
    try:
        if reset == 1 or LOCAL_DEBUG == 1:
            files_to_copy = ["library.js", "libraryroot.js"]
            for filename in files_to_copy:
                if not os.path.isfile(filename):
                    print("Copying file " + filename + " from Steam\steamui...")
                    shutil.copy2(library_dir() + "/" + filename, filename)
            if os.path.exists("libraryroot.beaut.js"):
                os.remove("libraryroot.beaut.js")
            
    except FileNotFoundError:
        error_exit("Steam directory and/or files not found.\n" \
              "Please check Steam\steamui for library.js and libraryroot.js")
            

def beautify_js():
    try:
        if not os.path.isfile("libraryroot.beaut.js"):
            print("Opening JS file and beautifying...")
            if not os.path.isfile("libraryroot.js"):
                shutil.copy2(library_dir() + "/libraryroot.js", "libraryroot.js")

            opts = jsbeautifier.default_options()
            #opts.eol = ""
            library = jsbeautifier.beautify_file("libraryroot.js", opts)

            f = open("libraryroot.beaut.js", "wt", newline='', encoding="UTF-8")
            print("Writing beautified file... please do not close")
            f.write(library)
            f.close()
            print("Beautified file write finished")
    except:
        error_exit("libraryroot.js not found")

#modify library.js to look for different libraryroot.js file
def setup_library(reset=0):
    try:
        #if reset == 1 or LOCAL_DEBUG == 1:
        if not os.path.isfile("library.js"):
            shutil.copy2(library_dir() + "/library.js", "library.js")
        if reset == 0:
            print("library.js changing to use tweaked JS. (librery.js)")
            modify_library(swap_js)        
        elif reset == 1: #revert library.js to use original libraryroot.js file
            print("library.js reverting to use original JS.")
            reset_html()
    except:
        error_exit("Error setting up library.js")
        

def modify_library(swap_js_array: dict):
    try:
        lines = []
        modified = 0
        with open('library.js', encoding="UTF-8") as infile:
            for line in infile:
                for src, target in swap_js_array.items():
                    new_line = re.sub(src, target, line)
                    #new_line = line.replace(src, target)
                    if new_line != line:
                        modified = 1
                lines.append(new_line)
        infile.close()
        if modified == 1:
            with open('librery.js', 'w', encoding="UTF-8") as outfile:
                for line in lines:
                    outfile.write(line)
            
            outfile.close()        
            shutil.copy2("librery.js", library_dir() + "/librery.js")
            print("librery.js copied over to " + library_dir() + "/librery.js")
    except:
        error_exit("library.js not found")

def modify_html():
    html_array = {"/library.js": "/librery.js"}
    
    try:
        lines = []
        modified = 0
        with open(library_dir() + "/index.html", encoding="UTF-8") as infile:
            for line in infile:
                for src, target in html_array.items():
                    new_line = re.sub(src, target, line)
                    if new_line != line:
                        modified = 1
                lines.append(new_line)
        infile.close()
        if modified == 1:
            with open(library_dir() + "/index.html.temp", 'w', encoding="UTF-8") as outfile:
                for line in lines:
                    outfile.write(line)            
            outfile.close()
            
            shutil.move(library_dir() +"/index.html", library_dir() + "/index.html.original")
            shutil.move(library_dir() +"/index.html.temp", library_dir() + "/index.html")
            print("index.html changing to use tweaked JS.")
            print("index.html backup created at " + library_dir() + "/index.html.original")
    except:
        error_exit("index.html unable to be patched.")

def reset_html():
    try:
        if os.path.isfile(library_dir() + "/index.html.original"):
            shutil.move(library_dir() + "/index.html.original", library_dir() + "/index.html")
            print(library_dir() + "/index.html replaced with backup: " + "index.html.original")
    except:
        error_exit("Unable to reset index.html")
            

def parse_fixes_file_OLD(filename):
    '''
    look through fixes file and add fixes to fixes_dict
    '''
    print("Finding Fixes...\n")
    global fixes_dict
    fixes_dict = {}
    try:
        with open(filename, newline='', encoding="UTF-8") as fi:
            lines = filter(None, (line.rstrip() for line in fi))
            try:
                for line in lines:
                    if not line.startswith('###'):
                        (key, val) = line.rstrip().split("  ")
                        if "~~" in key:
                            t = key.split("~~")
                            if len(t) == 2:
                                fixes_dict[t[1]] = {"prev" : t[0],
                                                    "current" : val}
                            else:
                                error_exit("Unexpected number of ~~ in line: " + line)
                        #elif re.search(r"\d\$", key):
                        #    print("V")
                        #    print(key)
                        else:
                            fixes_dict[key] = {"current" : val}
            except Exception as e:
                print("Error in line: " + line, file=sys.stderr)
                print(e, file=sys.stderr)
                fi.close()                
                error_exit("Invalid file format")
        fi.close()
    except FileNotFoundError:
        error_exit("fixes.txt not found")
    except Exception as e:
        error_exit("Error found while parsing fixes file: " + e)

class YamlHandler:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.parse_yaml_file()
        self.f_data = None#self.format_yaml_data()
        
    def parse_yaml_file(self):
        with open(self.filename, newline='', encoding="UTF-8") as f:
            data = yaml.safe_load(f)
        f.close()
        return data
    
    def format_yaml_data(self):
        '''
        Format yaml file data to support some Regex and TweakScript
        '''
        f_data = copy.deepcopy(self.data)
        self.regex = RegexHandler()
        for tweak in f_data:
            try:
                for i, find_repl in enumerate(tweak_strs := f_data[tweak]["strings"]):
                    #if using "previous line"
                    if (sem := semantic_find_str(find_repl["find"])):
                        tweak_strs[i].update({"find":
                            {"prev": self.regex.sub_find_with_regex(sem["prev"]),
                            "current": self.regex.sub_find_with_regex(sem["current"])}
                        })
                        tweak_strs[i]["repl"] = self.regex.sub_repl_with_regex(tweak_strs[i]["repl"])
                    else:
                        tweak_strs[i]["find"] = self.regex.sub_find_with_regex(tweak_strs[i]["find"])
                        tweak_strs[i]["repl"] = self.regex.sub_repl_with_regex(tweak_strs[i]["repl"])
            except KeyError:
                print("Tweak " + tweak + " has no strings to find and replace, skipping", file=sys.stderr)
                continue
            except:
                error_exit("Unable to properly format Yaml data at: " + tweak)
        return f_data

def raw_text(str_text):
    '''
    may not be needed \n
    takes a string and return a "raw string" version of it
    '''
    raw_text = [str_text]
    str_text = "%r"%str_text
    raw_text = str_text[1:-1]
    return raw_text

def escaped_pattern(pattern_str):
    str = re.escape(pattern_str)
    #str = re.sub('\\\\([0-9]+)', '\\1', str)
    return str

def regex_search(pattern_str, string):
    return re.search(escaped_pattern(pattern_str), string)

def semantic_find_values(str, config):
    '''
    String to search through and find values
    '''
    pass

def semantic_find_str(find_str):
    '''
    May need to redo/realign with the process
    '''
    #find_str = unescape(find_str)
    semantic = None
    if "~~" in find_str:
        t = find_str.split("~~")
        if len(t) == 2:
            semantic = {"prev" : t[0],
                        "current" : t[1]}
    return semantic

def unescape(string):
    #new_string = re.sub(r'\\(.)', r'\1', string)
    #new_string = re.sub(r'\([tnrvf])', r'\1', string)
    #return new_string
    #should cover all practical cases
    new_string = re.sub(r'\\(.)', r'\1', string, flags=re.DOTALL)
    return new_string

class RegexHandler:
    def __init__(self):
        #Detecting letter variables %1% %2% %3% etc.
        self.vars = re.compile("%([0-9]+)%")
        #The regex pattern to replace them with
        self.letters = "([A-Za-z]+)"
    
    def sub_find_with_regex(self, find):
        r'''
        returns string where:
            self.vars       regex pattern substituted with
            self.latters    regex pattern
        string special characters are escaped beforehand
            special characters: ()[]{}?*+-|^$\\.&~# \t\n\r\v\f
        '''
        return self.vars.sub(self.letters, escaped_pattern(find))
    
    def sub_repl_with_regex(self, repl):
        return self.vars.sub(r"\\"+"\\1",  escaped_pattern(repl))
    
    def find_and_repl(self, find, repl, line, lineno):
        '''
        takes a find/replace pair and returns the string to be written
            find - the string to find (regex formatted) \n
            repl - the string to replace it with (regex formatted) \n
            line - the line in question (in the tweaks file)
        '''
        return_string = unescape(re.sub(find, repl, line))
        #print(return_string.ljust(70)[:70].strip() + (' ...' if len(return_string) > 70 else ''))
        print("TWEAK (" + str(lineno) + "): " + return_string.strip().ljust(120)[:120] + (' ...\n' if len(return_string) > 120 else '\n'), end='')
        return return_string    
        
    def find(self, find, line):
        return re.search(find, line)

def find_var_names(string):
    #return re.findall("[A-Za-z]+", "Ga.c, ab.d, cc.d, e.b")
    #b = re.sub("%[0-9]+%", "([A-Za-z]+)", escaped_pattern("Object(%1%.%2%)([%3%, %4%], n)"))
    #re.search(b, "Object(Ap.g)([e, t], n)")
    #unescape(re.sub('Object\\(([A-Za-z]+)\\.([A-Za-z]+)\\)\\(\\[([A-Za-z]+),\\ ([A-Za-z]+)\\],\\ n\\)', 'Object\\(\\1\\.\\2\\)\\(\\[\\3,\\ \\4\\],\\ n\\)', 'Object(p.g)([e, t], n)'))  
    pass
       
def write_modif_file(data):
    start_time = datetime.datetime.now()
    try:
        r_search = RegexHandler()
        beaut_filename = "libraryroot.beaut.js"
        modif_filename = "libraryroot.modif.js"
        
        with open(beaut_filename, "r", newline='', encoding="UTF-8") as f, \
             open(modif_filename, "w", newline='', encoding="UTF-8") as f1:
            prev_line = ""
            for i, line in enumerate(f, start=1):
                try:
                    modified = 0            
                    for tweak in data:
                        if "strings" in data[tweak]:                        
                            for find_repl in data[tweak]["strings"]:
                                if "find" in find_repl:
                                    #print(find_repl["find"])
                                    if "prev" in find_repl["find"]:
                                    #if (sem := semantic_find_str(find_repl["find"])):
                                        #print(find_repl["find"])
                                        #sem["current"] = escaped_pattern(sem["current"])
                                        #sem["prev"] = escaped_pattern(sem["prev"])
                                        #print("PREV FOUND")
                                        if r_search.find(find_repl["find"]["prev"], prev_line) and \
                                            r_search.find(find_repl["find"]["current"], line):
                                            f1.write(r_search.find_and_repl(
                                                find_repl["find"]["current"],
                                                find_repl["repl"],
                                                line,
                                                i))
                                            modified = 1
                                                
                                    #el
                                    elif r_search.find(find_repl["find"], line):
                                        f1.write(r_search.find_and_repl(
                                                    find_repl["find"],
                                                    find_repl["repl"],
                                                    line, 
                                                    i))
                                        modified = 1
                                        #print("NORMAL" + tweak)
                        #else:
                        #    print("Strings to find/replace not found in tweak: " + tweak + ", skipping")
                    if modified == 0:
                        f1.write(line)
                    prev_line = line
                except:
                    #print("Unable to find strings for tweak: " + tweak)
                    continue
        f.close()
        f1.close()
    
    except:
        error_exit("Error writing " + modif_filename + " at: " + tweak + " " + find_repl["find"])
    end_time = datetime.datetime.now()
    print(end_time - start_time)
    
def write_modif_file_OLD():
    start_time = datetime.datetime.now()
    try:
        with open("libraryroot.beaut.js", "r", newline='', encoding="UTF-8") as f, \
             open("libraryroot.modif.js", "w", newline='', encoding="UTF-8") as f1:
            prev_line = ""
            for line in f:
                modified = 0
                for fix in fixes_dict:
                    if "prev" in fixes_dict[fix]:
                        if fixes_dict[fix]["prev"] in prev_line and fix in line:
                            f1.write(find_fix(line, fix))
                            modified = 1
                    elif fix in line:
                        f1.write(find_fix(line, fix))
                        modified = 1
                if modified == 0:
                    f1.write(line)
                prev_line = line
        f.close()
        f1.close()
    except:
        error_exit("Error writing libraryroot.modif.js")
    end_time = datetime.datetime.now()
    print(end_time - start_time)
        
def find_fix(line, fix):
    m_line = line.replace(fix, fixes_dict[fix]["current"])
    #print("FIX: ", end = '')
    #print(m_line.strip())
    #print(fixes_dict[fix]["current"])
    print("FIX: " + m_line.strip())
    return m_line

def find_fix_with_variable(line, fix):
    #res = [i.start() for i in re.finditer("\$\^", st)]
    #for lv in res:
    print("todo")

def re_minify_file():
    try:
        print("\nRe-minify JS file")
        with open("libraryroot.modif.js", "r", newline='', encoding="UTF-8") as js_file:
            minified = jsmin(js_file.read())
        with open("libraryreet.js", "w", newline='', encoding="UTF-8") as js_min_file:
            js_min_file.write(minified)
        js_file.close()
        js_min_file.close()
        print("\nJS Minify complete. (libraryreet.js)")
    except:
        error_exit("Error completing JS minify.")
    
def copy_files_to_steam():
    try:
        if LOCAL_DEBUG == 0:
            files_to_copy = ["librery.js", "libraryreet.js"]
            for filename in files_to_copy:
                if os.path.exists(filename):
                    shutil.copy2(filename, library_dir() + "/" + filename)
                    print("File " + filename + " written to " + library_dir())
                else:
                    print("File " + filename + " does not exist, skipping.", file=sys.stderr)
                
    except FileNotFoundError:
        error_exit("Files not found!\n" \
              "Run the other functions in js_tweaker first.")
    except Exception as e:
        error_exit("Error found while copying files to Steam: " + e)


def print_error(errormsg: str):
    '''
    Prints error message, traceback
    '''
    print(errormsg, file=sys.stderr)
    print("~~~~~~~~~~")
    print(traceback.print_exc(), file=sys.stderr)
    print("~~~~~~~~~~")

def error_exit(errormsg: str):
    '''
    Prints error message, traceback and exits
    '''
    print_error(errormsg)
    sys.exit()

    
def main(RUN = True):
    if RUN:
        print("JS Tweaker for Steam Library UI by Jonius7\n")
        initialise()
        copy_files_from_steam()
        setup_library()
        modify_html()
        beautify_js()    
        #parse_fixes_file_OLD("fixes.txt")
        #write_modif_file_OLD()
        a = YamlHandler("js_tweaks.yml")
        write_modif_file(a.f_data)
        re_minify_file()
        copy_files_to_steam()
        print("\nSteam Library JS Tweaks applied successfully.")
        time.sleep(1)
                
if __name__ == "__main__":
    main()
