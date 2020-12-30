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
