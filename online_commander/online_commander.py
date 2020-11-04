from BaseHTTPServer import BaseHTTPRequestHandler
import bs4
import SocketServer
import json

from os import path as os_path
from urllib import unquote


class Configuration(object):
    def __init__(self):
        with open("configuration.json", "rb") as configuration_file:
            configuration = json.loads(configuration_file.read())
            self.port = configuration["port"]
            self.command_types = configuration["command_types"]


class OnlineCommander(object):
    def __init__(self, configuration):
        self.__port = configuration.port
        self.__command_types = configuration.command_types
        current_directory = os_path.dirname(os_path.abspath(__file__))
        self.__resource_folder = "{}/resources/".format(current_directory)

    class OnlineCommandRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            current_directory = os_path.dirname(os_path.abspath(__file__))
            resouce_directory = "{}/resources/".format(current_directory)
            if self.path == "/":
                self.send_response(200)
                self.end_headers()
                with open("{}/home.html".format(resouce_directory), "rb") as home_html:
                    self.wfile.write(home_html.read())
            elif self.path.find('.css') != -1:
                self.send_response(200)
                self.end_headers()
                with open("{}/home.css".format(resouce_directory), "rb") as home_html:
                    self.wfile.write(home_html.read())
            elif self.path.find("new_shell_command") != -1:
                commands = unquote(self.path.split("shell_script=")[1])\
                    .replace("\r", "").lower().split("\n")
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()

    def start_monitoring(self):
        try:
            httpd = SocketServer.TCPServer(("", self.__port), OnlineCommander.OnlineCommandRequestHandler)
            print "serving at port", self.__port
        except Exception:
            httpd = SocketServer.TCPServer(("", self.__port + 1), OnlineCommander.OnlineCommandRequestHandler)
            print "serving at port", self.__port + 1
        self.__embed_command_types_in_html(self.__command_types)

        httpd.serve_forever()

    def __embed_command_types_in_html(self, command_types):
        with open("{}/home.html".format(self.__resource_folder), "rb") as html_to_embed_in:
            html_structure = bs4.BeautifulSoup(html_to_embed_in.read(), features="lxml")

        command_type_dropdown_item = html_structure.find("select", {"name": "type"})
        for current_command_types in command_type_dropdown_item.findChildren():
            if not current_command_types["type"] in command_types:
                current_command_types.extract()

        for command_type in command_types:
            if not command_type_dropdown_item.findChildren("option", {"type": command_type}):
                html_item = self.__create_form_item(html_structure, command_type)
                command_type_dropdown_item.append(html_item)

        with open("{}/home.html".format(self.__resource_folder), "wb") as html_to_embed_in:
            html_to_embed_in.write(html_structure.prettify("utf-8"))

    def __create_form_item(self, html_structure, command_type):
        item = html_structure.new_tag("option", type=command_type)
        item.insert(0, command_type.capitalize())

        return item

configuration = Configuration()
onliner = OnlineCommander(configuration)
onliner.start_monitoring()