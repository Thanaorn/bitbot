from locust import HttpUser , task ,between , TaskSet , User

# class http_set(HttpUser):
#     @task
#     def get_route(self):
#         self.client.get(self.client.get("/"))
        
#     @task
#     def post_route(self):
#         self.client.post(url="/test", data={"name":"test"})
# class test_api(HttpUser): #task ตัวกำหนดงาน
#     wait_time = between(1,5) # รอ 1-5 วิ
#     @task
#     def test_t1(self):
#         self.client.get("/")
#         self.client.get("/getJson")
        
#     @task()
#     def test_t2(self):
#         print('T2 current execute')

class WebsiteUser(HttpUser):
    @task(6)
    def test_link(self):
        self.client.get("/link?name='test_name'")
    
    @task(1)
    def test_set_queue(self):
        self.client.post("/testpostallqueue", json={"cid": "test_cid", "exercise": 1, "sleep": 1, "work": 1, "feeling": 1, "income": 10, "expense": 10, "daily": "test"})

    @task(2)
    def test_get_queue(self):
        self.client.post("/confirmallqueue", json={"cid": "test_cid", "status": "ถูกต้อง"})
        
    @task(3)
    def test_edit_data(self):
        self.client.post("/editdata", json={"cid": "test_cid", "index": 9, "exercise": 1, "sleep": 1, "work": 1, "feeling": 1, "income": 10, "expense": 10, "daily": "test"})
    
    @task(4)
    def test_confirm_data(self):
        self.client.post("/confirmedit", json={"cid": "test_cid", "status": "ถูกต้อง"})

    @task(5)
    def test_export_data(self): 
        self.client.post("/exportdata", json={"cid": "test_cid", "name": "test_name"})

        
    # locust -f .\locustfile.py
    
    #peak load รับ user สูงสุดตาม peak
    #ramp up เพิ่มไปเรื่อยๆทีละ ที่กำหนด เข้า (วิละกี่คน)