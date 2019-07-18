import os, glob, jinja2
import datetime
from operator import itemgetter

TEMPLATE = "status_template.html"
#event_name = "test_generated"

#Change this if the audio is in a different Directory)
AUDIODIR = "../audiorecordings/"


def main():
	owd = os.getcwd()

	matches = glob.glob(os.path.join(AUDIODIR, "*.wav"))

	print(matches)

	context = {"audio_files": 
			list(zip(

				[file for file in matches],
				[datetime.datetime.fromtimestamp(
					int(os.stat(file)[8]))
						.strftime('%d-%m-%Y %H:%M:%S')
				for file in matches]

			))
	}

	context["num_files"] = len(context["audio_files"])

	context["audio_files"].sort(key=itemgetter(1))

	print(context)

	template    = os.path.join(owd, TEMPLATE)
	output_file = "index.html"

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
