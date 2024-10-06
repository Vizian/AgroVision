import h5py
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os

def visualize_smap_data(file_path, bounding_box, selected_data, data_label, coordinates):
    """Visualize SMAP data for a Telegram bot."""

    # Open the file and read the data
    with h5py.File(file_path, 'r') as f:
        latitudes = f['cell_lat'][:]
        longitudes = f['cell_lon'][:]
        data_type = f[selected_data][:]

    # Convert data to float32 format for proper operation
    data_type = data_type.astype(np.float32)

    # Check if data dimensions match latitude/longitude dimensions
    if latitudes.shape != data_type.shape:
        raise ValueError("Data dimensions do not match; please check the input data.")

    # Function to mask water bodies and normalize data
    def smooth_classification(data):
        water_mask = (data == -9999)
        norm_data = np.clip(data, 0, 0.5) / 0.5  # Normalize data to range 0-0.5
        norm_data[water_mask] = np.nan  # Mask water bodies
        return norm_data

    classified_data = smooth_classification(data_type)

    # Function for global visualization
    def visualize_global_map(classified_data, latitudes, longitudes, data_label, coords):
        fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())  # Visualize the whole world

        cmap = plt.get_cmap('viridis_r')  # Use the viridis color map
        img = ax.imshow(classified_data, cmap=cmap, extent=[longitudes.min(), longitudes.max(), latitudes.min(), latitudes.max()],
                         origin='upper', interpolation='none', alpha=0.7)

        # Add a red polygon around the coordinates
        lat, lon = coords
        delta = 1  # Define the offset size for the square (1 degree in each direction)
        min_lon, min_lat = lon - delta, lat - delta
        max_lon, max_lat = lon + delta, lat + delta
        
        # Draw the polygon
        ax.plot([min_lon, max_lon, max_lon, min_lon, min_lon], [min_lat, min_lat, max_lat, max_lat, min_lat], color='red', linewidth=2)

        cbar = plt.colorbar(img, ax=ax, shrink=0.8)
        cbar.set_label("Normalized " + data_label)

        ax.set_title("Global View with Red Box Around Coordinates: " + data_label, fontsize=14)

        global_output_image_path = os.path.join(os.path.expanduser("~"), "Desktop", "global_smap_visualization_with_red_box.png")
        plt.savefig(global_output_image_path, dpi=300)
        plt.close()

        return global_output_image_path

    # Function for zoomed map visualization
    def visualize_zoomed_map(bounding_box, classified_data, latitudes, longitudes, data_label, coords):
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})

        # Set zoom to the selected coordinates
        min_lon, min_lat, max_lon, max_lat = bounding_box
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

        cmap = plt.get_cmap('viridis_r')
        img = ax.imshow(classified_data, cmap=cmap, extent=[longitudes.min(), longitudes.max(), latitudes.min(), latitudes.max()],
                        origin='upper', interpolation='none', alpha=0.7)

        # Add a red square around the provided coordinates
        lat, lon = coords
        delta = 1  # Define the offset size for the square (1 degree in each direction)
        ax.plot([lon - delta, lon + delta], [lat - delta, lat - delta], color='red', linewidth=2)
        ax.plot([lon - delta, lon + delta], [lat + delta, lat + delta], color='red', linewidth=2)
        ax.plot([lon - delta, lon - delta], [lat - delta, lat + delta], color='red', linewidth=2)
        ax.plot([lon + delta, lon + delta], [lat - delta, lat + delta], color='red', linewidth=2)

        cbar = plt.colorbar(img, ax=ax, shrink=0.8)
        cbar.set_label("Normalized " + data_label)

        ax.set_title("Zoomed View with Red Box Around Coordinates: " + data_label, fontsize=14)

        zoomed_output_image_path = os.path.join(os.path.expanduser("~"), "Desktop", "zoomed_smap_visualization_with_red_box.png")
        plt.savefig(zoomed_output_image_path, dpi=300)
        plt.close()

        return zoomed_output_image_path

    # Visualize the global map
    global_output_image_path = visualize_global_map(classified_data, latitudes, longitudes, data_label, coordinates)
    # Visualize the zoomed map based on bounding_box
    zoomed_output_image_path = visualize_zoomed_map(bounding_box, classified_data, latitudes, longitudes, data_label, coordinates)

    # Output paths of saved images
    print(f"Global Image saved at: {global_output_image_path}")
    print(f"Zoomed Image saved at: {zoomed_output_image_path}")

    # Return the paths of saved images
    return global_output_image_path, zoomed_output_image_path
