import h5py
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os

def visualize_smap_data(file_path, bounding_box, selected_data, data_label, coordinates):
    """Visualize SMAP data for a Telegram bot."""

    # Открытие файла и чтение данных
    with h5py.File(file_path, 'r') as f:
        latitudes = f['cell_lat'][:]
        longitudes = f['cell_lon'][:]
        data_type = f[selected_data][:]

    # Преобразование данных в формат float32 для корректной работы
    data_type = data_type.astype(np.float32)

    # Проверка соответствия размеров данных и широты/долготы
    if latitudes.shape != data_type.shape:
        raise ValueError("Размеры данных не совпадают, проверьте входные данные.")

    # Функция для маскирования водных объектов и нормализации данных
    def smooth_classification(data):
        water_mask = (data == -9999)
        norm_data = np.clip(data, 0, 0.5) / 0.5  # Нормализация данных в диапазоне 0-0.5
        norm_data[water_mask] = np.nan  # Маскирование водных объектов
        return norm_data

    classified_data = smooth_classification(data_type)

    # Функция для глобальной визуализации
    def visualize_global_map(classified_data, latitudes, longitudes, data_label, coords):
        fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())  # Визуализация всего мира

        cmap = plt.get_cmap('viridis_r')  # Используем цветовую палитру viridis
        img = ax.imshow(classified_data, cmap=cmap, extent=[longitudes.min(), longitudes.max(), latitudes.min(), latitudes.max()],
                         origin='upper', interpolation='none', alpha=0.7)

        # Добавляем красный полигон вокруг координат
        lat, lon = coords
        delta = 1  # Определяем размер смещения для квадрата (1 градус в каждую сторону)
        min_lon, min_lat = lon - delta, lat - delta
        max_lon, max_lat = lon + delta, lat + delta
        
        # Рисуем полигон
        ax.plot([min_lon, max_lon, max_lon, min_lon, min_lon], [min_lat, min_lat, max_lat, max_lat, min_lat], color='red', linewidth=2)

        cbar = plt.colorbar(img, ax=ax, shrink=0.8)
        cbar.set_label("Normalized " + data_label)

        ax.set_title("Global View with Red Box Around Coordinates: " + data_label, fontsize=14)

        global_output_image_path = os.path.join(os.path.expanduser("~"), "Desktop", "global_smap_visualization_with_red_box.png")
        plt.savefig(global_output_image_path, dpi=300)
        plt.close()

        return global_output_image_path

    # Функция для визуализации зумированной карты
    def visualize_zoomed_map(bounding_box, classified_data, latitudes, longitudes, data_label, coords):
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})

        # Устанавливаем зум на выбранные координаты
        min_lon, min_lat, max_lon, max_lat = bounding_box
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

        cmap = plt.get_cmap('viridis_r')
        img = ax.imshow(classified_data, cmap=cmap, extent=[longitudes.min(), longitudes.max(), latitudes.min(), latitudes.max()],
                        origin='upper', interpolation='none', alpha=0.7)

        # Добавляем красный квадрат вокруг введённых координат
        lat, lon = coords
        delta = 1  # Определяем размер смещения для квадрата (1 градус в каждую сторону)
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

    # Визуализация глобальной карты
    global_output_image_path = visualize_global_map(classified_data, latitudes, longitudes, data_label, coordinates)
    # Визуализация зумированной карты по bounding_box
    zoomed_output_image_path = visualize_zoomed_map(bounding_box, classified_data, latitudes, longitudes, data_label, coordinates)

    # Вывод путей сохраненных изображений
    print(f"Global Image saved at: {global_output_image_path}")
    print(f"Zoomed Image saved at: {zoomed_output_image_path}")

    # Возвращаем пути сохраненных изображений
    return global_output_image_path, zoomed_output_image_path
