<p align="center">
    <img src="https://upload.wikimedia.org/wikipedia/fr/thumb/b/b8/Logo_M%C3%A9tropole_Lyon_-_2022.svg/1200px-Logo_M%C3%A9tropole_Lyon_-_2022.svg.png" width="250">
    <img src="https://upload.wikimedia.org/wikipedia/fr/7/77/Logo_Universit%C3%A9_de_Lyon.png" width="250">
    <img src="https://images.exo-dev.fr/Logo_DatAgora.png" width="100">
    <img src="https://images.exo-dev.fr/white_creation_exo_dev.png" width="150">
</p>

# About This Project
The augmented model project was born during an experiment as part of the MAM project: **Mediation and Augmented Modeling**. Various workshops were organized in collaboration with *LabEx IMU*, *ERASME Urban Lab* and the *École Urbaine de Lyon*.

The project consists of a model of a city district made from **Lego** and created from a web platform. This model is made to be installed in public places and used in the context of mediation or neighborhood council.

# About This Repository 
> :warning: This version is using the tiles hosted on Exo-Dev's server :warning:

This repository contains the backend code that enables and allows the platform's users to visualize, data processing and building the results on the front side.

This code will : 
* Receive the Bbox of the selected zone
* Get the meshes from the WFS stream, merge it and clip it.
* Voxelize the meshes 
* ...

## Technical Information

### Available Layer Services 

* WFS 1.0.0, 1.1.0 & 2.0.0
* WMS 1.1.1, 1.3.0
* WMTS 1.0.0

### Available WFS/WMS Output Results 

* CSV
* GML
* GeoJson
* KML 
* GeoRSS
* OpenLayer

### Used EPSG Geodetic Parameters 

* Bbox : **EPSG:2154**
* GeoServer Default Projection : **EPSG:2154**

# How to deploy 
> :warning: This requires a PostgreSQL database setup :warning:

> The */**sql*** folder already contains the sql scripts to execute for creating and filling the database's tables.

## Set Up a PostgreSQL Database 

* Setup a PostgreSQL Server depending on the OS you're using.
* Execute the sql scripts available at the */**sql*** folder ( *create-tables.sql* & *insert-tables.sql* )

```bash
docker exec -it maquette_augmentee_postgres psql -U postgres -d postgres -f /sql/create-tables.sql
docker exec -it maquette_augmentee_postgres psql -U postgres -d postgres -f /sql/insert-datas.sql
```
```

## Run the app

* Clone the repository 
`
git clone https://github.com/datagora-erasme/maquette_back.git
`

* Change variables on the .env file (taking the *.env.EXAMPLE* as an example)

* Install Python PIP requirements :

```
pip install -r requirements.txt
```

* Start the API 
`
python run.py
`
# Use-case Specification 

## Voxelization :

We tried to make and render the voxelization fully in python, using the Pyvista python module but the received data we are using wasn't that clean and easy to handle!

So, we prefered using another oriented/specific and straight-forward tool for voxelization called **binvox** that reads a 3D model file, rasterizes it into a binary 3D voxel grid, and writes the resulting voxel file.

# Example 
In this example we will use a part of Lyon 3 (around *tour Part-Dieu*) and the Bbox [**843845.1134647338, 6519404.7046337575, 844253.0381356651, 6519813.770257493**] using the **/api/dataprocess** endpoint.

## Rendering

![Rendering](https://i.imgur.com/mE7CjVx.png)

## Voxelization

![Voxelization](https://i.imgur.com/WvmBza7.png)