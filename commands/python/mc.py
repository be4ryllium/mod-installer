import requests
import sys
import os

def explain():
	print("\nmc <command> [args]\n\ncommands:\n  install <modrinth project name>:\n    installs a mod/resource pack off of modrinth and puts it into your mods/resource packs folder\n    ex:\n      mc install sodium\n\n  update:\n    checks for updates in the program")
	exit()

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

	mod_name = sys.argv[2] # get the argument from the thing

	print("getting from modrinth...")

	mod = requests.get("https://api.modrinth.com/v2/project/" + mod_name + "/version")

	if mod.status_code == 404:
		print("Error: no mod/resource pack with the name", mod_name, "exists.")
	else:
		mod_json = mod.json()
		is_mod = False


		v = 0
		for i in mod_json:
			print(str(v) + ": " + i['name'] + "  -  " + i['version_number'])
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
else:
	explain()