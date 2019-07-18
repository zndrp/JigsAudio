#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import os, glob, jinja2

# Template to render webpage
TEMPLATE = "metro-jinja.html"
#the Directory it will use to generate
BASE_FOLDER = "/Users/Zander/Dropbox/City-Futures/website/html/"
RESOURCE_FOLDER = BASE_FOLDER + "Resources/"

def main():
    
    event_name = input("Name of the event being created? (Directory name files will need to be placed in): ")
    
    owd = os.getcwd()
    os.chdir(RESOURCE_FOLDER)

    matches = (
        [file.split('-')[0] for file in glob.glob("*.wav")],
        [file.split('.')[0] for file in glob.glob("*.jpg")]
    )

    matches = [name for name in matches[0] if name in matches[1]]

    context = { # Your variables for your template will go in this dictionary
        'audio_files': set([file+'-1.wav' for file in matches]),
        'image_files': [
            {'filename':file, 'has_audio': file.split('.')[0] in matches }
             for file in glob.glob("*.jpg")
        ],
        'event_name': event_name
    }
    print(context)

    template    = os.path.join(owd, TEMPLATE)
    output_file = os.path.join(BASE_FOLDER, event_name + ".html")

    with open(output_file, "w") as text_file:
        text_file.write(render(template, context))
        print(
            "Webpage created with the name:\n {0}\nusing template\n {1}"
            .format(output_file, template))

def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)


if __name__ == "__main__":
    main()
