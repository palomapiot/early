"""
    Copyright 2020-2021 Paloma Piot Pérez-Abadín
	
	This file is part of early.
    early is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    early is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with early.  If not, see <https://www.gnu.org/licenses/>.
"""

import time
from locust import HttpUser, TaskSet, task, tag, constant

class Profiles(HttpUser):
    wait_time = constant(2)
    @tag('profiles')
    @task()
    def get_profiles(self):
        self.client.get("/api/profiles", headers={'Authorization':'Token ' + '8ca72bac81117043cef2aafa3b0ea34e02369971'})

    @tag('profiles')
    @task()
    def get_profile_detail(self):
        for item_id in range(3070, 3080):
            self.client.get("/api/profiles/" + str(item_id), headers={'Authorization':'Token ' + '8ca72bac81117043cef2aafa3b0ea34e02369971'})

    def on_start(self):
        self.client.post("/api/login", json={"username":"test", "password":"loadtestlocust1"})
