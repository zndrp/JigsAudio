import os, glob, jinja2

TEMPLATE = "status_template.html"
event_name = "test_generated"

def main():
	matches = glob.glob("*.wav")
	owd = os.getcwd()

	print(matches)

	context = {
		'audio_files': set([file for file in matches])
	}

	print(context)

	template    = os.path.join(owd, TEMPLATE)
	output_file = os.path.join(event_name + ".html")

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

main()

