
```
            /$$       /$$$$$$$$                                         /$$$$$$$                             /$$   
           /$$/      | $$_____/                                        | $$__  $$                           |  $$  
          /$$/       | $$       /$$   /$$  /$$$$$$                     | $$  \ $$  /$$$$$$  /$$    /$$       \  $$ 
         /$$/        | $$$$$   |  $$ /$$/ /$$__  $$       /$$$$$$      | $$  | $$ /$$__  $$|  $$  /$$/        \  $$
        |  $$        | $$__/    \  $$$$/ | $$  \ $$      |______/      | $$  | $$| $$$$$$$$ \  $$/$$/          /$$/
         \  $$       | $$        >$$  $$ | $$  | $$                    | $$  | $$| $$_____/  \  $$$/          /$$/ 
          \  $$      | $$$$$$$$ /$$/\  $$|  $$$$$$/                    | $$$$$$$/|  $$$$$$$   \  $/          /$$/  
           \__/      |________/|__/  \__/ \______/                     |_______/  \_______/    \_/          |__/   
```

# About this repository 
> :warning: This version is using the tiles hosted on Exo-Dev's server :warning:

This repository contains the backend code that enables and allows the platform's users to visualize, data processing and building the results on the front side.

This code will : 
* Receive the Bbox of the selected zone
* Get the meshes from the WFS stream, merge it and clip it.
* Voxelize the meshes 
* Generate the Heightmap into multiple CSV Files ( Coming...) 
* ...

# How to deploy 
> :warning: This requires a PostgreSQL database setup :warning:

> The */**sql*** folder already contains the sql scripts to execute for creating and filling the database's tables.

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

## Heightmap :

This one was kind of tricky ! using the old method used before in **Legonizer** wasn't possible, so started by generating a heatmap of the voxelized result we are having and than use that heatmap to calculate the relation between height/Eleveation and the heat... 

And that's how we bypassed and got the heightmap of each center-cell of a voxel (cube), which will give us the height of each *building* to generate the CSV.

# Example 
In this example we will use a part of Lyon 3 (around *tour Part-Dieu*) and the Bbox [**843845.1134647338, 6519404.7046337575, 844253.0381356651, 6519813.770257493**]

## Rendering

![Rendering](https://i.imgur.com/mE7CjVx.png)

## Voxelization

![Voxelization](https://i.imgur.com/WvmBza7.png)

## Heatmap (to get the heightmap)

![Heatmap](https://i.imgur.com/7ioPvas.png)