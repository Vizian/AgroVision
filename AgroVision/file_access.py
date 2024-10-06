import earthaccess

def download_data(short_name, bounding_box, date, download_path):
    # Authenticate through NASA Earthdata without passing credentials
    auth = earthaccess.login()  # Use only login without arguments

    # Search for data with the specified date range
    results = earthaccess.search_data(
        short_name=short_name,
        temporal=(date, date),
        bounding_box=bounding_box
    )

    # Check if any data files were found
    if results:
        print(f"Found {len(results)} files. Downloading...")
        files = earthaccess.download(results[0], download_path)
        print("Data successfully downloaded.")
        return files

    # If no data is found, attempt to expand the search
    print("No data found for the specified date range. Trying to expand the range...")

    # Expand the date range
    new_start_date = "2024-01-01"  # Set a new start date (example)
    new_end_date = "2024-09-30"    # Set a new end date (example)

    # Repeat the search with the new date range
    results = earthaccess.search_data(
        short_name=short_name,
        temporal=(new_start_date, new_end_date),
        bounding_box=bounding_box
    )

    # Check if any data files were found with the new date range
    if results:
        print(f"Found {len(results)} files in the new date range. Downloading...")
        files = earthaccess.download(results, download_path)
        print("Data successfully downloaded.")
        return files

    # If no results are still found, inform the user
    print("No data found for the expanded date range.")
    return None  # Return None if files are not found
