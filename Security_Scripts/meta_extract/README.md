# meta_extract.py
Extracts metadata from files (images, documents, etc.) using exiftool.

## Usage
python3 meta_extract.py -f file1.jpg file2.pdf -o metadata_results.json

## Arguments:

-f, --files: One or more file paths to extract metadata from (required)

-o, --output: Output JSON file path (default: metadata_results.json)


## Example Output (metadata_results.json)
```json
  [
  {
    "file": "file1.jpg",
    "metadata": {
      "File Name": "file1.jpg",
      "File Type": "JPEG",
      "MIME Type": "image/jpeg",
      "Date/Time Original": "2022:08:10 14:32:12",
      "GPS Latitude": "32 deg 20' 5.12\" N",
      "GPS Longitude": "95 deg 18' 10.24\" W"
    }
  },
  {
    "file": "file2.pdf",
    "metadata": {
      "File Name": "file2.pdf",
      "File Type": "PDF",
      "Producer": "Microsoft Word",
      "Author": "Jane Doe"
    }
  }
]
```
## Security Context
Metadata may reveal sensitive information such as GPS coordinates, author names, creation tools, and timestamps. Always review file metadata before sharing documents or media externally.

## Notes
Requires exiftool to be installed and available in the system path.

Can handle images, PDFs, Word docs, and other file formats supported by exiftool.

Files that cannot be parsed will include an error message in the output.

## License
MIT License

