# NNUnet Repo

Este repositorio incluye los scripts de ejecución y análisis de resultados del modelo nnUNet en los datos de tumores del dataset BRATS y el repositorio clínico local.

Los scripts hacen uso del modelo nnUNet-v2 que debe ser instalado siguiendo las instrucciones detalladas en: https://github.com/MIC-DKFZ/nnUNet


Organizacion de estructura
------------


    
    ├── README.md          <- Readme del proyecto
    ├── data
    │   ├── interim        <- Data Preprocesada y transformada
    │   └── raw            <- Datos originales sin modificaciones
    │
    ├── models             <- Modelos utilizados para predicciones
    │
    ├── notebooks          <- Jupyter notebooks y .pys
    │
    └── docs               <- Documentacion adiciconal