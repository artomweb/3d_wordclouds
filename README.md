# 3d_wordclouds
 
# NO LONGER WORKS WITH NEW VERSIONS OF PYTHON :(( latest is 2.83

Description
-----
Create 3D wordclouds representing your Spotify playlists. This is just a proof of concept in generating procedural art. 

![example1](./example1.png)
![example2](./example2.png)

Usage
----

Clone the repo to download the two files. The 'generate_freq.py' file is used to generate both a csv file of song lyrics and a text file containing the word frequencies. 'WordPile.py' should be run with blender to generate the image. 

Install prerequisites:
---
Install [blender](https://www.blender.org/)

Pip can be used to install the dependencies:

````
pip install -r REQUIREMENTS.txt
````

Running the code:
---

1. Edit both the 'client_id' and 'client_secret' in 'generate_req.py' to your [spotify dev](https://developer.spotify.com/dashboard/) credentials.

2. Run 'generate_req.py' with the playlists URI as an argument:

````
python generate_freq.py <URI>
````
  
3. For the program to run blender, `blender` needs to be accessible from the command line. Alternatively if this fails run WordPile.py with blender, with the URI as an argument after '--'

````
<path_to_blender> -b --python WordPile.py -- <URI>
````


  
Adjustable parameters in 'config.txt'
-----

 - 'col_pal' an array of hex values creating a color pallet
   - These can be generated easily at [coolors.co](https://coolors.co/palettes/trending) exporting a pallet as code and copying the array
 - 'random_color' if false then the color pallet is used, if true random colors are generated
 - 'num_words' the number of words to be simulated
 - 'mi_max' the spread from the centre of the image of the largest words
 - 'li_max' the spread from the centre fo the image of the smallest words
 - 'current_height' the starting height of the words
 - 'vertical_offset' the amount that each word is raised above the last
 - 'extrusion' the height of each word
 - 's_f' a scale factor to adjust the size of the words
 - 'add_exclude' an array of additional words to exclude from the wordcloud
