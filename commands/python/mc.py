import requests
import sys
import os

thing_to_do = sys.argv[1]

if thing_to_do == None:
	print("mc <command> [args]\n\ncommands:\n  install <modrinth mod name>\n  ex:\n    mc install sodium\n\n  update")

elif thing_to_do == 'update':
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
	elif version != newest_update:
		answer = input("a new version is available, would you like to install? (y/n)\n")
		if answer == 'y':
			newest_version = requests.get("https://codeload.github.com/be4ryllium/mod-installer/zip/refs/heads/master").content
			with open("newest.zip", mode="wb") as f:
				f.write(newest_version)
		else:
			print("ok")

elif thing_to_do == 'install':

	mod_name = sys.argv[2] # get the argument from the thing

	mod = requests.get("https://api.modrinth.com/v2/project/" + mod_name)

	if mod.status_code == 404:
		print("Error: no mod with the name", mod_name, "exists.")
	else:
		mod_json = mod.json()
		github_url = mod_json['source_url']

		if github_url.find("github") == -1:
			print("This thing only works with github source links sorry :(")
		else:
			author_and_repo = github_url[18:len(github_url)]

			versions = requests.get("https://api.github.com/repos" + author_and_repo + "/releases")
			versions_json = versions.json()

			v = 0
			for i in versions_json:
				print(str(v) + ": " + i['name'])
				v += 1

			answer = input("which one: ")

			print("downloading...")
			mod_name_with_version = versions_json[int(answer)]['name']
			browser_download_url = versions_json[int(answer)]['assets'][0]['browser_download_url']
			mod_jar = requests.get(browser_download_url).content
			print("downloaded")

			mod_jar_name = browser_download_url[browser_download_url.rfind("/")+1:len(browser_download_url)]

			with open("../mods_folder_directory.txt") as f:
				mod_folder_location = f.read()
				if mod_folder_location == "":
					mod_folder_location = os.getenv('APPDATA') + "\\.minecraft\\mods"
				with open(mod_folder_location + "\\" + mod_jar_name,mode="wb") as jar:
					jar.write(mod_jar)
					print("done. downloaded to " + mod_folder_location + "\\" + mod_jar_name)
					jar.close()
				f.close()