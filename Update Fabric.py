import os, xml.etree.ElementTree as ET, json, re, platform, pkg_resources, subprocess, sys

# Check if additionnal libraries are installed
required = {'requests', 'bs4'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
if missing:
	python = sys.executable
	subprocess.check_call(
		[python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
import requests
from bs4 import BeautifulSoup

"""# Set the name of the proccess to the name of the file
filesplit = __file__.split("\\")
filename = filesplit[len(filesplit)-1]
filename_without_py = filename.replace(".py", "")
os.system("title "+filename_without_py)"""

# Get mc dir
if platform.system() == "Windows": mc_dir = os.path.join(os.getenv('APPDATA'), ".minecraft")
elif platform.system() == "Linux": mc_dir = os.path.join(os.getenv("HOME"), ".minecraft")
elif platform.system() == "Darwin": mc_dir = os.path.join(os.getenv("HOME"), "Library", "Application Support", "minecraft")
else: mc_dir = input("Enter the .minecraft path: ")
mc_ver_dir = os.path.join(mc_dir, "versions")

# Get list of fabric and quilt
fabric_list = []
iris_list = []
quilt_list = []

for file in os.listdir(mc_ver_dir):
	dir = os.path.join(mc_ver_dir, file)
	if os.path.isdir(dir):
		if "fabric" in dir:
			if not "iris" in dir:
				fabric_list = fabric_list + [file]
			else:
				iris_list = iris_list + [file]
		elif "quilt" in dir:
			quilt_list = quilt_list + [file]

# Get latest ver for quilt and fabric
maven_metadata_fabric = requests.get("https://maven.fabricmc.net/net/fabricmc/fabric-loader/maven-metadata.xml", allow_redirects=True).text
maven_metadata_quilt = requests.get("https://maven.quiltmc.org/repository/release/org/quiltmc/quilt-loader/maven-metadata.xml", allow_redirects=True).text

list_ver_fabric = []
root = ET.fromstring(maven_metadata_fabric)
for child in root.iter('version'):
	list_ver_fabric = list_ver_fabric + [child.text]
latest_ver_fabric = list_ver_fabric[len(list_ver_fabric)-1]

list_ver_quilt = []
root = ET.fromstring(maven_metadata_quilt)
for child in root.iter('version'):
	list_ver_quilt = list_ver_quilt + [child.text]
latest_ver_quilt = list_ver_quilt[len(list_ver_quilt)-1]

html_github_iris = requests.get("https://github.com/IrisShaders/Iris-Installer-Maven/tree/master/net/coderbot/iris-loader").text
soup = BeautifulSoup(html_github_iris, 'html.parser')
result = soup.find_all(class_="js-navigation-open Link--primary")
iris_versions = []
for i in result:
	iris_versions = iris_versions + [i.string]

#https://stackoverflow.com/questions/50996134/finding-the-latest-version-in-a-list
def major_minor_micro(version):
	major, minor, micro = re.search('(\d+)\.(\d+)\.(\d+)', version).groups()
	return int(major), int(minor), int(micro)

latest_ver_iris = max(iris_versions, key=major_minor_micro)

# Check updatable installations
fabric_update_list = []
for check in fabric_list:
	current_version = check.split("-")[2]
	if latest_ver_fabric != current_version:
		fabric_update_list = fabric_update_list + [check]

iris_update_list = []
for check in iris_list:
	current_version = check.split("-")[3]
	if latest_ver_iris != current_version:
		iris_update_list = iris_update_list + [check]

quilt_update_list = []
for check in quilt_list:
	if "beta" in check: current_version = check.split("-")[2] + "-" + check.split("-")[len(check.split("-"))-2]
	else: current_version = check.split("-")[2]
	if latest_ver_quilt != current_version:
		quilt_update_list = quilt_update_list + [check]

# Main component
for i in fabric_update_list:
	current_version = i.split("-")[2]
	new_i = i.replace(current_version, latest_ver_fabric)
	path_folder = os.path.join(mc_ver_dir, i)
	new_path_folder = os.path.join(mc_ver_dir, new_i)
	path_json = os.path.join(path_folder, i + ".json")
	new_path_json = os.path.join(path_folder, new_i + ".json")
	path_jar = os.path.join(path_folder, i + ".jar")

	try:
		data = json.load(open(path_json))
		for value in data["libraries"]:
			if "net.fabricmc:fabric-loader" in value["name"]:
				value["name"] = value["name"].replace(current_version, latest_ver_fabric)
		data["id"] = data["id"].replace(current_version, latest_ver_fabric)
		json.dump(data, open(path_json, 'w'))
	except: pass

	try: os.rename(path_json, new_path_json)
	except: pass

	if os.path.isfile(path_jar):
		os.remove(path_jar)
	
	try: os.rename(path_folder, new_path_folder)
	except: pass

for i in iris_update_list:
	current_version = i.split("-")[3]
	new_i = i.replace(current_version, latest_ver_iris)
	path_folder = os.path.join(mc_ver_dir, i)
	new_path_folder = os.path.join(mc_ver_dir, new_i)
	path_json = os.path.join(path_folder, i + ".json")
	new_path_json = os.path.join(path_folder, new_i + ".json")
	path_jar = os.path.join(path_folder, i + ".jar")

	try:
		data = json.load(open(path_json))
		for value in data["libraries"]:
			if "net.coderbot:iris-loader" in value["name"]:
				value["name"] = value["name"].replace(current_version, latest_ver_iris)
		data["id"] = data["id"].replace(current_version, latest_ver_iris)
		json.dump(data, open(path_json, 'w'))
	except: pass

	try: os.rename(path_json, new_path_json)
	except: pass

	if os.path.isfile(path_jar):
		os.remove(path_jar)
	
	try: os.rename(path_folder, new_path_folder)
	except: pass

for i in quilt_update_list:
	if "beta" in i: current_version = i.split("-")[2] + "-" + i.split("-")[len(i.split("-"))-2]
	else: current_version = i.split("-")[2]
	new_i = i.replace(current_version, latest_ver_quilt)
	path_folder = os.path.join(mc_ver_dir, i)
	new_path_folder = os.path.join(mc_ver_dir, new_i)
	path_json = os.path.join(path_folder, i + ".json")
	new_path_json = os.path.join(path_folder, new_i + ".json")
	path_jar = os.path.join(path_folder, i + ".jar")

	try:
		data = json.load(open(path_json))
		for value in data["libraries"]:
			if "org.quiltmc:quilt-loader" in value["name"]:
				value["name"] = value["name"].replace(current_version, latest_ver_quilt)
		data["id"] = data["id"].replace(current_version, latest_ver_quilt)
		json.dump(data, open(path_json, 'w'))
	except: pass

	try: os.rename(path_json, new_path_json)
	except: pass

	if os.path.isfile(path_jar):
		os.remove(path_jar)
	
	try: os.rename(path_folder, new_path_folder)
	except: pass

# Correct launcher_profiles.json
data = json.load(open(os.path.join(mc_dir, "launcher_profiles.json")))
for v in data["profiles"]:
	ver = data["profiles"][v]["lastVersionId"]
	if "fabric" in ver:
		if not "iris" in ver:
			current_version = ver.split("-")[2]
			if current_version != latest_ver_fabric:
				data["profiles"][v]["lastVersionId"] = ver.replace(current_version, latest_ver_fabric)
		else:
			current_version = ver.split("-")[3]
			if current_version != latest_ver_iris:
				data["profiles"][v]["lastVersionId"] = ver.replace(current_version, latest_ver_iris)
	elif "quilt" in ver:
		if "beta" in ver: current_version = ver.split("-")[2] + "-" + ver.split("-")[len(ver.split("-"))-2]
		else: current_version = ver.split("-")[2]
		if current_version != latest_ver_quilt:
			data["profiles"][v]["lastVersionId"] = ver.replace(current_version, latest_ver_quilt)
json.dump(data, open(os.path.join(mc_dir, "launcher_profiles.json"), 'w'))

print("Done")
print("Press any key to exit")
input()