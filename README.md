
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

This repository contains the backend code that enables and allows the platform's users to visualize, data processing and building the results on the front side.

This code will : 
* Receive the 3D Objects
* Visualize and fix it
* Voxelize it 
* Generate the Heightmap into CSV Files  
* ...

# How to deploy 
> :warning: This requires a PostgreSQL database setup :warning:

> The */**sql*** folder already contains the sql scripts to execute for creating and filling the database's tables.

* Clone the repository 
`
git clone https://github.com/datagora-erasme/maquette_back.git
`
* Switching to the branche **develop**
`
git checkout develop
`
* Change variables on the .env file (taking the .env.EXAMPLE as an example)

* Start the API 
`
python run.py
`
