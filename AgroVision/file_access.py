import earthaccess

def download_data(short_name, bounding_box, date, download_path):
    auth = earthaccess.login() 

    results = earthaccess.search_data(
        short_name=short_name,
        temporal=(date, date),
        bounding_box=bounding_box
    )

    if results:
        print(f"Foind {len(results)} files")
        files = earthaccess.download(results[0], download_path)
        print("Downloaded")
        return files



    new_start_date = "2024-01-01"  
    new_end_date = "2024-09-30" 


    results = earthaccess.search_data(
        short_name=short_name,
        temporal=(new_start_date, new_end_date),
        bounding_box=bounding_box
    )


    if results:
        print(f"Found {len(results)} files")
        files = earthaccess.download(results, download_path)
        print("Downloaded")
        return files


    print("Couldn't find data")
    return None
