### webapi
Ideally, a web scraper for tracking elements robust to website changes.
Currently `backend` parses the DOM and uses simple heuristics on class/id/hierarchy to pick the most likely target.
`chrome-ext` is a chrome extension that allows you to pick web page elements to create the website's api.

More interesting directions/cues:
- What kind of value are trying to track
- What is the typical layout of websites created with framework X? 
- How is content presented/highlighted through common design guidelines
- What does the web platform actually do? level of interaction?
