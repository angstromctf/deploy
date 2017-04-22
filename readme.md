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

# Deploy

To export static problem files listed in the `file` field of the `problem.yml`
field, run the following command:
 
```
python3 deploy static /path/to/problems/ /static/file/dir/
```

Static files will be put in the following structure:

```
/static/file/dir/
  <category>/
    <problem>/
      <files>
```
