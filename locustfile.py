from locust import HttpUser, task, between


class WarehouseUser(HttpUser):
    wait_time = between(1, 2)

    @task(5)
    def list_products(self):
        self.client.get("/api/v1/products/?skip=0&limit=10")

    @task(2)
    def readiness(self):
        self.client.get("/ready")

    @task(1)
    def health(self):
        self.client.get("/health")
