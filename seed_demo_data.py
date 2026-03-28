import requests
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000/api"

def print_step(msg):
    print(f"\n[+] {msg}")

def login(email, password):
    res = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if res.status_code == 200:
        return res.json()['token']
    print(f"Login failed for {email}: {res.text}")
    return None

def register(role, data):
    res = requests.post(f"{BASE_URL}/auth/register", json={"role": role, **data})
    return res

def seed():
    print_step("Seeding Demo Data for Placement Portal...")
    
    # 1. Register Companies
    companies = [
        {"email": "hr@techcorp.com", "password": "pass123", "company_name": "TechCorp Solutions", "industry": "Software", "description": "Leading tech company"},
        {"email": "hr@finova.com", "password": "pass123", "company_name": "Finova Analytics", "industry": "Finance", "description": "Fintech and Analytics"},
        {"email": "hr@greenleaf.com", "password": "pass123", "company_name": "GreenLeaf Energy", "industry": "Cleantech", "description": "Sustainable energy solutions"}
    ]
    for c in companies: register("company", c)
    print("Registered 3 Companies.")

    # 2. Register Students
    students = [
        {"email": "arun@student.edu", "password": "pass123", "name": "Arun Kumar", "roll_number": "CS20B001", "branch": "CSE", "cgpa": 8.5},
        {"email": "meera@student.edu", "password": "pass123", "name": "Meera Patel", "roll_number": "CS20B002", "branch": "CSE", "cgpa": 8.8},
        {"email": "vikram@student.edu", "password": "pass123", "name": "Vikram Singh", "roll_number": "ME20B001", "branch": "Mech", "cgpa": 7.2},
        {"email": "priya.s@student.edu", "password": "pass123", "name": "Priya Sundaram", "roll_number": "EC20B001", "branch": "ECE", "cgpa": 9.1},
        {"email": "deepak@student.edu", "password": "pass123", "name": "Deepak Raj", "roll_number": "CE20B001", "branch": "Civil", "cgpa": 6.8}
    ]
    for s in students: register("student", s)
    print("Registered 5 Students.")

    # 3. Admin: Approve Companies
    admin_token = login("admin@placement.com", "admin123")
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    
    companies_list = requests.get(f"{BASE_URL}/admin/companies", headers=headers_admin).json()
    for c in companies_list.get('companies', []):
        requests.put(f"{BASE_URL}/admin/companies/{c['id']}/status", json={"status": "Approved"}, headers=headers_admin)
    print("Admin approved all companies.")

    # 4. Companies: Post Jobs
    techcorp_token = login("hr@techcorp.com", "pass123")
    finova_token = login("hr@finova.com", "pass123")
    greenleaf_token = login("hr@greenleaf.com", "pass123")

    jobs = [
        (techcorp_token, {"title": "Software Engineer", "description": "Full-stack developer role.", "salary_min": 800000, "salary_max": 1200000, "min_cgpa": 8.0, "eligibility_branch": "CSE"}),
        (finova_token, {"title": "Data Science Intern", "description": "Analytics team intern.", "salary_min": 400000, "salary_max": 600000, "min_cgpa": 8.5, "eligibility_branch": "Any"}),
        (finova_token, {"title": "Business Analyst", "description": "Bridging business and tech.", "salary_min": 1000000, "salary_max": 1500000, "min_cgpa": 7.5, "eligibility_branch": "Any"}),
        (greenleaf_token, {"title": "Sustainability Engineer", "description": "Renewable energy project management.", "salary_min": 700000, "salary_max": 900000, "min_cgpa": 7.0, "eligibility_branch": "Mech"})
    ]
    
    for token, job in jobs:
        requests.post(f"{BASE_URL}/company/jobs", json=job, headers={"Authorization": f"Bearer {token}"})
    print("Companies posted 4 jobs.")

    # 5. Admin: Approve Jobs
    drives_list = requests.get(f"{BASE_URL}/admin/drives", headers=headers_admin).json()
    for d in drives_list.get('drives', []):
        requests.put(f"{BASE_URL}/admin/drives/{d['id']}/status", json={"status": "Approved"}, headers=headers_admin)
    print("Admin approved all job drives.")

    # 6. Students: Apply for Jobs
    meera_token = login("meera@student.edu", "pass123")
    vikram_token = login("vikram@student.edu", "pass123")
    priya_token = login("priya.s@student.edu", "pass123")

    # Fetch approved jobs
    jobs_available = requests.get(f"{BASE_URL}/student/jobs", headers={"Authorization": f"Bearer {meera_token}"}).json()
    
    # Students applying to eligible jobs
    for job in jobs_available.get('jobs', []):
        if job['title'] == "Software Engineer":
            requests.post(f"{BASE_URL}/student/jobs/{job['id']}/apply", headers={"Authorization": f"Bearer {meera_token}"})
            requests.post(f"{BASE_URL}/student/jobs/{job['id']}/apply", headers={"Authorization": f"Bearer {priya_token}"})
        elif job['title'] == "Data Science Intern":
            requests.post(f"{BASE_URL}/student/jobs/{job['id']}/apply", headers={"Authorization": f"Bearer {meera_token}"})
            requests.post(f"{BASE_URL}/student/jobs/{job['id']}/apply", headers={"Authorization": f"Bearer {priya_token}"})
        elif job['title'] == "Business Analyst":
            requests.post(f"{BASE_URL}/student/jobs/{job['id']}/apply", headers={"Authorization": f"Bearer {vikram_token}"})
        elif job['title'] == "Sustainability Engineer":
            requests.post(f"{BASE_URL}/student/jobs/{job['id']}/apply", headers={"Authorization": f"Bearer {vikram_token}"})

    print("Students applied to jobs.")
    
    print_step("Demo Data Seeded Successfully!")
    print("You can now log in and record your video!")

if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print("Error: Make sure the Flask server is running on http://127.0.0.1:5000 before running this script.")
        print(e)
