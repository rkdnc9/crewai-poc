  @echo off
  echo Creating conda environment...
  conda env create -f environment.yml

  echo Activating environment...
  call conda activate crewai-poc

  echo Installing dependencies...
  pip install -r requirements.txt

  echo Creating sample data...
  python create_sample_ifc.py

  echo Setup complete!
  echo.
  echo To use the environment:
  echo   conda activate crewai-poc
  echo.
  echo To run the demo:
  echo   python main.py --ifc test_data/sample_wall.ifc