### Deduplication of bookmarks

- Export bookmarks from Brave / Chrome in .html format (Netscape bookmarks format which is not actually HTML)
- Import bookmarks into Firefox
- Export bookmarks from Firefox in .json format
- Run notebook `json_bookmarks_dedup.ipynb` to read the bookmarks from the json file dedup them and write them back to `.html` format
- Import resulting .html file into Brave (it will be imported inside a separate folder called `Bookmarks` at the top level)
