# Fix — AngularJS Expression Injection

## Fix
1. Use `ng-non-bindable` on elements containing user-reflected data.
2. Do not use AngularJS 1.x in new projects — use Angular 2+ with strict mode.
3. Never reflect user input inside ng-app scope without ng-non-bindable.
