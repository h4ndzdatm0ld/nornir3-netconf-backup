from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
import datetime, os, xmltodict, json, sys
from nornir_utils.plugins.tasks.files import write_file
from nornir_netconf.plugins.tasks import netconf_get_config

__author__ = "Hugo Tinoco"
__email__ = "hugotinoco@icloud.com"

# Specify a custom config yaml file.
nr = InitNornir("config.yml")

# Filter the hosts by the 'west-region' site key.
netconf_devices = nr.filter(operation="netconf-enabled")


def create_folder(directory):
    """Helper function to automatically generate directories"""
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Creating directory. " + directory)


def xml2json(xmlconfig):
    """Simple function to conver the extract xml config and convert it to JSON str"""
    try:
        xml = xmltodict.parse(str(xmlconfig))
        return json.dumps(xml, indent=2)
    except Exception as e:
        print(f"Issue converting XML to JSON, {e}")


def get_config(task, json_backup=False, xml_backup=False):
    """Use the get_config operation to retrieve the full xml config file from our device.
    If 'json_backup' set to True, the xml will be converted to JSON and backedup as well.
    """
    response = task.run(task=netconf_get_config)
    xmlconfig = response.result

    # Path to save output: This path will be auto-created for your below>
    path = f"Backups/{task.host.platform}"

    if json_backup == False and xml_backup == False:
        sys.exit("JSON and XML are both set to False. Nothing to backup.")

    # Generate Directories:
    create_folder(path)

    # Generate Time.
    x = datetime.datetime.now()
    today = x.date()

    # If the 'True' Bool val is passed into the xml_config task function,
    # convert xml to json as well and backup.
    if json_backup == True:
        json_config = xml2json(xmlconfig)

        write_file(
            task,
            filename=f"{path}/{task.host.name}_{today}_JSON.txt",
            content=json_config,
        )
    if xml_backup == True:
        write_file(
            task, filename=f"{path}/{task.host.name}_{today}_XML.txt", content=xmlconfig
        )


def main():

    netconf_devices.run(task=get_config, json_backup=True, xml_backup=True)


if __name__ == "__main__":
    main()
