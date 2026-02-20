from locust import HttpUser, task, between

class DaisoUser(HttpUser):
    wait_time = between(1, 3) # 사용자가 1~3초 간격으로 행동함

    @task
    def search_item(self):
        # 실제 검색 API 경로로 테스트
        self.client.get("/api/search?q=물티슈")

    @task
    def view_map(self):
        self.client.get("/maps/map_b1.jpg")