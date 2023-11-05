import requests
import sys
import os

command_descs = [
	"  install <project name> [-dep]:\n    installs a mod/resource pack off of modrinth and puts it into your mods/resource packs folder.\n    if -dep is enabled, it will only install the dependencies associated with the mod.\n    ex:\n      mc install sodium",
	"  update:\n    checks for updates in the program",
	"  describe <project name> [-in-detail]:\n    prints the description (or body, if you enable -in-detail) of the project\n    ex:\n      mc describe sodium -in-detail"
]

def explain():
	print("\nmc <command> [args]\n\ncommands:")
	for i in command_descs:
		print(i + "\n")
	exit()

def install(mod_name = None, dep_only = None):
	if mod_name == None:
		mod_name = sys.argv[2] # get the argument from the thing

	if len(sys.argv) > 3:
		for i in sys.argv[3:len(sys.argv)]:
			if i == '-dep' and dep_only == None:
				dep_only = True
				print("only getting dependencies from mod")

	print("getting from modrinth...")

	mod = requests.get("https://api.modrinth.com/v2/project/" + mod_name + "/version")

	if mod.status_code == 404:
		print("no mod/resource pack with the name", mod_name, "exists.")
	else:
		mod_json = mod.json()
		is_mod = False

		v = 0
		for i in mod_json:
			versions_string = ''
			loaders_string = ''
			for g in i['game_versions']:
				versions_string += g + ", "
			for g in i['loaders']:
				loaders_string += g + ", "
			if versions_string != '':
				versions_string = versions_string[0:len(versions_string)-2]
			if loaders_string != '':
				loaders_string = loaders_string[0:len(loaders_string)-2]
			print(str(v) + ": " + i['name'] + "    -    " + versions_string + "    -    " + loaders_string)
			v += 1

		answer = input("which one? (type 'x' to cancel): ")

		if answer == "x":
			print("cancelled")
			exit()

		mod_jar_name = mod_json[int(answer)]['files'][0]['filename']

		if mod_jar_name.find(".jar") != -1:
			print("project type: mod")
			is_mod = True
		else:
			print("project type: resource pack")
			if dep_only:
				print("error: dependency only mode doesn't work on resource packs")
				exit()

		if dep_only:
			dependencies = mod_json[int(answer)]['dependencies']
			if len(dependencies) == 0:
				print("this mod doesn't have any dependencies")
				exit()
			dep_i = 0
			for dep in dependencies:
				dep_i += 1
				print("getting dependency... (" + str(dep_i) + "/" + str(len(dependencies)) + ")\n")
				depend_r = requests.get("https://api.modrinth.com/v2/project/" + dep['project_id']).json()
				answer = input("name:        " + depend_r['title'] + "\ndescription: " + depend_r['description'] + "\nimportance:  " + dep['dependency_type'] + "\n\nwould you like to install? (y/n/x)\n")
				if answer == 'y':
					install(dep['project_id'], False)
				elif answer == 'x':
					print("aborted")
					exit()
				elif answer == 'n':
					print("ok")
			print("all dependencies looked at")
			exit()

		print("downloading...")
		browser_download_url = mod_json[int(answer)]['files'][0]['url']
		mod_jar = requests.get(browser_download_url).content
		print("downloaded")
		
		if is_mod:
			with open("../mods_folder_directory.txt") as f:
				mod_folder_location = f.read()
				if mod_folder_location == "":
					mod_folder_location = os.getenv('APPDATA') + "\\.minecraft\\mods"
				with open(mod_folder_location + "\\" + mod_jar_name,mode="wb") as jar:
					jar.write(mod_jar)
					print("done. saved to " + mod_folder_location + "\\" + mod_jar_name)
					jar.close()
				f.close()

			dependencies = mod_json[int(answer)]['dependencies']
			if len(dependencies) > 0:
				answer = input("\nthis mod has some dependencies, would you like to see and decide on installing them one by one? (y/n)\n")
				if answer == 'y':
					dep_i = 0
					for dep in dependencies:
						dep_i += 1
						print("getting dependency... (" + str(dep_i) + "/" + str(len(dependencies)) + ")\n")
						depend_r = requests.get("https://api.modrinth.com/v2/project/" + dep['project_id']).json()
						answer = input("name:        " + depend_r['title'] + "\ndescription: " + depend_r['description'] + "\nimportance:  " + dep['dependency_type'] + "\n\nwould you like to install? (y/n/x)\n")
						if answer == 'y':
							install(dep['project_id'], False)
						elif answer == 'x':
							print("aborted")
							break
						elif answer == 'n':
							print("ok")
				else:
					print("ok")
		else:
			with open("../resource_pack_folder_directory.txt") as f:
				res_folder_location = f.read()
				if res_folder_location == "":
					res_folder_location = os.getenv('APPDATA') + "\\.minecraft\\resourcepacks"
				with open(res_folder_location + "\\" + mod_jar_name,mode="wb") as jar:
					jar.write(mod_jar)
					print("done. saved to " + res_folder_location + "\\" + mod_jar_name)
					jar.close()
				f.close()

if len(sys.argv) == 1:
	explain()

thing_to_do = sys.argv[1]

if thing_to_do == 'update':
	location = sys.argv[0]

	# i know this is horrible shut up

	newest_update = requests.get("https://api.github.com/repos/be4ryllium/mod-installer").json()['updated_at']
	print("newest update: " + newest_update)

	f = open("..\\version.txt")
	version = f.read()
	f.close()
	if version == "":
		f = open("..\\version.txt", "w")
		f.write(newest_update)
		f.close()
		print("up to date")
	elif version != newest_update:
		answer = input("a new version is available, would you like to download? (y/n)\n")
		if answer == 'y':
			newest_version = requests.get("https://codeload.github.com/be4ryllium/mod-installer/zip/refs/heads/master").content
			with open("..\\newest.zip", mode="wb") as f:
				f.write(newest_version)
		else:
			print("ok")
	else:
		print("up to date")

elif thing_to_do == 'install':
	install()

elif thing_to_do == 'describe':
	mod_name = sys.argv[2]
	in_detail = 'description'

	if len(sys.argv) > 3:
		for i in sys.argv[3:len(sys.argv)]:
			if i == '-in-detail':
				in_detail = 'body'

	mod_req = requests.get("https://api.modrinth.com/v2/project/" + mod_name)
	if mod_req.status_code == 404:
		print("no project exists with the name", mod_name)
	else:
		print(mod_req.json()[in_detail])

else:
	explain()