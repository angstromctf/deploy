# Deploy

Deploy scripts for AngstromCTF problems. Allows users to check problem 
formatting, export to JSON for DjangoCTF, and deploy them to the problem
server directories.

## Search

Search allows the user to analyse a directory structure for problems. The 
syntax is as follows:

```
python3 deploy search /path/to/problems/
```

## Export

Converts problem to a JSON file that can easily be imported by Django.
 
```
python3 deploy export /path/to/problems/ output_file.json
```

Optionally, include a hardcoded link for static files reference in the text:

```
python3 deploy export /path/to/problems/ output_file.json --url https://angstromctf.com
```
