import asyncio
import earthaccess
import os
from datetime import datetime  
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from file_access import download_data
from visualisation import visualize_smap_data 

API_TOKEN = os.getenv('API_TOKEN')
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage, bot=bot)

# Define states for finite state machine (FSM)
class FormStates(StatesGroup):
    waiting_for_coordinates = State()
    waiting_for_data_type = State() 
    waiting_for_date = State()

@dp.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handler for start command.""" 
    await message.answer("Welcome! Let's begin the authentication process, please wait..")

    # Authentication using earthaccess
    try:
        auth = earthaccess.login(strategy="environment")  # Use environment variable strategy
        await message.answer("Successfully logged in using credentials.")
        
        # Move to the next step after successful authentication
        await state.set_state(FormStates.waiting_for_coordinates)
        await message.answer("Please send your coordinates in the format 'longitude, latitude'.\nFor example: 29.631, 30.968")
    except Exception as e:
        await message.answer(f"Failed to log in. Please check your credentials. Error: {str(e)}")

@dp.message(FormStates.waiting_for_coordinates)
async def handle_coordinates(message: types.Message, state: FSMContext):
    """Handler for user coordinates."""    
    coords = message.text.strip()
    
    try:
        latitude, longitude = map(float, coords.split(','))
        await state.update_data(coordinates=(longitude, latitude))
        
        # Display user-friendly data type options
        await message.answer("Please select the data type:\n"
                             "1. Soil moisture from surface\n"
                             "2. Soil moisture in rootzone\n"
                             "3. Surface temperature\n"
                             "4. Soil temperature")
        
        await state.set_state(FormStates.waiting_for_data_type)
    except ValueError:
        await message.answer("Invalid format. Please send coordinates in the format 'longitude, latitude'.\nFor example: 29.631, 30.968")

@dp.message(FormStates.waiting_for_data_type)
async def handle_data_type(message: types.Message, state: FSMContext):
    """Handler for user data type selection."""    
    # Mapping user-friendly names to their corresponding data type keys
    data_type_mapping = {
        "1": ("Analysis_Data/sm_surface_analysis", "Soil moisture from surface"),
        "2": ("Analysis_Data/sm_rootzone_analysis", "Soil moisture in rootzone"),
        "3": ("Analysis_Data/surface_temp_analysis", "Surface temperature"),
        "4": ("Analysis_Data/soil_temp_layer1_analysis", "Soil temperature")
    }

    selected_type = message.text.strip()
    
    if selected_type in data_type_mapping:
        await state.update_data(data_type=data_type_mapping[selected_type][0]) 
        await message.answer(f"You selected: {data_type_mapping[selected_type][1]}\n"
                             "Enter the date in the format YYYY-MM-DD.\nFor example: 2022-02-05")
        await state.set_state(FormStates.waiting_for_date)
    else:
        await message.answer("Invalid selection. Please choose a number from 1 to 4.")

@dp.message(FormStates.waiting_for_date)
async def handle_date(message: types.Message, state: FSMContext):
    """Handler for date."""    
    selected_date = message.text.strip()

    # Define date range
    min_date = datetime(2015, 5, 1)  # May 1, 2015
    max_date = datetime.now()  # Today's date

    try:
        # Parse the date from the user input
        user_date = datetime.strptime(selected_date, "%Y-%m-%d")

        # Validate the date
        if user_date < min_date:
            await message.answer(f"Please select a date after {min_date.date()}.")
            return
        elif user_date > max_date:
            await message.answer("Please select a date before today.")
            return
        
        await state.update_data(selected_date=selected_date)

        data = await state.get_data()
        longitude, latitude = data['coordinates']
        latitude = latitude + latitude * 0.35
        # Define bounding box around coordinates
        bounding_box = (longitude - 2, latitude - 2, longitude + 2, latitude + 2)

        # Get data type from state
        data_type = data['data_type']  # Get the selected data type

        # Short name for SMAP data
        short_name = "SPL4SMAU"

        # Download path for data
        download_path = "C:/Users/User/Desktop/dataNASA"

        # Download data
        downloaded_files = download_data(short_name, bounding_box, selected_date, download_path)
        
        # Check for downloaded files
        if not downloaded_files:
            await message.answer("No data found for the specified date.")
            await state.clear()
            return
        
        await message.answer("Data successfully downloaded, please wait...")

        output_image_paths = []
        file = downloaded_files[0] 

        # Visualize the data and check the result
        global_image_path, zoomed_image_path = visualize_smap_data(file, bounding_box, data_type, "SMAP Data", [latitude, longitude])  # Added coordinates
        if global_image_path is None or zoomed_image_path is None:
            await message.answer("Visualization failed. Please try again later.")
            await state.clear()  # Clear the state machine
            return
        
        output_image_paths.append(global_image_path)
        output_image_paths.append(zoomed_image_path)

        # Send the visualizations to the user
        for image_path in output_image_paths:
            # Check for file existence before sending
            if os.path.exists(image_path):
                await bot.send_photo(message.chat.id, FSInputFile(image_path))
            else:
                await message.answer(f"Error: File {image_path} not found.")
        
        await state.clear()  # Clear the state machine

    except ValueError:
        await message.answer("Invalid date format. Please enter the date in the format YYYY-MM-DD.")

# Main function to run the bot
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())
