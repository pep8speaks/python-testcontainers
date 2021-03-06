#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready

IMAGES = {
    "firefox": "selenium/standalone-firefox-debug",
    "chrome": "selenium/standalone-chrome-debug"
}


def get_image_name(capabilities):
    return IMAGES[capabilities['browserName']]


class BrowserWebDriverContainer(DockerContainer):
    def __init__(self, capabilities, version="latest"):
        self.capabilities = capabilities
        self.image = get_image_name(capabilities)
        self.host_port = 4444
        self.host_vnc_port = 5900
        super(BrowserWebDriverContainer, self).__init__(image=self.image, version=version)

    def _configure(self):
        self.add_env("no_proxy", "localhost")
        self.add_env("HUB_ENV_no_proxy", "localhost")
        self.expose_port(4444, self.host_port)
        self.expose_port(5900, self.host_vnc_port)

    @wait_container_is_ready()
    def _connect(self):
        return webdriver.Remote(
            command_executor=(self.get_connection_url()),
            desired_capabilities=self.capabilities)

    def get_driver(self) -> WebDriver:
        return self._connect()

    def get_connection_url(self) -> str:
        ip = self.get_container_host_ip()
        port = self.get_exposed_port(self.host_port)
        return 'http://{}:{}/wd/hub'.format(ip, port)
