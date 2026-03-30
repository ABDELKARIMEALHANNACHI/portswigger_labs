# basic-ssrf-backend-system
# basic-ssrf-backend-system

## 🎯 Objective

Exploit an SSRF vulnerability to:
1. Discover an internal backend system in the range:
   192.168.0.X
2. Identify the host running an admin service on port 8080
3. Access the admin interface
4. Delete the user `carlos`

---

## 🧠 What is different from Lab 1

In the previous lab, the target was:
- localhost (same machine)

In this lab:
- the target is another internal system
- located inside the private network (192.168.0.X)

👉 This introduces **internal network enumeration via SSRF**

---

## ⚙️ Attack Model

Attacker → Web App → Internal Network (192.168.0.X)


The vulnerable server becomes a **proxy to scan internal infrastructure**.

---
